import math

import mysql.connector
from fastapi import Body, FastAPI, HTTPException, Query

import employee_queries
import file_operations


app = FastAPI(title="Employee Management API")

EMPLOYEE_FIELDS = {"name", "email", "department", "salary"}


def validate_employee_data(employee):
    """Check required fields and return a cleaned employee dictionary."""
    if set(employee.keys()) != EMPLOYEE_FIELDS:
        raise HTTPException(
            status_code=422,
            detail="Provide exactly these fields: name, email, department, salary.",
        )

    cleaned_employee = {}
    for field in ("name", "email", "department"):
        value = employee[field]
        if not isinstance(value, str) or not value.strip():
            raise HTTPException(
                status_code=422,
                detail=f"{field} must be a non-empty string.",
            )
        cleaned_employee[field] = value.strip()

    email = cleaned_employee["email"]
    if "@" not in email or "." not in email.rsplit("@", 1)[-1] or " " in email:
        raise HTTPException(status_code=422, detail="Provide a valid email address.")

    salary = employee["salary"]
    if (
        isinstance(salary, bool)
        or not isinstance(salary, (int, float))
        or not math.isfinite(salary)
        or salary < 0
    ):
        raise HTTPException(
            status_code=422,
            detail="salary must be a non-negative number.",
        )
    cleaned_employee["salary"] = salary
    return cleaned_employee


def run_database_operation(operation, *arguments):
    """Translate expected MySQL errors into useful HTTP responses."""
    try:
        return operation(*arguments)
    except mysql.connector.IntegrityError as error:
        if error.errno == 1062:
            raise HTTPException(
                status_code=409,
                detail="An employee with that email address already exists.",
            ) from error
        raise HTTPException(
            status_code=500,
            detail="MySQL rejected the operation. Check the employees table and data.",
        ) from error
    except mysql.connector.Error as error:
        raise HTTPException(
            status_code=503,
            detail="Could not complete the database operation. Check the MySQL connection.",
        ) from error


def run_file_operation(operation, *arguments):
    """Translate expected file errors into useful HTTP responses."""
    try:
        return operation(*arguments)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="File not found.") from error
    except FileExistsError as error:
        raise HTTPException(status_code=409, detail="A file with that name already exists.") from error
    except PermissionError as error:
        raise HTTPException(status_code=403, detail="Permission denied for this file operation.") from error
    except OSError as error:
        raise HTTPException(status_code=500, detail="File operation failed.") from error


def validate_file_request(data, required_fields):
    if not isinstance(data, dict) or set(data) != set(required_fields):
        fields = ", ".join(required_fields)
        raise HTTPException(status_code=422, detail=f"Provide exactly these fields: {fields}.")
    for field in required_fields:
        if not isinstance(data[field], str):
            raise HTTPException(status_code=422, detail=f"{field} must be text.")


@app.post("/employees", status_code=201)
def create_employee(employee: dict = Body(...)):
    cleaned_employee = validate_employee_data(employee)
    employee_id = run_database_operation(employee_queries.add_employee, cleaned_employee)
    return {"id": employee_id, "message": "Employee created."}


@app.get("/employees")
def read_all_employees():
    return run_database_operation(employee_queries.get_all_employees)


@app.get("/employees/search")
def search_employee_records(term: str = Query(..., min_length=1)):
    search_term = term.strip()
    if not search_term:
        raise HTTPException(status_code=422, detail="Search term cannot be blank.")
    return run_database_operation(employee_queries.search_employees, search_term)


@app.get("/employees/{employee_id}")
def read_employee(employee_id: int):
    employee = run_database_operation(employee_queries.get_employee_by_id, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return employee


@app.put("/employees/{employee_id}")
def replace_employee(employee_id: int, employee: dict = Body(...)):
    cleaned_employee = validate_employee_data(employee)
    existing_employee = run_database_operation(
        employee_queries.get_employee_by_id, employee_id
    )
    if existing_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found.")

    run_database_operation(employee_queries.update_employee, employee_id, cleaned_employee)
    return {"message": "Employee updated."}


@app.delete("/employees/{employee_id}")
def remove_employee(employee_id: int):
    deleted_rows = run_database_operation(employee_queries.delete_employee, employee_id)
    if deleted_rows == 0:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return {"message": "Employee deleted."}


@app.post("/employees/import/csv")
def import_employees_csv(data: dict = Body(...)):
    validate_file_request(data, ("filename",))
    rows = run_file_operation(file_operations.read_employee_csv, data["filename"])
    imported_count = 0
    invalid_rows = []

    for row_number, row in enumerate(rows, start=2):
        try:
            if set(row.keys()) != EMPLOYEE_FIELDS:
                raise HTTPException(
                    status_code=422,
                    detail="Row must contain name, email, department, and salary.",
                )
            row["salary"] = float(row["salary"])
            employee = validate_employee_data(row)
        except (HTTPException, TypeError, ValueError) as error:
            if isinstance(error, HTTPException):
                message = error.detail
            else:
                message = "salary must be a valid number."
            invalid_rows.append({"row": row_number, "error": message})
            continue

        try:
            run_database_operation(employee_queries.add_employee, employee)
            imported_count += 1
        except HTTPException as error:
            if error.status_code != 409:
                raise
            invalid_rows.append({"row": row_number, "error": error.detail})

    return {
        "imported_count": imported_count,
        "invalid_count": len(invalid_rows),
        "invalid_rows": invalid_rows,
    }


@app.get("/employees/export/csv")
def export_employees_csv():
    employees = run_database_operation(employee_queries.get_all_employees)
    filename = run_file_operation(
        file_operations.write_employee_csv, "employees.csv", employees
    )
    return {
        "filename": filename,
        "records_exported": len(employees),
        "saved_to": "reports/employees.csv",
    }


@app.get("/files/csv/{filename}")
def read_employee_csv(filename: str):
    records = run_file_operation(file_operations.read_employee_csv, filename)
    return {"filename": filename, "records": records}


@app.post("/files/text", status_code=201)
def create_text_file(data: dict = Body(...)):
    validate_file_request(data, ("filename",))
    filename = run_file_operation(file_operations.create_text_file, data["filename"])
    return {"filename": filename, "message": "Text file created."}


@app.put("/files/text/{filename}")
def write_text_file(filename: str, data: dict = Body(...)):
    validate_file_request(data, ("content",))
    run_file_operation(file_operations.write_text_file, filename, data["content"])
    return {"message": "Text file written."}


@app.post("/files/text/{filename}/append")
def append_text_file(filename: str, data: dict = Body(...)):
    validate_file_request(data, ("content",))
    run_file_operation(file_operations.append_text_file, filename, data["content"])
    return {"message": "Content appended."}


@app.get("/files/text/{filename}")
def read_text_file(filename: str):
    content = run_file_operation(file_operations.read_text_file, filename)
    return {"filename": filename, "content": content}


@app.get("/files/text/{filename}/lines")
def read_text_file_lines(filename: str):
    lines = run_file_operation(file_operations.read_text_file_lines, filename)
    return {"filename": filename, "lines": lines}


@app.get("/files/text/{filename}/exists")
def check_text_file_exists(filename: str):
    exists = run_file_operation(file_operations.text_file_exists, filename)
    return {"filename": filename, "exists": exists}


@app.post("/files/text/{filename}/rename")
def rename_text_file(filename: str, data: dict = Body(...)):
    validate_file_request(data, ("new_filename",))
    new_filename = run_file_operation(
        file_operations.rename_text_file, filename, data["new_filename"]
    )
    return {"filename": new_filename, "message": "Text file renamed."}


@app.post("/files/text/{filename}/copy", status_code=201)
def copy_text_file(filename: str, data: dict = Body(...)):
    validate_file_request(data, ("copy_filename",))
    copy_filename = run_file_operation(
        file_operations.copy_text_file, filename, data["copy_filename"]
    )
    return {"filename": copy_filename, "message": "Text file copied."}


@app.delete("/files/text/{filename}")
def delete_text_file(filename: str):
    run_file_operation(file_operations.delete_text_file, filename)
    return {"message": "Text file deleted."}


@app.get("/files/text/{filename}/size")
def get_text_file_size(filename: str):
    size = run_file_operation(file_operations.get_text_file_size, filename)
    return {"filename": filename, "size_bytes": size}
