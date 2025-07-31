from user import User

def welcome():
    user_manager = User()
    while True:
        print("\n" + "="*50)
        print("🌟  MEDICATION REMINDER APP  🌟".center(50))
        print("="*50)
        print("\nPlease choose an option:")
        print("  [1] 📝 Register")
        print("  [2] 🔑 Login")
        print("  [3] 🚪 Exit")
        print("-"*50)
        choice = input("👉 Enter your choice (1/2/3): ").strip()
        if choice == "1":
            print("\n--- Registration ---")
            name = input("👤 Username: ").strip()
            while True:
                password = input("🔒 Password (digits only): ").strip()
                if password.isdigit():
                    break
                else:
                    print("❌ Password must be a number. Please try again.")
            user_manager.register_user(name, password)
            print("🎉 Registration complete! Proceeding to main menu...")
            return  # Don't return name; session is already set
        elif choice == "2":
            print("\n--- Login ---")
            name = input("👤 Username: ").strip()
            password = input("🔒 Password: ").strip()
            if user_manager.login_user(name, password):
                print(f"👋 Welcome, {name}! Proceeding to main menu...")
                return  # Don't return name; session is already set
        elif choice == "3":
            print("👋 Goodbye! Stay healthy!")
            exit(0)
        else:
            print("❌ Invalid option. Please try again.")
