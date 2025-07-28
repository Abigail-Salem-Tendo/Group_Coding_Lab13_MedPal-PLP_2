# 💊 MedPal - Medication Reminder App

A command-line app to help users keep track of their medications and get reminders.

##  Features

- Add new medications with name, ailment, schedule, and duration  
- View medication history and status (Active, Completed, Upcoming)  
- Update medication details  
- Delete medications  
- Get automated reminders based on set times

##  How to Run

1. Make sure MySQL is running and the database is set up properly  
2. Install dependencies (if any):  
   ```bash
   pip install mysql-connector-python
   ```
3. Run the app:  
   ```bash
   python main_menu.py
   ```

## User Flow

- On startup, enter your username (a new one is created if it doesn't exist)
- Choose actions from the main menu
- The app will remind you of medications at scheduled times (in the background)

## Tech Stack

- Python  
- MySQL

## Project Structure

- `main_menu.py` – main app logic and user interaction  
- `database.py` – handles DB connection  
- `welcome.py` – user login prompt