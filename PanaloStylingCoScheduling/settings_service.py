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
    "cancellation_policy": "Payments made are non-refundable."
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

    def list_event_types(self):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT id, name, is_active, created_at
                FROM event_types
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
            conn.execute(
                """
                DELETE FROM event_types
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
                    (actor_id, "DELETE_EVENT_TYPE", f"Deleted event type ID {event_type_id}")
                )

    def list_booking_statuses(self):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT id, name, is_active, created_at
                FROM booking_statuses
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
            conn.execute(
                """
                DELETE FROM booking_statuses
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
                    (actor_id, "DELETE_BOOKING_STATUS", f"Deleted booking status ID {status_id}")
                )