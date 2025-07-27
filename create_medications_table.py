from database import get_connection

def create_medications_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(255) NOT NULL,
            ailment VARCHAR(255),
            times_per_day INT,
            reminder_times VARCHAR(255),
            interval_hours FLOAT,
            duration_days INT,
            start_date VARCHAR(50),
            end_date VARCHAR(50),
            created_at VARCHAR(50),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 'medications' table created (if it did not exist).")

if __name__ == "__main__":
    create_medications_table()