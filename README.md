# python_-API_-using-_MySQL

## Stage 4: Connect Python to MySQL

1. Copy `.env.example` to `.env`.
2. Replace the example MySQL username and password in `.env` with your local MySQL credentials.
3. Run `.\.venv\Scripts\python.exe database.py` from the project folder.

The connection settings are loaded from `.env` by `database.py`. The `.env` file is ignored by Git so database credentials are not committed.

## Stage 5: Employee API

Start the API from the project folder with `.\.venv\Scripts\python.exe -m uvicorn main:app --reload`.
Open `http://127.0.0.1:8000/docs` to view the available employee endpoints.

## Stage 7: Text file operations

Text-file APIs accept only `.txt` filenames and store them under `uploads/text_files`.
They support creating, writing, appending, reading, checking, renaming, copying,
deleting, and checking the size of text files. File paths supplied by clients are
validated to prevent access outside the designated folder.

## Stage 8: Employee CSV import and export

Place import files in `uploads/csv_files` with this exact header:
`name,email,department,salary`. Import using `POST /employees/import/csv` with
`{"filename":"employees.csv"}`. Valid rows are inserted; invalid or duplicate
rows are reported in the response, while other valid rows can still be imported.

Read a CSV file as records using `GET /files/csv/{filename}`.
Export using `GET /employees/export/csv`. The current employee records are saved
to `reports/employees.csv`; the response reports the number of exported records.
The upload and report folders are ignored by Git to avoid committing employee data.