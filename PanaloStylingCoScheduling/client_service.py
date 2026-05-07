from datetime import datetime

from db import Database


class ClientService:
    def __init__(self, db: Database):
        self.db = db

    def validate_client_details(self, full_name: str):
        if not full_name.strip():
            raise ValueError("Client full name is required.")


    def list_clients(self, search_text: str = ""):
        search_text = search_text.strip()

        with self.db.get_conn() as conn:
            if search_text:
                rows = conn.execute(
                    """
                    SELECT 
                        id,
                        full_name,
                        contact_number,
                        notes,
                        created_at
                    FROM clients
                    WHERE 
                        full_name LIKE ?
                        OR contact_number LIKE ?
                        OR notes LIKE ?
                    ORDER BY id DESC
                    """,
                    (
                        f"%{search_text}%",
                        f"%{search_text}%",
                        f"%{search_text}%",
                    )
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT 
                        id,
                        full_name,
                        contact_number,
                        notes,
                        created_at
                    FROM clients
                    ORDER BY id DESC
                    """
                ).fetchall()

        return [dict(row) for row in rows]

    def list_clients_available_for_booking(self, exclude_booking_id: int | None = None):
        with self.db.get_conn() as conn:
            cancelled_status = conn.execute(
                """
                SELECT id
                FROM booking_statuses
                WHERE LOWER(name) = 'cancelled'
                LIMIT 1
                """
            ).fetchone()

            cancelled_status_id = cancelled_status["id"] if cancelled_status else None

            query = """
                SELECT 
                    c.id,
                    c.full_name,
                    c.contact_number,
                    c.notes,
                    c.created_at
                FROM clients c
                WHERE c.id NOT IN (
                    SELECT b.client_id
                    FROM bookings b
                    WHERE b.client_id IS NOT NULL
            """

            params = []

            if cancelled_status_id:
                query += " AND b.status_id != ?"
                params.append(cancelled_status_id)

            if exclude_booking_id:
                query += " AND b.id != ?"
                params.append(exclude_booking_id)

            query += """
                )
                ORDER BY c.full_name ASC
            """

            rows = conn.execute(query, params).fetchall()

        return [dict(row) for row in rows]

    def get_client_by_id(self, client_id: int):
        with self.db.get_conn() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM clients
                WHERE id = ?
                """,
                (client_id,)
            ).fetchone()

        return dict(row) if row else None

    def add_client(
        self,
        full_name: str,
        contact_number: str,
        event_type_id: int | None,
        event_date: str,
        event_location: str,
        guest_count: int | None,
        theme_motif: str,
        preferred_package: str,
        status_id: int | None,
        notes: str,
        created_by: int
    ):
        full_name = full_name.strip()

        self.validate_client_details(full_name)

        if guest_count is not None and guest_count < 0:
            raise ValueError("Guest count cannot be negative.")

        with self.db.get_conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO clients (
                    full_name,
                    contact_number,
                    event_type_id,
                    event_date,
                    event_location,
                    guest_count,
                    theme_motif,
                    preferred_package,
                    status_id,
                    notes,
                    created_by
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    full_name,
                    contact_number.strip(),
                    event_type_id,
                    event_date.strip(),
                    event_location.strip(),
                    guest_count,
                    theme_motif.strip(),
                    preferred_package.strip(),
                    status_id,
                    notes.strip(),
                    created_by
                )
            )

            client_id = cur.lastrowid

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (
                    created_by,
                    "ADD_CLIENT",
                    f"Added client ID {client_id}: {full_name}"
                )
            )

    def update_client(
        self,
        client_id: int,
        full_name: str,
        contact_number: str,
        event_type_id: int | None,
        event_date: str,
        event_location: str,
        guest_count: int | None,
        theme_motif: str,
        preferred_package: str,
        status_id: int | None,
        notes: str,
        actor_id: int
    ):
        full_name = full_name.strip()

        self.validate_client_details(
            full_name,
            event_date,
            event_location
        )

        if guest_count is not None and guest_count < 0:
            raise ValueError("Guest count cannot be negative.")

        with self.db.get_conn() as conn:
            existing = conn.execute(
                """
                SELECT id
                FROM clients
                WHERE id = ?
                """,
                (client_id,)
            ).fetchone()

            if not existing:
                raise ValueError("Client not found.")

            conn.execute(
                """
                UPDATE clients
                SET 
                    full_name = ?,
                    contact_number = ?,
                    event_type_id = ?,
                    event_date = ?,
                    event_location = ?,
                    guest_count = ?,
                    theme_motif = ?,
                    preferred_package = ?,
                    status_id = ?,
                    notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    full_name,
                    contact_number.strip(),
                    event_type_id,
                    event_date.strip(),
                    event_location.strip(),
                    guest_count,
                    theme_motif.strip(),
                    preferred_package.strip(),
                    status_id,
                    notes.strip(),
                    client_id
                )
            )

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (
                    actor_id,
                    "UPDATE_CLIENT",
                    f"Updated client ID {client_id}: {full_name}"
                )
            )