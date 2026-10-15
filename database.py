import os

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """Connect to MySQL using settings from the environment."""
    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE")

    if not user or not database:
        raise ValueError(
            "Set MYSQL_USER and MYSQL_DATABASE in your .env file before connecting."
        )

    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )


if __name__ == "__main__":
    connection = None

    try:
        connection = get_connection()
        print("Connected to MySQL successfully.")
    except mysql.connector.Error as error:
        raise SystemExit(f"MySQL connection failed: {error}") from error
    finally:
        if connection is not None and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")
