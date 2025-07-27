from user import User

user = User()
name = input("Enter your name: ")
password = input("Enter your password: ")

user.register_user(name, password)