from typing import List, Dict, Optional
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG


class Database:
    def __init__(self):
        """Initialize the database connection pool."""
        self.pool = ThreadedConnectionPool(minconn=1, maxconn=10, **DB_CONFIG)

    def get_connection(self):
        """Get a connection from the pool."""
        return self.pool.getconn()

    def put_connection(self, conn):
        """Put the connection to the pool."""
        self.pool.putconn(conn)

    def execute_query(self, query: str, params: Optional[tuple] = None) -> None:
        """
        Execute a query without returning data.

        Args:
            query (str): SQL query string.
            params (Optional[tuple]): Parameters for the query.
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
        finally:
            self.put_connection(conn)

    def fetch_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """
        Execute a query and return the results.

        Args:
            query (str): SQL query string.
            params (Optional[tuple]): Parameters for the query.

        Returns:
            List[Dict]: Query results as a list of dictionaries.
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        finally:
            self.put_connection(conn)

    def create_user(self, telegram_id: int, username: Optional[str]) -> None:
        """Create a user if they don't already exist."""
        self.execute_query(
            """
            INSERT INTO users (telegram_id, username)
            VALUES (%s, %s)
            ON CONFLICT (telegram_id) DO NOTHING;
            """,
            (telegram_id, username),
        )

    def add_reminder(self, telegram_id: int, description: str, reminder_time: str) -> None:
        """Add a new reminder."""
        self.execute_query(
            """
            INSERT INTO reminders (user_id, description, reminder_time)
            VALUES (%s, %s, %s);
            """,
            (telegram_id, description, reminder_time),
        )

    def get_due_reminders(self) -> List[Dict]:
        """Get reminders that are due for notification."""
        return self.fetch_query(
            """
            SELECT r.id, r.description, r.reminder_time, u.telegram_id
            FROM reminders r
            JOIN users u ON r.user_id = u.telegram_id
            WHERE r.notified = FALSE AND r.reminder_time <= NOW();
            """
        )

    def mark_reminder_as_notified(self, reminder_id: int) -> None:
        """Mark a reminder as notified."""
        self.execute_query(
            """
            UPDATE reminders
            SET notified = TRUE
            WHERE id = %s;
            """,
            (reminder_id,),
        )

    def get_user_reminders(self, telegram_id: int) -> List[Dict]:
        """Get all reminders for a specific user."""
        return self.fetch_query(
            """
            SELECT id, description, reminder_time, notified
            FROM reminders
            WHERE user_id = %s
            ORDER BY reminder_time ASC;
            """,
            (telegram_id,),
        )

    def delete_reminder(self, reminder_id: int, telegram_id: int) -> bool:
        """Delete a specific reminder."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM reminders
                    WHERE id = %s AND user_id = %s;
                    """,
                    (reminder_id, telegram_id),
                )
                return cursor.rowcount > 0
        finally:
            self.put_connection(conn)