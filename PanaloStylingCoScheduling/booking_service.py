from datetime import date, datetime, timedelta

from db import Database


class BookingService:
    def __init__(self, db: Database):
        self.db = db

    def parse_event_date(self, event_date: str):
        event_date = event_date.strip()

        if not event_date:
            raise ValueError("Event date is required.")

        try:
            return datetime.strptime(event_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Event date must follow YYYY-MM-DD format.")

    def validate_booking_date_and_time(self, event_date: str, event_time: str):
        parsed_date = self.parse_event_date(event_date)

        if not event_time.strip():
            raise ValueError("Event time is required.")

        minimum_date = date.today() + timedelta(days=3)

        if parsed_date < minimum_date:
            raise ValueError(
                f"Booking must be scheduled at least 3 days from today. "
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

    def ensure_client_not_already_booked(self, conn, client_id: int, current_booking_id: int | None = None):
        cancelled_status_id = self.get_cancelled_status_id(conn)

        query = """
            SELECT id
            FROM bookings
            WHERE client_id = ?
        """

        params = [client_id]

        if cancelled_status_id:
            query += " AND status_id != ?"
            params.append(cancelled_status_id)

        if current_booking_id:
            query += " AND id != ?"
            params.append(current_booking_id)

        query += " LIMIT 1"

        existing = conn.execute(query, params).fetchone()

        if existing:
            raise ValueError(
                "This client already has an active booking. Cancel the existing booking first before creating another one."
            )

    def ensure_no_booking_conflict(self, conn, event_date: str, current_booking_id: int | None = None):
        cancelled_status_id = self.get_cancelled_status_id(conn)

        query = """
            SELECT id
            FROM bookings
            WHERE event_date = ?
        """

        params = [event_date.strip()]

        if cancelled_status_id:
            query += " AND status_id != ?"
            params.append(cancelled_status_id)

        if current_booking_id:
            query += " AND id != ?"
            params.append(current_booking_id)

        query += " LIMIT 1"

        existing = conn.execute(query, params).fetchone()

        if existing:
            raise ValueError(
                "This date already has a booked client. For now, only one client can be scheduled per day."
            )

    def list_bookings(self, search_text: str = ""):
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
                        b.total_amount,
                        b.down_payment_amount,
                        b.balance_amount,
                        b.created_at
                    FROM bookings b
                    LEFT JOIN clients c ON b.client_id = c.id
                    LEFT JOIN packages p ON b.package_id = p.id
                    LEFT JOIN event_types et ON b.event_type_id = et.id
                    LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                    WHERE
                        c.full_name LIKE ?
                        OR p.package_name LIKE ?
                        OR et.name LIKE ?
                        OR bs.name LIKE ?
                        OR b.event_location LIKE ?
                    ORDER BY b.id DESC
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
                        b.total_amount,
                        b.down_payment_amount,
                        b.balance_amount,
                        b.created_at
                    FROM bookings b
                    LEFT JOIN clients c ON b.client_id = c.id
                    LEFT JOIN packages p ON b.package_id = p.id
                    LEFT JOIN event_types et ON b.event_type_id = et.id
                    LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                    ORDER BY b.id DESC
                    """
                ).fetchall()

        return [dict(row) for row in rows]

    def get_booking_by_id(self, booking_id: int):
        with self.db.get_conn() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM bookings
                WHERE id = ?
                """,
                (booking_id,)
            ).fetchone()

        return dict(row) if row else None

    def add_booking(
        self,
        client_id: int,
        package_id: int | None,
        event_type_id: int | None,
        status_id: int | None,
        event_date: str,
        event_time: str,
        event_location: str,
        guest_count: int | None,
        theme_motif: str,
        total_amount: float,
        down_payment_amount: float,
        booking_notes: str,
        created_by: int
    ):
        if not client_id:
            raise ValueError("Client is required.")

        if total_amount < 0:
            raise ValueError("Total amount cannot be negative.")

        if down_payment_amount < 0:
            raise ValueError("Down payment cannot be negative.")

        if down_payment_amount > total_amount:
            raise ValueError("Down payment cannot be greater than total amount.")

        if guest_count is not None and guest_count < 0:
            raise ValueError("Guest count cannot be negative.")

        self.validate_booking_date_and_time(event_date, event_time)

        balance_amount = total_amount - down_payment_amount

        with self.db.get_conn() as conn:
            self.ensure_client_not_already_booked(conn, client_id)
            self.ensure_no_booking_conflict(conn, event_date)

            cur = conn.execute(
                """
                INSERT INTO bookings (
                    client_id,
                    package_id,
                    event_type_id,
                    status_id,
                    event_date,
                    event_time,
                    event_location,
                    guest_count,
                    theme_motif,
                    total_amount,
                    down_payment_amount,
                    balance_amount,
                    booking_notes,
                    created_by
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    client_id,
                    package_id,
                    event_type_id,
                    status_id,
                    event_date.strip(),
                    event_time.strip(),
                    event_location.strip(),
                    guest_count,
                    theme_motif.strip(),
                    total_amount,
                    down_payment_amount,
                    balance_amount,
                    booking_notes.strip(),
                    created_by
                )
            )

            booking_id = cur.lastrowid

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (
                    created_by,
                    "ADD_BOOKING",
                    f"Added booking ID {booking_id}"
                )
            )

    def update_booking(
        self,
        booking_id: int,
        client_id: int,
        package_id: int | None,
        event_type_id: int | None,
        status_id: int | None,
        event_date: str,
        event_time: str,
        event_location: str,
        guest_count: int | None,
        theme_motif: str,
        total_amount: float,
        down_payment_amount: float,
        booking_notes: str,
        actor_id: int
    ):
        if not client_id:
            raise ValueError("Client is required.")

        if total_amount < 0:
            raise ValueError("Total amount cannot be negative.")

        if down_payment_amount < 0:
            raise ValueError("Down payment cannot be negative.")

        if down_payment_amount > total_amount:
            raise ValueError("Down payment cannot be greater than total amount.")

        if guest_count is not None and guest_count < 0:
            raise ValueError("Guest count cannot be negative.")

        self.validate_booking_date_and_time(event_date, event_time)

        balance_amount = total_amount - down_payment_amount

        with self.db.get_conn() as conn:
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

            self.ensure_client_not_already_booked(
                conn,
                client_id,
                current_booking_id=booking_id
            )

            self.ensure_no_booking_conflict(
                conn,
                event_date,
                current_booking_id=booking_id
            )

            conn.execute(
                """
                UPDATE bookings
                SET
                    client_id = ?,
                    package_id = ?,
                    event_type_id = ?,
                    status_id = ?,
                    event_date = ?,
                    event_time = ?,
                    event_location = ?,
                    guest_count = ?,
                    theme_motif = ?,
                    total_amount = ?,
                    down_payment_amount = ?,
                    balance_amount = ?,
                    booking_notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    client_id,
                    package_id,
                    event_type_id,
                    status_id,
                    event_date.strip(),
                    event_time.strip(),
                    event_location.strip(),
                    guest_count,
                    theme_motif.strip(),
                    total_amount,
                    down_payment_amount,
                    balance_amount,
                    booking_notes.strip(),
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
                    "UPDATE_BOOKING",
                    f"Updated booking ID {booking_id}"
                )
            )