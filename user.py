from database import get_connection
import sys

# Global session shared across app
session = {}

class User:
    def user_exists(self, name):
        """Check if the username already exists"""
        conn = get_connection()
        cursor = conn.cursor(buffered=True)  # <-- buffered!
        try:
            cursor.execute("SELECT 1 FROM users WHERE name = %s LIMIT 1", (name,))
            return cursor.fetchone() is not None
        except Exception as e:
            print("❌ Error checking for existing user:", e)
            return True  # assume taken to be safe
        finally:
            cursor.close()
            conn.close()


    def register_user(self, name, password):
        if self.user_exists(name):
            print("❌ Username already taken. Please choose a different name.")
            sys.exit(1)

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (name, password))
            conn.commit()
            print("✅ Registered successfully")
            # Optionally log in user right after registering
            session["user"] = {"name": name}  # You could also fetch and include id
        except Exception as e:
            print("❌ There was an error while registering your account:", e)
            sys.exit(1)
        finally:
            cursor.close()
            conn.close()

    def login_user(self, name, password):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE name = %s AND password = %s", (name, password))
            user = cursor.fetchone()
            if user:
                session["user"] = user  # Store the full user record
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
            conn.close()

    def get_logged_in_user(self):
        return session.get("user")
