import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env file from the same directory as this file
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("PORT")),
            ssl_disabled=False
        )

        if conn.is_connected():
            print("✅ Database connection successful!")
            return conn
        else:
            raise Exception("⚠️ Connection established but not active.")

    except Error as e:
        print(f"❌ Could not connect to the database: {e}")
        raise  # Re-raise the exception if you want to handle it elsewhere
