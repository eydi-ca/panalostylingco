from datetime import date, datetime, timedelta

from db import Database


class ScheduleService:
    def __init__(self, db: Database):
        self.db = db

    def list_schedules_for_month(self, year: int, month: int):
        month_text = f"{year:04d}-{month:02d}-%"

        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT
                    b.id,
                    c.full_name AS client_name,
                    p.package_name,
                    et.name AS event_type,
                    bs.name AS status,
                    b.event_date,
                    b.event_time,
                    b.event_location,
                    b.guest_count,
                    b.theme_motif,
                    b.total_amount,
                    b.down_payment_amount,
                    b.balance_amount,
                    b.booking_notes
                FROM bookings b
                LEFT JOIN clients c ON b.client_id = c.id
                LEFT JOIN packages p ON b.package_id = p.id
                LEFT JOIN event_types et ON b.event_type_id = et.id
                LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                WHERE b.event_date LIKE ?
                ORDER BY b.event_date ASC, b.event_time ASC
                """,
                (month_text,)
            ).fetchall()

        return [dict(row) for row in rows]

    def parse_event_date(self, event_date: str):
        event_date = event_date.strip()

        if not event_date:
            raise ValueError("New event date is required.")

        try:
            return datetime.strptime(event_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Event date must follow YYYY-MM-DD format.")

    def validate_reschedule_date_and_time(self, event_date: str, event_time: str):
        parsed_date = self.parse_event_date(event_date)

        if not event_time.strip():
            raise ValueError("Event time is required.")

        minimum_date = date.today() + timedelta(days=3)

        if parsed_date < minimum_date:
            raise ValueError(
                f"Schedule must be at least 3 days from today. "
                f"Earliest allowed date is {minimum_date.strftime('%Y-%m-%d')}."
            )

    def get_cancelled_status_id(self, conn):
        row = conn.execute(
            """
            SELECT id
            FROM booking_statuses
            WHERE LOWER(name) = 'cancelled'
            LIMIT 1
            """
        ).fetchone()

        return row["id"] if row else None

    def ensure_no_schedule_conflict(self, conn, event_date: str, current_booking_id: int):
        cancelled_status_id = self.get_cancelled_status_id(conn)

        query = """
            SELECT id
            FROM bookings
            WHERE event_date = ?
              AND id != ?
        """

        params = [
            event_date.strip(),
            current_booking_id
        ]

        if cancelled_status_id:
            query += " AND status_id != ?"
            params.append(cancelled_status_id)

        query += " LIMIT 1"

        existing = conn.execute(query, params).fetchone()

        if existing:
            raise ValueError(
                "This date already has a booked client. For now, only one client can be scheduled per day."
            )

    def list_schedules_for_date(self, event_date: str):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT
                    b.id,
                    c.full_name AS client_name,
                    p.package_name,
                    et.name AS event_type,
                    bs.name AS status,
                    b.event_date,
                    b.event_time,
                    b.event_location,
                    b.guest_count,
                    b.theme_motif,
                    b.total_amount,
                    b.down_payment_amount,
                    b.balance_amount,
                    b.booking_notes
                FROM bookings b
                LEFT JOIN clients c ON b.client_id = c.id
                LEFT JOIN packages p ON b.package_id = p.id
                LEFT JOIN event_types et ON b.event_type_id = et.id
                LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                WHERE b.event_date = ?
                ORDER BY b.event_time ASC
                """,
                (event_date,)
            ).fetchall()

        return [dict(row) for row in rows]

    def list_all_schedules(self, search_text: str = ""):
        search_text = search_text.strip()

        with self.db.get_conn() as conn:
            if search_text:
                rows = conn.execute(
                    """
                    SELECT
                        b.id,
                        c.full_name AS client_name,
                        p.package_name,
                        et.name AS event_type,
                        bs.name AS status,
                        b.event_date,
                        b.event_time,
                        b.event_location,
                        b.guest_count,
                        b.theme_motif,
                        b.total_amount,
                        b.balance_amount,
                        b.booking_notes
                    FROM bookings b
                    LEFT JOIN clients c ON b.client_id = c.id
                    LEFT JOIN packages p ON b.package_id = p.id
                    LEFT JOIN event_types et ON b.event_type_id = et.id
                    LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                    WHERE
                        b.event_date IS NOT NULL
                        AND b.event_date != ''
                        AND (
                            c.full_name LIKE ?
                            OR p.package_name LIKE ?
                            OR et.name LIKE ?
                            OR bs.name LIKE ?
                            OR b.event_location LIKE ?
                        )
                    ORDER BY b.event_date ASC, b.event_time ASC
                    """,
                    (
                        f"%{search_text}%",
                        f"%{search_text}%",
                        f"%{search_text}%",
                        f"%{search_text}%",
                        f"%{search_text}%",
                    )
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT
                        b.id,
                        c.full_name AS client_name,
                        p.package_name,
                        et.name AS event_type,
                        bs.name AS status,
                        b.event_date,
                        b.event_time,
                        b.event_location,
                        b.guest_count,
                        b.theme_motif,
                        b.total_amount,
                        b.balance_amount,
                        b.booking_notes
                    FROM bookings b
                    LEFT JOIN clients c ON b.client_id = c.id
                    LEFT JOIN packages p ON b.package_id = p.id
                    LEFT JOIN event_types et ON b.event_type_id = et.id
                    LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                    WHERE b.event_date IS NOT NULL
                      AND b.event_date != ''
                    ORDER BY b.event_date ASC, b.event_time ASC
                    """
                ).fetchall()

        return [dict(row) for row in rows]

    def get_schedule_by_booking_id(self, booking_id: int):
        with self.db.get_conn() as conn:
            row = conn.execute(
                """
                SELECT
                    b.id,
                    c.full_name AS client_name,
                    p.package_name,
                    et.name AS event_type,
                    bs.name AS status,
                    b.event_date,
                    b.event_time,
                    b.event_location,
                    b.guest_count,
                    b.theme_motif,
                    b.total_amount,
                    b.down_payment_amount,
                    b.balance_amount,
                    b.booking_notes
                FROM bookings b
                LEFT JOIN clients c ON b.client_id = c.id
                LEFT JOIN packages p ON b.package_id = p.id
                LEFT JOIN event_types et ON b.event_type_id = et.id
                LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                WHERE b.id = ?
                """,
                (booking_id,)
            ).fetchone()

        return dict(row) if row else None

    def reschedule_booking(self, booking_id: int, new_event_date: str, new_event_time: str, actor_id: int):
        new_event_date = new_event_date.strip()
        new_event_time = new_event_time.strip()

        self.validate_reschedule_date_and_time(new_event_date, new_event_time)

        with self.db.get_conn() as conn:
            existing = conn.execute(
                """
                SELECT id, reschedule_count
                FROM bookings
                WHERE id = ?
                """,
                (booking_id,)
            ).fetchone()

            if not existing:
                raise ValueError("Booking not found.")

            settings_rows = conn.execute(
                """
                SELECT setting_key, setting_value
                FROM system_settings
                WHERE setting_key IN ('allow_reschedule', 'max_reschedule_count')
                """
            ).fetchall()

            settings = {
                row["setting_key"]: row["setting_value"]
                for row in settings_rows
            }

            allow_reschedule = settings.get("allow_reschedule", "Yes")

            if allow_reschedule != "Yes":
                raise ValueError("Rescheduling is currently not allowed by system settings.")

            max_reschedule_count = int(settings.get("max_reschedule_count", "1"))
            current_count = int(existing["reschedule_count"] or 0)

            if current_count >= max_reschedule_count:
                raise ValueError(
                    f"This booking already reached the maximum reschedule count of {max_reschedule_count}."
                )

            self.ensure_no_schedule_conflict(
                conn,
                new_event_date,
                current_booking_id=booking_id
            )

            conn.execute(
                """
                UPDATE bookings
                SET event_date = ?,
                    event_time = ?,
                    reschedule_count = reschedule_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    new_event_date,
                    new_event_time,
                    booking_id
                )
            )

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (
                    actor_id,
                    "RESCHEDULE_BOOKING",
                    f"Rescheduled booking ID {booking_id} to {new_event_date} {new_event_time}"
                )
            )

    def cancel_schedule(self, booking_id: int, actor_id: int):
        with self.db.get_conn() as conn:
            cancelled_status = conn.execute(
                """
                SELECT id
                FROM booking_statuses
                WHERE LOWER(name) = 'cancelled'
                LIMIT 1
                """
            ).fetchone()

            if not cancelled_status:
                raise ValueError("Cancelled status does not exist in Booking Statuses settings.")

            existing = conn.execute(
                """
                SELECT id
                FROM bookings
                WHERE id = ?
                """,
                (booking_id,)
            ).fetchone()

            if not existing:
                raise ValueError("Booking not found.")

            conn.execute(
                """
                UPDATE bookings
                SET status_id = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    cancelled_status["id"],
                    booking_id
                )
            )

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (
                    actor_id,
                    "CANCEL_SCHEDULE",
                    f"Cancelled schedule for booking ID {booking_id}"
                )
            )