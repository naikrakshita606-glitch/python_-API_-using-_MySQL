import csv
import shutil
from pathlib import Path


PROJECT_DIRECTORY = Path(__file__).resolve().parent
UPLOADS_DIRECTORY = PROJECT_DIRECTORY / "uploads"
TEXT_FILES_DIRECTORY = UPLOADS_DIRECTORY / "text_files"
CSV_FILES_DIRECTORY = UPLOADS_DIRECTORY / "csv_files"
REPORTS_DIRECTORY = PROJECT_DIRECTORY / "reports"
EMPLOYEE_CSV_FIELDS = ("name", "email", "department", "salary")


def get_text_file_path(filename):
    """Return a validated .txt path confined to uploads/text_files."""
    if (
        not isinstance(filename, str)
        or not filename
        or filename in {".", ".."}
        or "/" in filename
        or "\\" in filename
        or Path(filename).name != filename
        or Path(filename).suffix.lower() != ".txt"
    ):
        raise ValueError("Use a plain .txt filename without folder paths.")

    UPLOADS_DIRECTORY.mkdir(exist_ok=True)
    if UPLOADS_DIRECTORY.resolve() != PROJECT_DIRECTORY / "uploads":
        raise PermissionError("The uploads directory must not be a symbolic link.")

    TEXT_FILES_DIRECTORY.mkdir(exist_ok=True)
    uploads_directory = UPLOADS_DIRECTORY.resolve()
    if TEXT_FILES_DIRECTORY.resolve() != uploads_directory / "text_files":
        raise PermissionError("The text-files directory must not be a symbolic link.")

    file_path = TEXT_FILES_DIRECTORY / filename
    if file_path.resolve().parent != TEXT_FILES_DIRECTORY.resolve():
        raise ValueError("File paths must stay inside the text-files directory.")
    return file_path


def create_text_file(filename):
    file_path = get_text_file_path(filename)
    with file_path.open("x", encoding="utf-8"):
        pass
    return filename


def write_text_file(filename, content):
    file_path = get_text_file_path(filename)
    with file_path.open("w", encoding="utf-8", newline="") as file:
        file.write(content)


def append_text_file(filename, content):
    file_path = get_text_file_path(filename)
    with file_path.open("a", encoding="utf-8", newline="") as file:
        file.write(content)


def read_text_file(filename):
    file_path = get_text_file_path(filename)
    with file_path.open("r", encoding="utf-8") as file:
        return file.read()


def read_text_file_lines(filename):
    file_path = get_text_file_path(filename)
    with file_path.open("r", encoding="utf-8") as file:
        return [line.rstrip("\r\n") for line in file]


def text_file_exists(filename):
    return get_text_file_path(filename).is_file()


def rename_text_file(filename, new_filename):
    file_path = get_text_file_path(filename)
    new_file_path = get_text_file_path(new_filename)
    if not file_path.is_file():
        raise FileNotFoundError(filename)
    if new_file_path.exists():
        raise FileExistsError(new_filename)
    file_path.rename(new_file_path)
    return new_filename


def copy_text_file(filename, copy_filename):
    file_path = get_text_file_path(filename)
    copy_file_path = get_text_file_path(copy_filename)
    if not file_path.is_file():
        raise FileNotFoundError(filename)
    if copy_file_path.exists():
        raise FileExistsError(copy_filename)
    shutil.copyfile(file_path, copy_file_path)
    return copy_filename


def delete_text_file(filename):
    file_path = get_text_file_path(filename)
    if not file_path.is_file():
        raise FileNotFoundError(filename)
    file_path.unlink()


def get_text_file_size(filename):
    file_path = get_text_file_path(filename)
    if not file_path.is_file():
        raise FileNotFoundError(filename)
    return file_path.stat().st_size


def get_employee_csv_path(filename):
    """Return a validated .csv path confined to uploads/csv_files."""
    if (
        not isinstance(filename, str)
        or not filename
        or filename in {".", ".."}
        or "/" in filename
        or "\\" in filename
        or Path(filename).name != filename
        or Path(filename).suffix.lower() != ".csv"
    ):
        raise ValueError("Use a plain .csv filename without folder paths.")

    UPLOADS_DIRECTORY.mkdir(exist_ok=True)
    if UPLOADS_DIRECTORY.resolve() != PROJECT_DIRECTORY / "uploads":
        raise PermissionError("The uploads directory must not be a symbolic link.")

    CSV_FILES_DIRECTORY.mkdir(exist_ok=True)
    uploads_directory = UPLOADS_DIRECTORY.resolve()
    if CSV_FILES_DIRECTORY.resolve() != uploads_directory / "csv_files":
        raise PermissionError("The CSV-files directory must not be a symbolic link.")

    file_path = CSV_FILES_DIRECTORY / filename
    if file_path.resolve().parent != CSV_FILES_DIRECTORY.resolve():
        raise ValueError("File paths must stay inside the CSV-files directory.")
    return file_path


def read_employee_csv(filename):
    """Read CSV rows with the required employee column names."""
    file_path = get_employee_csv_path(filename)
    try:
        with file_path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, strict=True)
            if reader.fieldnames != list(EMPLOYEE_CSV_FIELDS):
                raise ValueError(
                    "CSV headers must be: name,email,department,salary."
                )
            return list(reader)
    except (csv.Error, UnicodeDecodeError) as error:
        raise ValueError("The CSV file is malformed or is not valid UTF-8.") from error


def write_employee_csv(filename, employees):
    """Write employee records to a CSV file inside reports."""
    if filename != "employees.csv":
        raise ValueError("Export filename must be employees.csv.")

    REPORTS_DIRECTORY.mkdir(exist_ok=True)
    if REPORTS_DIRECTORY.resolve() != PROJECT_DIRECTORY / "reports":
        raise PermissionError("The reports directory must not be a symbolic link.")

    file_path = REPORTS_DIRECTORY / filename
    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=EMPLOYEE_CSV_FIELDS)
        writer.writeheader()
        for employee in employees:
            writer.writerow({field: employee[field] for field in EMPLOYEE_CSV_FIELDS})
    return filename
