from user import User

def main():
    """
    Using this function to test the functionality of User.
    It provides a menu where the user can either register or
    login if they are already registered.
    """
    user = User()

    while True:
        print("\n=== User Menu ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            name = input("Enter your name: ")
            password = input("Enter your password: ")
            user.register_user(name, password)

        elif choice == "2":
            name = input("Enter your name: ")
            password = input("Enter your password: ")
            user.login_user(name, password)

        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("⚠️ Invalid choice, try again.")

if __name__ == "__main__":
    main()

