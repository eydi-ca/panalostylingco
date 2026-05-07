from db import Database


class BookingService:
    def __init__(self, db: Database):
        self.db = db

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

        balance_amount = total_amount - down_payment_amount

        with self.db.get_conn() as conn:
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