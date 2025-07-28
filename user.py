from database import get_connection
import sys 

class User:
    def register_user(self, name, password):
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (name, password))
            connection.commit()
            print("✅ Registered successfully")
        except Exception as e:
            print("❌ There was an error while registering your account:", e)
            sys.exit(1) 
        finally:
            cursor.close()
            connection.close()

    def login_user(self, name, password):
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE name = %s AND password = %s", (name, password))
            user = cursor.fetchone()
            if user:
                print("✅ Login successful")
                return True
            else:
                print("❌ Invalid username or password")
                return False
        except Exception as e:
            print("❌ There was an error while logging in:", e)
            return False
        finally:
            cursor.close()
            connection.close()