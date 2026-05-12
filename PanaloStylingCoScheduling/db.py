import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


DB_FOLDER = Path(__file__).resolve().parent / "data"
DB_PATH = DB_FOLDER / "panalo_styling.db"


class Database:
    def __init__(self):
        DB_FOLDER.mkdir(exist_ok=True)
        self.db_path = DB_PATH
        self.initialize_database()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @contextmanager
    def get_conn(self) -> Iterator[sqlite3.Connection]:
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_database(self):
        with self.get_conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    username TEXT UNIQUE,
                    email TEXT,
                    phone_number TEXT,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('ADMIN', 'STAFF')),
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS user_module_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    module_name TEXT NOT NULL,
                    is_allowed INTEGER NOT NULL CHECK(is_allowed IN (0, 1)),
                    UNIQUE(user_id, module_name),
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
                
                CREATE TABLE IF NOT EXISTS system_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT NOT NULL UNIQUE,
                    setting_value TEXT,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS event_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS booking_statuses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    contact_number TEXT,
                    event_type_id INTEGER,
                    event_date TEXT,
                    event_location TEXT,
                    guest_count INTEGER,
                    theme_motif TEXT,
                    preferred_package TEXT,
                    status_id INTEGER,
                    notes TEXT,
                    created_by INTEGER,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(event_type_id) REFERENCES event_types(id),
                    FOREIGN KEY(status_id) REFERENCES booking_statuses(id),
                    FOREIGN KEY(created_by) REFERENCES users(id)
                );
                
                CREATE TABLE IF NOT EXISTS packages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    package_name TEXT NOT NULL UNIQUE,
                    recommended_pax TEXT,
                    description TEXT,
                    inclusions TEXT,
                    min_price REAL,
                    max_price REAL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_by INTEGER,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(created_by) REFERENCES users(id)
                );
                
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    package_id INTEGER,
                    event_type_id INTEGER,
                    status_id INTEGER,
                    event_date TEXT,
                    event_time TEXT,
                    event_location TEXT,
                    guest_count INTEGER,
                    theme_motif TEXT,
                    total_amount REAL DEFAULT 0,
                    down_payment_amount REAL DEFAULT 0,
                    balance_amount REAL DEFAULT 0,
                    booking_notes TEXT,
                    created_by INTEGER,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(client_id) REFERENCES clients(id),
                    FOREIGN KEY(package_id) REFERENCES packages(id),
                    FOREIGN KEY(event_type_id) REFERENCES event_types(id),
                    FOREIGN KEY(status_id) REFERENCES booking_statuses(id),
                    FOREIGN KEY(created_by) REFERENCES users(id)
                );
                
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_id INTEGER NOT NULL,
                    payment_type TEXT NOT NULL CHECK(payment_type IN ('Down Payment', 'Partial Payment', 'Full Payment', 'Refund')),
                    amount REAL NOT NULL,
                    payment_method TEXT,
                    reference_number TEXT,
                    payment_date TEXT,
                    verification_status TEXT NOT NULL DEFAULT 'Pending' CHECK(verification_status IN ('Pending', 'Verified', 'Rejected')),
                    verified_by INTEGER,
                    verified_at TEXT,
                    notes TEXT,
                    created_by INTEGER,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(booking_id) REFERENCES bookings(id),
                    FOREIGN KEY(verified_by) REFERENCES users(id),
                    FOREIGN KEY(created_by) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS bypass_pins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    pin_hash TEXT NOT NULL,
                    pin_salt TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                """

            )

            columns = conn.execute("PRAGMA table_info(users)").fetchall()
            column_names = [column["name"] for column in columns]

            columns = conn.execute("PRAGMA table_info(bookings)").fetchall()
            booking_column_names = [column["name"] for column in columns]

            if "reschedule_count" not in booking_column_names:
                conn.execute(
                    "ALTER TABLE bookings ADD COLUMN reschedule_count INTEGER NOT NULL DEFAULT 0"
                )

            if "username" not in column_names:
                conn.execute("ALTER TABLE users ADD COLUMN username TEXT")

            if "email" not in column_names:
                conn.execute("ALTER TABLE users ADD COLUMN email TEXT")

            if "phone_number" not in column_names:
                conn.execute("ALTER TABLE users ADD COLUMN phone_number TEXT")

            if "is_active" not in column_names:
                conn.execute("ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")

            conn.execute(
                """
                UPDATE users
                SET username = LOWER(SUBSTR(email, 1, INSTR(email, '@') - 1))
                WHERE username IS NULL
                  AND email IS NOT NULL
                  AND INSTR(email, '@') > 1
                """
            )

            conn.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username
                ON users(username)
                """
            )

