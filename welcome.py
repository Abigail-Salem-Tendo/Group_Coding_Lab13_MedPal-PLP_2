from user import User

def welcome():
    user_manager = User()
    while True:
        print("\n=== Medication Reminder App ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Select an option: ").strip()
        if choice == "1":
            name = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            user_manager.register_user(name, password)
            return name  # Proceed to main menu after registration
        elif choice == "2":
            name = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            if user_manager.login_user(name, password):
                print(f"Welcome, {name}!")
                return name  # Proceed to main menu after login
        elif choice == "3":
            print("Goodbye!")
            return None
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    user = welcome()
    if user:
        print(f"Proceeding to main menu for {user}...")