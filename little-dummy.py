import json
import os
import datetime
from typing import Dict, List, Optional
import time
import threading

class MedicationReminderApp:
    def __init__(self):
        self.current_user = None
        self.users_folder = "medication_users"
        self.ensure_users_folder_exists()
        self.reminder_thread = None
        self.running_reminders = False
        
    def ensure_users_folder_exists(self):
        """Create users folder if it doesn't exist"""
        if not os.path.exists(self.users_folder):
            os.makedirs(self.users_folder)
    
    def get_user_file_path(self, username: str) -> str:
        """Get the file path for a user's medication history"""
        filename = f"{username}'s_Medication_History.json"
        return os.path.join(self.users_folder, filename)
    
    def load_user_data(self, username: str) -> Dict:
        """Load user data from JSON file"""
        file_path = self.get_user_file_path(username)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {"username": username, "medications": []}
        return {"username": username, "medications": []}
    
    def save_user_data(self, user_data: Dict):
        """Save user data to JSON file"""
        file_path = self.get_user_file_path(user_data["username"])
        with open(file_path, 'w') as f:
            json.dump(user_data, f, indent=4, default=str)
    
    def login_or_register(self):
        """Handle user login/registration"""
        print("\n" + "="*50)
        print("    MEDICATION REMINDER APP")
        print("="*50)
        
        username = input("\n>>> Enter your username to access your medical reminders: ").strip()
        
        if not username:
            print("❌ Username cannot be empty!")
            return False
        
        self.current_user = username
        user_data = self.load_user_data(username)
        
        if not os.path.exists(self.get_user_file_path(username)):
            print(f"👋 Welcome new user, {username}! Creating your medication profile...")
        else:
            print(f"👋 Welcome back, {username}!")
        
        return True
    
    def validate_time_input(self, time_str: str) -> bool:
        """Validate time input (0-23 hours)"""
        try:
            hour = int(time_str)
            return 0 <= hour <= 23
        except ValueError:
            return False
    
    def validate_duration_input(self, duration_str: str) -> Optional[int]:
        """Parse and validate duration input (returns days)"""
        duration_str = duration_str.lower().strip()
        
        try:
            if 'day' in duration_str:
                return int(duration_str.split()[0])
            elif 'week' in duration_str:
                weeks = int(duration_str.split()[0])
                return weeks * 7
            elif 'month' in duration_str:
                months = int(duration_str.split()[0])
                return months * 30  # Approximate
            else:
                # Try to parse as just a number (assume days)
                return int(duration_str)
        except (ValueError, IndexError):
            return None
    
    def calculate_reminder_times(self, first_dose_hour: int, times_per_day: int, interval_hours: float) -> List[str]:
        """Calculate all reminder times for a day"""
        reminder_times = []
        current_hour = first_dose_hour
        
        for i in range(times_per_day):
            hour = int(current_hour) % 24
            minute = int((current_hour % 1) * 60)
            reminder_times.append(f"{hour:02d}:{minute:02d}")
            current_hour += interval_hours
        
        return reminder_times
    
    def add_medication(self):
        """Add a new medication with all details"""
        print("\n" + "-"*40)
        print("     ADD NEW MEDICATION")
        print("-"*40)
        
        # Get medication name (required)
        while True:
            med_name = input("\n>>> Enter the name of your medication* (MUST ANSWER): ").strip()
            if med_name:
                break
            print("❌ Medication name is required!")
        
        # Get ailment (optional)
        ailment = input(">>> What are you taking this for / what ailment(disease) are you suffering from?* (Optional): ").strip()
        if not ailment:
            ailment = "Not specified"
        
        # Get duration
        while True:
            duration_input = input(">>> How long will your medicine last? (e.g: 67 days / 2 weeks): ").strip()
            duration_days = self.validate_duration_input(duration_input)
            if duration_days:
                break
            print("❌ Please enter a valid duration (e.g., '30 days', '2 weeks', '1 month')")
        
        # Get times per day
        while True:
            try:
                times_per_day = int(input(">>> How many times a day will you take it?: ").strip())
                if times_per_day > 0:
                    break
                print("❌ Please enter a positive number!")
            except ValueError:
                print("❌ Please enter a valid number!")
        
        # Get first dose time
        print("\n    Time Format Guide:")
        print("    (For AM use: 0-11, e.g., 8 for 8:00 AM)")
        print("    (For PM use: 12-23, e.g., 20 for 8:00 PM)")
        
        while True:
            first_dose_input = input(">>> When do you take your first dose of the day? (0-23): ").strip()
            if self.validate_time_input(first_dose_input):
                first_dose_hour = int(first_dose_input)
                break
            print("❌ Please enter a valid hour (0-23)!")
        
        # Get interval between doses
        while True:
            try:
                interval_hours = float(input(">>> What is the time interval in HOURS before you take another dose? (e.g: 2 or 6.5): ").strip())
                if interval_hours > 0:
                    break
                print("❌ Please enter a positive number!")
            except ValueError:
                print("❌ Please enter a valid number!")
        
        # Calculate reminder times
        reminder_times = self.calculate_reminder_times(first_dose_hour, times_per_day, interval_hours)
        
        # Create medication record
        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(days=duration_days)
        
        medication = {
            "name": med_name,
            "ailment": ailment,
            "times_per_day": times_per_day,
            "reminder_times": reminder_times,
            "interval_hours": interval_hours,
            "duration_days": duration_days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "created_at": datetime.datetime.now().isoformat()
        }
        
        # Save to user data
        user_data = self.load_user_data(self.current_user)
        user_data["medications"].append(medication)
        self.save_user_data(user_data)
        
        print(f"\n✅ Medication '{med_name}' added successfully!")
        print(f"📅 Duration: {duration_days} days")
        print(f"⏰ Daily reminder times: {', '.join(reminder_times)}")
        print(f"💊 Take {times_per_day} time(s) per day every {interval_hours} hours")
        
        input("\nPress Enter to continue...")
    
    def view_medication_history(self):
        """Display user's medication history"""
        print("\n" + "-"*40)
        print("     YOUR MEDICATION HISTORY")
        print("-"*40)
        
        user_data = self.load_user_data(self.current_user)
        medications = user_data.get("medications", [])
        
        if not medications:
            print("\n📝 No medications found in your history.")
            print("   Add some medications first!")
        else:
            for i, med in enumerate(medications, 1):
                print(f"\n--- Medication #{i} ---")
                print(f"💊 Name: {med['name']}")
                print(f"🏥 For: {med['ailment']}")
                print(f"📊 Times per day: {med['times_per_day']}")
                print(f"⏰ Reminder times: {', '.join(med['reminder_times'])}")
                print(f"⏳ Interval: Every {med['interval_hours']} hours")
                print(f"📅 Duration: {med['duration_days']} days")
                
                # Parse dates
                try:
                    start_date = datetime.datetime.fromisoformat(med['start_date'])
                    end_date = datetime.datetime.fromisoformat(med['end_date'])
                    now = datetime.datetime.now()
                    
                    print(f"🗓️  Start date: {start_date.strftime('%Y-%m-%d')}")
                    print(f"🏁 End date: {end_date.strftime('%Y-%m-%d')}")
                    
                    if now > end_date:
                        print("✅ Status: COMPLETED")
                    elif now < start_date:
                        print("⏳ Status: UPCOMING")
                    else:
                        days_left = (end_date - now).days
                        print(f"🔄 Status: ACTIVE ({days_left} days remaining)")
                except:
                    print("❌ Date information unavailable")
        
        input("\nPress Enter to continue...")
    
    def start_reminder_system(self):
        """Start the reminder system in background"""
        if self.running_reminders:
            print("⚠️  Reminder system is already running!")
            return
        
        print("\n🔔 Starting reminder system...")
        print("   Reminders will appear when it's time to take your medication.")
        print("   Continue using the app normally - reminders run in background.")
        
        self.running_reminders = True
        self.reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self.reminder_thread.start()
        
        input("\nPress Enter to continue...")
    
    def _reminder_loop(self):
        """Background loop for medication reminders"""
        while self.running_reminders:
            try:
                user_data = self.load_user_data(self.current_user)
                medications = user_data.get("medications", [])
                current_time = datetime.datetime.now()
                current_time_str = current_time.strftime("%H:%M")
                
                for med in medications:
                    # Check if medication is currently active
                    try:
                        start_date = datetime.datetime.fromisoformat(med['start_date'])
                        end_date = datetime.datetime.fromisoformat(med['end_date'])
                        
                        if start_date <= current_time <= end_date:
                            # Check if current time matches any reminder time
                            for reminder_time in med['reminder_times']:
                                if reminder_time == current_time_str:
                                    self._show_reminder(med)
                    except:
                        continue
                
                # Check every minute
                time.sleep(60)
            except:
                break
    
    def _show_reminder(self, medication):
        """Display a medication reminder"""
        print(f"\n🔔 MEDICATION REMINDER! 🔔")
        print(f"⏰ Time to take: {medication['name']}")
        print(f"🏥 For: {medication['ailment']}")
        print(f"📋 Current time: {datetime.datetime.now().strftime('%H:%M')}")
        print("-" * 40)
    
    def stop_reminder_system(self):
        """Stop the reminder system"""
        if not self.running_reminders:
            print("⚠️  Reminder system is not running!")
            return
        
        print("\n🔕 Stopping reminder system...")
        self.running_reminders = False
        print("✅ Reminder system stopped.")
        
        input("\nPress Enter to continue...")
    
    def show_active_medications(self):
        """Show currently active medications"""
        print("\n" + "-"*40)
        print("     ACTIVE MEDICATIONS")
        print("-"*40)
        
        user_data = self.load_user_data(self.current_user)
        medications = user_data.get("medications", [])
        current_time = datetime.datetime.now()
        active_meds = []
        
        for med in medications:
            try:
                start_date = datetime.datetime.fromisoformat(med['start_date'])
                end_date = datetime.datetime.fromisoformat(med['end_date'])
                
                if start_date <= current_time <= end_date:
                    active_meds.append(med)
            except:
                continue
        
        if not active_meds:
            print("\n📝 No active medications at this time.")
        else:
            for i, med in enumerate(active_meds, 1):
                print(f"\n--- Active Medication #{i} ---")
                print(f"💊 {med['name']} for {med['ailment']}")
                print(f"⏰ Today's doses at: {', '.join(med['reminder_times'])}")
                
                try:
                    end_date = datetime.datetime.fromisoformat(med['end_date'])
                    days_left = (end_date - current_time).days
                    print(f"📅 Days remaining: {days_left}")
                except:
                    print("📅 Days remaining: Unknown")
        
        input("\nPress Enter to continue...")
    
    def main_menu(self):
        """Display and handle main menu"""
        while True:
            print("\n" + "="*50)
            print(f"    MEDICATION REMINDER - {self.current_user}")
            print("="*50)
            print("\n📋 MAIN MENU:")
            print("1. 💊 Add New Medication")
            print("2. 📖 View Medication History")
            print("3. 🔔 Start Reminder System")
            print("4. 🔕 Stop Reminder System")
            print("5. 📊 Show Active Medications")
            print("6. 🚪 Exit Application")
            
            choice = input("\n>>> Enter your choice (1-6): ").strip()
            
            if choice == "1":
                self.add_medication()
            elif choice == "2":
                self.view_medication_history()
            elif choice == "3":
                self.start_reminder_system()
            elif choice == "4":
                self.stop_reminder_system()
            elif choice == "5":
                self.show_active_medications()
            elif choice == "6":
                self.stop_reminder_system()
                print("\n👋 Thank you for using Medication Reminder App!")
                print("💝 Stay healthy and take care!")
                break
            else:
                print("❌ Invalid choice! Please enter a number between 1-6.")
                input("Press Enter to continue...")
    
    def run(self):
        """Main application entry point"""
        try:
            if self.login_or_register():
                self.main_menu()
        except KeyboardInterrupt:
            print("\n\n👋 Application interrupted. Goodbye!")
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please restart the application.")





def main():
    """Application entry point"""
    app = MedicationReminderApp()
    app.run()

if __name__ == "__main__":
    main()