# Telegram Reminder Bot

Telegram Reminder Bot is a simple Python-based application that allows users to create, view, and manage reminders via a Telegram bot. The bot sends automatic notifications at the scheduled times and uses a PostgreSQL database to store user and reminder data.

---

## Features

- **Add Reminders**: Create reminders with a description and a specific date/time.
- **View Reminders**: List all upcoming reminders.
- **Delete Reminders**: Remove reminders by their ID.
- **Automatic Notifications**: The bot sends messages to remind you of events at the correct time.

---

## Requirements

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Telegram Bot Token (from [BotFather](https://core.telegram.org/bots#botfather))

---

## Database setup
Create a new PostgreSQL database:
```
CREATE DATABASE reminder_db;
CREATE USER reminder_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE reminder_db TO reminder_user;
```
Execute the database schema:
```
psql -U reminder_user -d reminder_db -f setup.sql
```

## Usage
Telegram Commands
Start the bot:
```
/start
```
Registers you in the system if you're a new user.
Add a reminder:
```
/add <description> <YYYY-MM-DD HH:MM:SS>
```
View your reminders:
```
/view
```
Delete a reminder:
```
/delete <reminder_id>
```
