import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from database import Database
from scheduler import start_scheduler
from config import TELEGRAM_TOKEN
from datetime import datetime
import pytz

# Initialize database instance
db = Database()

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Command to start the bot
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    db.create_user(telegram_id=user.id, username=user.username)
    update.message.reply_text("Welcome to the Reminder Bot! Use /help to see available commands.")

# Command to add a reminder
def add_reminder(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        update.message.reply_text("Usage: /add <description> <YYYY-MM-DD HH:MM:SS>")
        return

    try:
        description = " ".join(context.args[:-1])
        reminder_time = datetime.strptime(context.args[-1], "%Y-%m-%d %H:%M:%S")
        reminder_time = reminder_time.replace(tzinfo=pytz.UTC)

        db.add_reminder(
            telegram_id=update.message.from_user.id,
            description=description,
            reminder_time=reminder_time.isoformat(),
        )
        update.message.reply_text(f"Reminder added: {description} at {reminder_time} UTC.")
    except ValueError:
        update.message.reply_text("Invalid date format. Use YYYY-MM-DD HH:MM:SS.")

# Command to view reminders
def view_reminders(update: Update, context: CallbackContext) -> None:
    reminders = db.get_user_reminders(telegram_id=update.message.from_user.id)
    if not reminders:
        update.message.reply_text("You have no reminders.")
        return

    reminder_list = "\n".join(
        [f"{r['id']}: {r['description']} at {r['reminder_time']} (Notified: {r['notified']})" for r in reminders]
    )
    update.message.reply_text(f"Your reminders:\n{reminder_list}")

# Command to delete a reminder
def delete_reminder(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1 or not context.args[0].isdigit():
        update.message.reply_text("Usage: /delete <reminder_id>")
        return

    reminder_id = int(context.args[0])
    success = db.delete_reminder(reminder_id=reminder_id, telegram_id=update.message.from_user.id)
    if success:
        update.message.reply_text(f"Reminder {reminder_id} deleted.")
    else:
        update.message.reply_text(f"Reminder {reminder_id} not found.")

# Main function to start the bot
def main() -> None:
    # Use TELEGRAM_TOKEN from config.py
    updater = Updater(token=TELEGRAM_TOKEN)

    # Register commands
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add_reminder))
    dispatcher.add_handler(CommandHandler("view", view_reminders))
    dispatcher.add_handler(CommandHandler("delete", delete_reminder))

    # Start the scheduler
    start_scheduler()

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
