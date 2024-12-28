CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY,
    username TEXT
);

CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id),
    description TEXT NOT NULL,
    reminder_time TIMESTAMP WITH TIME ZONE NOT NULL,
    notified BOOLEAN DEFAULT FALSE
);
