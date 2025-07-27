from database import get_connection
class User:
    def __init__(self):
        self.connection = get_connection()
        self.cursor = self.connection.cursor()

    def register_user(self, name, password):

        try:
            self.cursor.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (name, password))
            self.connection.commit()
            print("Registered successfully")
        except Exception as e:
            print("There was an error while registering your account:", e)

    def login_user(self, name, password):
        try:
            self.cursor.execute("SELECT id FROM users WHERE name = %s AND password = %s", (name, password))
            user = self.cursor.fetchone()
            if user is None:
                print("User not found")
            else:
                print("Login successful")
        except Exception as e:
            print("There was an error while logging in:", e)

    def close_connection(self):
            self.cursor.close()
            self.connection.close()