from apscheduler.schedulers.background import BackgroundScheduler
from tenacity import retry, stop_after_attempt, wait_fixed
from database import Database
from telegram import Bot
from config import TELEGRAM_TOKEN

db = Database()
bot = Bot(token=TELEGRAM_TOKEN)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def safe_send_message(chat_id: int, text: str) -> None:
    """Send a message to a user with retries."""
    bot.send_message(chat_id=chat_id, text=text)


def send_reminders() -> None:
    """Send reminders that are due."""
    reminders = db.get_due_reminders()
    for reminder in reminders:
        try:
            safe_send_message(
                chat_id=reminder["telegram_id"],
                text=f"⏰ Reminder: {reminder['description']} (Time: {reminder['reminder_time']})",
            )
            db.mark_reminder_as_notified(reminder["id"])
        except Exception as e:
            print(f"Error sending reminder {reminder['id']}: {e}")


def start_scheduler() -> None:
    """Start the background scheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_reminders, "interval", seconds=10)
    scheduler.start()
