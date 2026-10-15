from database import get_connection


def run_query(sql, values=(), fetch=None, commit=False):
    """Run one SQL statement and always close its cursor and connection."""
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, values)

        if commit:
            connection.commit()

        if fetch == "one":
            return cursor.fetchone()
        if fetch == "all":
            return cursor.fetchall()
        if fetch == "result":
            return {"rowcount": cursor.rowcount, "lastrowid": cursor.lastrowid}
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def add_employee(employee):
    sql = """
        INSERT INTO employees (name, email, department, salary)
        VALUES (%s, %s, %s, %s)
    """
    result = run_query(
        sql,
        (employee["name"], employee["email"], employee["department"], employee["salary"]),
        commit=True,
        fetch="result",
    )
    return result["lastrowid"]


def get_all_employees():
    sql = """
        SELECT id, name, email, department, salary
        FROM employees
        ORDER BY id
    """
    return run_query(sql, fetch="all")


def get_employee_by_id(employee_id):
    sql = """
        SELECT id, name, email, department, salary
        FROM employees
        WHERE id = %s
    """
    return run_query(sql, (employee_id,), fetch="one")


def update_employee(employee_id, employee):
    sql = """
        UPDATE employees
        SET name = %s, email = %s, department = %s, salary = %s
        WHERE id = %s
    """
    result = run_query(
        sql,
        (
            employee["name"],
            employee["email"],
            employee["department"],
            employee["salary"],
            employee_id,
        ),
        commit=True,
        fetch="result",
    )
    return result["rowcount"]


def delete_employee(employee_id):
    sql = "DELETE FROM employees WHERE id = %s"
    result = run_query(sql, (employee_id,), commit=True, fetch="result")
    return result["rowcount"]


def search_employees(term):
    sql = """
        SELECT id, name, email, department, salary
        FROM employees
        WHERE name LIKE %s OR department LIKE %s
        ORDER BY id
    """
    search_term = f"%{term}%"
    return run_query(sql, (search_term, search_term), fetch="all")
