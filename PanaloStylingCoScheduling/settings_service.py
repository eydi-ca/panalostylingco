import shutil
from datetime import datetime, timedelta
from pathlib import Path

from db import Database


DEFAULT_SETTINGS = {
    "business_name": "Panalo Styling Co.",
    "business_tagline": "Styling • Coordination • Events",
    "business_location": "Barangay Sto. Niño, Marikina City",
    "business_contact": "",
    "business_email": "",
    "facebook_page": "",
    "instagram_page": "",

    "down_payment_percentage": "50",
    "full_payment_due_days": "30",
    "payment_verification_required": "Yes",
    "refund_policy": "Down payment is non-refundable.",

    "allow_reschedule": "Yes",
    "max_reschedule_count": "1",
    "reschedule_policy": "Rescheduling may be allowed once, subject to availability.",
    "cancellation_policy": "Payments made are non-refundable.",
    "contract_policy_notes": "Booking, payment, refund, reschedule, and cancellation policies should be reflected in the client contract.",

    "backup_frequency": "Manual Only",
    "backup_location": "",
    "last_backup_at": "",
    "last_backup_file": ""
}

DEFAULT_EVENT_TYPES = [
    "Birthday",
    "Binyag / Dedication",
    "Wedding",
    "Intimate Gathering",
    "Milestone Event",
    "Other",
]


DEFAULT_BOOKING_STATUSES = [
    "Inquiry",
    "Consultation",
    "Proposal Sent",
    "Reserved",
    "Booked",
    "In Preparation",
    "Completed",
    "Cancelled",
]

CORE_BOOKING_STATUSES = {"inquiry", "booked", "completed", "cancelled"}


class SettingsService:
    def __init__(self, db: Database):
        self.db = db
        self.seed_default_settings()
        self.seed_default_event_types()
        self.seed_default_booking_statuses()

    def seed_default_settings(self):
        with self.db.get_conn() as conn:
            for key, value in DEFAULT_SETTINGS.items():
                conn.execute(
                    """
                    INSERT OR IGNORE INTO system_settings 
                    (setting_key, setting_value)
                    VALUES (?, ?)
                    """,
                    (key, value)
                )

    def get_all_settings(self) -> dict:
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT setting_key, setting_value
                FROM system_settings
                """
            ).fetchall()

        return {
            row["setting_key"]: row["setting_value"]
            for row in rows
        }

    def update_settings(self, settings: dict, actor_id: int | None = None):
        with self.db.get_conn() as conn:
            for key, value in settings.items():
                conn.execute(
                    """
                    INSERT INTO system_settings 
                    (setting_key, setting_value)
                    VALUES (?, ?)
                    ON CONFLICT(setting_key)
                    DO UPDATE SET 
                        setting_value = excluded.setting_value,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (key, str(value))
                )

            if actor_id:
                conn.execute(
                    """
                    INSERT INTO audit_logs 
                    (user_id, action, details)
                    VALUES (?, ?, ?)
                    """,
                    (
                        actor_id,
                        "UPDATE_SETTINGS",
                        "Updated system settings"
                    )
                )

    def seed_default_event_types(self):
        with self.db.get_conn() as conn:
            for name in DEFAULT_EVENT_TYPES:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO event_types (name, is_active)
                    VALUES (?, 1)
                    """,
                    (name,)
                )

    def seed_default_booking_statuses(self):
        with self.db.get_conn() as conn:
            for name in DEFAULT_BOOKING_STATUSES:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO booking_statuses (name, is_active)
                    VALUES (?, 1)
                    """,
                    (name,)
                )

    def list_event_types(self, active_only: bool = True):
        with self.db.get_conn() as conn:
            where_clause = "WHERE is_active = 1" if active_only else ""
            rows = conn.execute(
                f"""
                SELECT id, name, is_active, created_at
                FROM event_types
                {where_clause}
                ORDER BY name ASC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def add_event_type(self, name: str, actor_id: int | None = None):
        name = name.strip()

        if not name:
            raise ValueError("Event type name is required.")

        try:
            with self.db.get_conn() as conn:
                existing = conn.execute(
                    """
                    SELECT id, is_active
                    FROM event_types
                    WHERE name = ?
                    """,
                    (name,)
                ).fetchone()

                if existing:
                    if existing["is_active"] == 1:
                        raise ValueError("Event type already exists.")

                    conn.execute(
                        """
                        UPDATE event_types
                        SET is_active = 1
                        WHERE id = ?
                        """,
                        (existing["id"],)
                    )

                    if actor_id:
                        conn.execute(
                            """
                            INSERT INTO audit_logs (user_id, action, details)
                            VALUES (?, ?, ?)
                            """,
                            (actor_id, "RESTORE_EVENT_TYPE", f"Restored event type: {name}")
                        )
                    return

                conn.execute(
                    """
                    INSERT INTO event_types (name, is_active)
                    VALUES (?, 1)
                    """,
                    (name,)
                )

                if actor_id:
                    conn.execute(
                        """
                        INSERT INTO audit_logs (user_id, action, details)
                        VALUES (?, ?, ?)
                        """,
                        (actor_id, "ADD_EVENT_TYPE", f"Added event type: {name}")
                    )

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Event type already exists.")
            raise

    def update_event_type(self, event_type_id: int, name: str, actor_id: int | None = None):
        name = name.strip()

        if not name:
            raise ValueError("Event type name is required.")

        try:
            with self.db.get_conn() as conn:
                conn.execute(
                    """
                    UPDATE event_types
                    SET name = ?
                    WHERE id = ?
                    """,
                    (name, event_type_id)
                )

                if actor_id:
                    conn.execute(
                        """
                        INSERT INTO audit_logs (user_id, action, details)
                        VALUES (?, ?, ?)
                        """,
                        (actor_id, "UPDATE_EVENT_TYPE", f"Updated event type ID {event_type_id}")
                    )

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Event type already exists.")
            raise

    def delete_event_type(self, event_type_id: int, actor_id: int | None = None):
        with self.db.get_conn() as conn:
            existing = conn.execute(
                """
                SELECT id, name
                FROM event_types
                WHERE id = ?
                """,
                (event_type_id,)
            ).fetchone()

            if not existing:
                raise ValueError("Event type not found.")

            conn.execute(
                """
                UPDATE event_types
                SET is_active = 0
                WHERE id = ?
                """,
                (event_type_id,)
            )

            if actor_id:
                conn.execute(
                    """
                    INSERT INTO audit_logs (user_id, action, details)
                    VALUES (?, ?, ?)
                    """,
                    (actor_id, "DISABLE_EVENT_TYPE", f"Disabled event type: {existing['name']}")
                )

    def list_booking_statuses(self, active_only: bool = True):
        with self.db.get_conn() as conn:
            where_clause = "WHERE is_active = 1" if active_only else ""
            rows = conn.execute(
                f"""
                SELECT id, name, is_active, created_at
                FROM booking_statuses
                {where_clause}
                ORDER BY id ASC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def add_booking_status(self, name: str, actor_id: int | None = None):
        name = name.strip()

        if not name:
            raise ValueError("Booking status name is required.")

        try:
            with self.db.get_conn() as conn:
                existing = conn.execute(
                    """
                    SELECT id, is_active
                    FROM booking_statuses
                    WHERE name = ?
                    """,
                    (name,)
                ).fetchone()

                if existing:
                    if existing["is_active"] == 1:
                        raise ValueError("Booking status already exists.")

                    conn.execute(
                        """
                        UPDATE booking_statuses
                        SET is_active = 1
                        WHERE id = ?
                        """,
                        (existing["id"],)
                    )

                    if actor_id:
                        conn.execute(
                            """
                            INSERT INTO audit_logs (user_id, action, details)
                            VALUES (?, ?, ?)
                            """,
                            (actor_id, "RESTORE_BOOKING_STATUS", f"Restored booking status: {name}")
                        )
                    return

                conn.execute(
                    """
                    INSERT INTO booking_statuses (name, is_active)
                    VALUES (?, 1)
                    """,
                    (name,)
                )

                if actor_id:
                    conn.execute(
                        """
                        INSERT INTO audit_logs (user_id, action, details)
                        VALUES (?, ?, ?)
                        """,
                        (actor_id, "ADD_BOOKING_STATUS", f"Added booking status: {name}")
                    )

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Booking status already exists.")
            raise

    def update_booking_status(self, status_id: int, name: str, actor_id: int | None = None):
        name = name.strip()

        if not name:
            raise ValueError("Booking status name is required.")

        try:
            with self.db.get_conn() as conn:
                existing = conn.execute(
                    """
                    SELECT name
                    FROM booking_statuses
                    WHERE id = ?
                    """,
                    (status_id,)
                ).fetchone()

                if not existing:
                    raise ValueError("Booking status not found.")

                if existing["name"].lower() in CORE_BOOKING_STATUSES and name.lower() != existing["name"].lower():
                    raise ValueError("This booking status is required by the system and cannot be renamed.")

                conn.execute(
                    """
                    UPDATE booking_statuses
                    SET name = ?
                    WHERE id = ?
                    """,
                    (name, status_id)
                )

                if actor_id:
                    conn.execute(
                        """
                        INSERT INTO audit_logs (user_id, action, details)
                        VALUES (?, ?, ?)
                        """,
                        (actor_id, "UPDATE_BOOKING_STATUS", f"Updated booking status ID {status_id}")
                    )

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Booking status already exists.")
            raise

    def delete_booking_status(self, status_id: int, actor_id: int | None = None):
        with self.db.get_conn() as conn:
            existing = conn.execute(
                """
                SELECT name
                FROM booking_statuses
                WHERE id = ?
                """,
                (status_id,)
            ).fetchone()

            if not existing:
                raise ValueError("Booking status not found.")

            if existing["name"].lower() in CORE_BOOKING_STATUSES:
                raise ValueError("This booking status is required by the system and cannot be deleted.")

            conn.execute(
                """
                UPDATE booking_statuses
                SET is_active = 0
                WHERE id = ?
                """,
                (status_id,)
            )

            if actor_id:
                conn.execute(
                    """
                    INSERT INTO audit_logs (user_id, action, details)
                    VALUES (?, ?, ?)
                    """,
                    (actor_id, "DISABLE_BOOKING_STATUS", f"Disabled booking status: {existing['name']}")
                )

    def get_backup_directory(self, settings: dict | None = None) -> Path:
        if settings is None:
            settings = self.get_all_settings()

        location = (settings.get("backup_location") or "").strip()

        if location:
            backup_dir = Path(location)
        else:
            backup_dir = Path(self.db.db_path).resolve().parent / "backups"

        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    def create_database_backup(self, actor_id: int | None = None, reason: str = "Manual") -> Path:
        settings = self.get_all_settings()
        backup_dir = self.get_backup_directory(settings)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"panalo_styling_backup_{timestamp}.db"

        shutil.copy2(self.db.db_path, backup_file)

        with self.db.get_conn() as conn:
            for key, value in {
                "last_backup_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_backup_file": str(backup_file)
            }.items():
                conn.execute(
                    """
                    INSERT INTO system_settings
                    (setting_key, setting_value)
                    VALUES (?, ?)
                    ON CONFLICT(setting_key)
                    DO UPDATE SET
                        setting_value = excluded.setting_value,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (key, value)
                )

            if actor_id:
                conn.execute(
                    """
                    INSERT INTO audit_logs
                    (user_id, action, details)
                    VALUES (?, ?, ?)
                    """,
                    (
                        actor_id,
                        "CREATE_DATABASE_BACKUP",
                        f"{reason} database backup created: {backup_file}"
                    )
                )

        return backup_file

    def list_database_backups(self):
        backup_dir = self.get_backup_directory()

        backups = []
        for backup_file in backup_dir.glob("*.db"):
            stat = backup_file.stat()
            backups.append({
                "file_name": backup_file.name,
                "file_path": str(backup_file),
                "size_kb": round(stat.st_size / 1024, 1),
                "created_at": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })

        return sorted(backups, key=lambda item: item["created_at"], reverse=True)

    def restore_database_backup(self, backup_file: str, actor_id: int | None = None) -> Path:
        backup_path = Path(backup_file)

        if not backup_path.exists() or backup_path.suffix.lower() != ".db":
            raise ValueError("Selected backup file is not valid.")

        safety_backup = self.create_database_backup(actor_id=actor_id, reason="Before restore")
        shutil.copy2(backup_path, self.db.db_path)

        with self.db.get_conn() as conn:
            audit_user_id = actor_id

            if actor_id:
                existing_user = conn.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE id = ?
                    """,
                    (actor_id,)
                ).fetchone()

                if not existing_user:
                    audit_user_id = None

            if actor_id:
                conn.execute(
                    """
                    INSERT INTO audit_logs
                    (user_id, action, details)
                    VALUES (?, ?, ?)
                    """,
                    (
                        audit_user_id,
                        "RESTORE_DATABASE_BACKUP",
                        f"Restored database backup: {backup_path}; safety backup: {safety_backup}"
                    )
                )

        return safety_backup

    def create_auto_backup_if_due(self):
        settings = self.get_all_settings()
        frequency = settings.get("backup_frequency", "Manual Only")

        if frequency == "Manual Only":
            return None

        last_backup_at = settings.get("last_backup_at", "")
        if not last_backup_at:
            return self.create_database_backup(reason="Automatic")

        try:
            last_backup = datetime.strptime(last_backup_at, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return self.create_database_backup(reason="Automatic")

        due_after = timedelta(days=1 if frequency == "Daily" else 7)

        if datetime.now() - last_backup >= due_after:
            return self.create_database_backup(reason="Automatic")

        return None
