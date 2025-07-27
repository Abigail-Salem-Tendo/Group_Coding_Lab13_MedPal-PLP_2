import datetime
from typing import List, Optional
import time
import threading
from database import get_connection
from welcome import welcome
import mysql.connector

class MedicationReminderApp:
    def __init__(self, current_user):
        self.current_user = current_user
        self.reminder_thread = None
        self.running_reminders = False

    def get_user_id(self, username: str) -> Optional[int]:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE name = %s", (username,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            if result:
                return result[0]
            return None
        except mysql.connector.Error as err:
            print(f"❌ Database error while fetching user ID: {err}")
            return None

    def create_user(self, username: str):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name) VALUES (%s)", (username,))
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"❌ Database error while creating user: {err}")

    def validate_time_input(self, time_str: str) -> bool:
        try:
            hour = int(time_str)
            return 0 <= hour <= 23
        except ValueError:
            return False

    def validate_duration_input(self, duration_str: str) -> Optional[int]:
        duration_str = duration_str.lower().strip()
        try:
            if 'day' in duration_str:
                return int(duration_str.split()[0])
            elif 'week' in duration_str:
                weeks = int(duration_str.split()[0])
                return weeks * 7
            elif 'month' in duration_str:
                months = int(duration_str.split()[0])
                return months * 30
            else:
                return int(duration_str)
        except (ValueError, IndexError):
            return None

    def calculate_reminder_times(self, first_dose_hour: int, times_per_day: int, interval_hours: float) -> List[str]:
        reminder_times = []
        current_hour = first_dose_hour
        for i in range(times_per_day):
            hour = int(current_hour) % 24
            minute = int((current_hour % 1) * 60)
            reminder_times.append(f"{hour:02d}:{minute:02d}")
            current_hour += interval_hours
        return reminder_times

    def add_medication(self):
        print("\n" + "-"*40)
        print("     ADD NEW MEDICATION")
        print("-"*40)
        while True:
            med_name = input("\n>>> Enter the name of your medication* (MUST ANSWER): ").strip()
            if med_name:
                break
            print("❌ Medication name is required!")
        ailment = input(">>> What are you taking this for / what ailment(disease) are you suffering from?* (Optional): ").strip()
        if not ailment:
            ailment = "Not specified"
        while True:
            duration_input = input(">>> How long will your medicine last? (e.g: 67 days / 2 weeks): ").strip()
            duration_days = self.validate_duration_input(duration_input)
            if duration_days:
                break
            print("❌ Please enter a valid duration (e.g., '30 days', '2 weeks', '1 month')")
        while True:
            try:
                times_per_day = int(input(">>> How many times a day will you take it?: ").strip())
                if times_per_day > 0:
                    break
                print("❌ Please enter a positive number!")
            except ValueError:
                print("❌ Please enter a valid number!")
        print("\n    Time Format Guide:")
        print("    (For AM use: 0-11, e.g., 8 for 8:00 AM)")
        print("    (For PM use: 12-23, e.g., 20 for 8:00 PM)")
        while True:
            first_dose_input = input(">>> When do you take your first dose of the day? (0-23): ").strip()
            if self.validate_time_input(first_dose_input):
                first_dose_hour = int(first_dose_input)
                break
            print("❌ Please enter a valid hour (0-23)!")
        while True:
            try:
                interval_hours = float(input(">>> What is the time interval in HOURS before you take another dose? (e.g: 2 or 6.5): ").strip())
                if interval_hours > 0:
                    break
                print("❌ Please enter a positive number!")
            except ValueError:
                print("❌ Please enter a valid number!")
        reminder_times = self.calculate_reminder_times(first_dose_hour, times_per_day, interval_hours)
        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(days=duration_days)
        user_id = self.get_user_id(self.current_user)
        if user_id is None:
            print("❌ Could not find user. Please login again.")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO medications 
                (user_id, name, ailment, times_per_day, reminder_times, interval_hours, duration_days, start_date, end_date, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id, med_name, ailment, times_per_day, ",".join(reminder_times), interval_hours, duration_days,
                start_date.isoformat(), end_date.isoformat(), datetime.datetime.now().isoformat()
            ))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"\n✅ Medication '{med_name}' added successfully!")
            print(f"📅 Duration: {duration_days} days")
            print(f"⏰ Daily reminder times: {', '.join(reminder_times)}")
            print(f"💊 Take {times_per_day} time(s) per day every {interval_hours} hours")
        except mysql.connector.Error as err:
            print(f"❌ Database error while adding medication: {err}")
        input("\nPress Enter to continue...")

    def view_medication_history(self):
        print("\n" + "-"*40)
        print("     YOUR MEDICATION HISTORY")
        print("-"*40)
        user_id = self.get_user_id(self.current_user)
        if user_id is None:
            print("❌ Could not find user. Please login again.")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM medications WHERE user_id = %s", (user_id,))
            medications = cursor.fetchall()
            cursor.close()
            conn.close()
            if not medications:
                print("\n📝 No medications found in your history.")
                print("   Add some medications first!")
            else:
                for i, med in enumerate(medications, 1):
                    print(f"\n--- Medication #{i} ---")
                    print(f"💊 Name: {med['name']}")
                    print(f"🏥 For: {med['ailment']}")
                    print(f"📊 Times per day: {med['times_per_day']}")
                    print(f"⏰ Reminder times: {med['reminder_times']}")
                    print(f"⏳ Interval: Every {med['interval_hours']} hours")
                    print(f"📅 Duration: {med['duration_days']} days")
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
                    except Exception as e:
                        print("❌ Date information unavailable:", e)
            input("\nPress Enter to continue...")
        except mysql.connector.Error as err:
            print(f"❌ Database error while fetching medication history: {err}")

    def delete_medication(self):
        user_id = self.get_user_id(self.current_user)
        if user_id is None:
            print("❌ Could not find user. Please login again.")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, name FROM medications WHERE user_id = %s", (user_id,))
            meds = cursor.fetchall()
            if not meds:
                print("No medications to delete.")
                cursor.close()
                conn.close()
                return
            print("\nYour Medications:")
            for med in meds:
                print(f"  [{med['id']}] {med['name']}")
            med_id = input("Enter the ID of the medication to delete: ").strip()
            cursor.execute("DELETE FROM medications WHERE id = %s AND user_id = %s", (med_id, user_id))
            conn.commit()
            print("✅ Medication deleted (if ID was valid).")
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"❌ Database error while deleting medication: {err}")

    def update_medication(self):
        user_id = self.get_user_id(self.current_user)
        if user_id is None:
            print("❌ Could not find user. Please login again.")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, name, ailment FROM medications WHERE user_id = %s", (user_id,))
            meds = cursor.fetchall()
            if not meds:
                print("No medications to update.")
                cursor.close()
                conn.close()
                return
            print("\nYour Medications:")
            for med in meds:
                print(f"  [{med['id']}] {med['name']} ({med['ailment']})")
            med_id = input("Enter the ID of the medication to update: ").strip()
            new_name = input("Enter new name (leave blank to keep current): ").strip()
            new_ailment = input("Enter new ailment (leave blank to keep current): ").strip()
            update_fields = []
            params = []
            if new_name:
                update_fields.append("name = %s")
                params.append(new_name)
            if new_ailment:
                update_fields.append("ailment = %s")
                params.append(new_ailment)
            if update_fields:
                params.append(med_id)
                params.append(user_id)
                cursor.execute(f"UPDATE medications SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s", tuple(params))
                conn.commit()
                print("✅ Medication updated.")
            else:
                print("No changes made.")
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"❌ Database error while updating medication: {err}")

def main():
    try:
        user = welcome()
        if user:
            app = MedicationReminderApp(user)
            while True:
                print("\n" + "="*50)
                print(f"🌿 MAIN MENU - {user.upper()} 🌿".center(50))
                print("="*50)
                print("  [1] ➕ Add Medication")
                print("  [2] 📋 View Medication History")
                print("  [3] ✏️ Update Medication")
                print("  [4] 🗑️ Delete Medication")
                print("  [5] 🚪 Logout")
            
                print("-"*50)
                try:
                    choice = input("👉 Enter your choice (1/2/3/4/5): ").strip()
                except KeyboardInterrupt:
                    print("\n❌ Program interrupted. Exiting gracefully.")
                    break
                if choice == "1":
                    print("\n--- Add Medication ---")
                    app.add_medication()
                elif choice == "2":
                    print("\n--- Medication History ---")
                    app.view_medication_history()
                elif choice == "3":
                    print("\n--- Update Medication ---")
                    app.update_medication()
                elif choice == "4":
                    print("\n--- Delete Medication ---")
                    app.delete_medication()
                elif choice == "5":
                    print("👋 Logging out... Stay healthy!")
                    break
                else:
                    print("❌ Invalid option. Please try again.")
    except mysql.connector.Error as err:
        print(f"❌ Could not connect to the database: {err}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()