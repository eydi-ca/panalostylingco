from db import Database


class PaymentService:
    def __init__(self, db: Database):
        self.db = db

    def list_booking_payment_summaries(self, search_text: str = ""):
        search_text = search_text.strip()

        base_query = """
            SELECT
                b.id AS booking_id,
                c.full_name AS client_name,
                p.package_name,
                et.name AS event_type,
                bs.name AS booking_status,
                b.event_date,
                b.total_amount,

                COALESCE(SUM(
                    CASE 
                        WHEN pay.verification_status = 'Verified'
                         AND pay.payment_type != 'Refund'
                        THEN pay.amount
                        ELSE 0
                    END
                ), 0) AS total_paid,

                COALESCE(SUM(
                    CASE 
                        WHEN pay.verification_status = 'Verified'
                         AND pay.payment_type = 'Refund'
                        THEN pay.amount
                        ELSE 0
                    END
                ), 0) AS total_refunded

            FROM bookings b
            LEFT JOIN clients c ON b.client_id = c.id
            LEFT JOIN packages p ON b.package_id = p.id
            LEFT JOIN event_types et ON b.event_type_id = et.id
            LEFT JOIN booking_statuses bs ON b.status_id = bs.id
            LEFT JOIN payments pay ON b.id = pay.booking_id
        """

        where_clause = ""
        params = []

        if search_text:
            where_clause = """
                WHERE
                    c.full_name LIKE ?
                    OR p.package_name LIKE ?
                    OR et.name LIKE ?
                    OR bs.name LIKE ?
                    OR b.event_date LIKE ?
            """
            params = [
                f"%{search_text}%",
                f"%{search_text}%",
                f"%{search_text}%",
                f"%{search_text}%",
                f"%{search_text}%",
            ]

        group_order = """
            GROUP BY b.id
            ORDER BY b.id DESC
        """

        with self.db.get_conn() as conn:
            rows = conn.execute(
                base_query + where_clause + group_order,
                params
            ).fetchall()

        summaries = []

        for row in rows:
            item = dict(row)

            total_amount = float(item["total_amount"] or 0)
            total_paid = float(item["total_paid"] or 0)
            total_refunded = float(item["total_refunded"] or 0)

            net_paid = total_paid - total_refunded
            balance = total_amount - net_paid

            if balance <= 0 and total_amount > 0:
                payment_status = "Paid"
            elif net_paid > 0:
                payment_status = "Partial"
            else:
                payment_status = "Unpaid"

            item["net_paid"] = net_paid
            item["balance"] = balance
            item["payment_status"] = payment_status

            summaries.append(item)

        return summaries

    def get_booking_payment_summary(self, booking_id: int):
        summaries = self.list_booking_payment_summaries("")

        for summary in summaries:
            if summary["booking_id"] == booking_id:
                return summary

        return None

    def list_payments_by_booking(self, booking_id: int):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT
                    pay.id,
                    pay.booking_id,
                    pay.payment_type,
                    pay.amount,
                    pay.payment_method,
                    pay.reference_number,
                    pay.payment_date,
                    pay.verification_status,
                    verifier.full_name AS verified_by_name,
                    pay.verified_at,
                    pay.notes,
                    creator.full_name AS created_by_name,
                    pay.created_at
                FROM payments pay
                LEFT JOIN users verifier ON pay.verified_by = verifier.id
                LEFT JOIN users creator ON pay.created_by = creator.id
                WHERE pay.booking_id = ?
                ORDER BY pay.id DESC
                """,
                (booking_id,)
            ).fetchall()

        return [dict(row) for row in rows]

    def get_refundable_amount(self, conn, booking_id: int):
        totals = conn.execute(
            """
            SELECT
                COALESCE(SUM(
                    CASE
                        WHEN verification_status = 'Verified'
                         AND payment_type IN ('Pencil Booking Fee', 'Partial Payment', 'Full Payment')
                        THEN amount
                        ELSE 0
                    END
                ), 0) AS refundable_paid,

                COALESCE(SUM(
                    CASE
                        WHEN verification_status = 'Verified'
                         AND payment_type = 'Refund'
                        THEN amount
                        ELSE 0
                    END
                ), 0) AS already_refunded
            FROM payments
            WHERE booking_id = ?
            """,
            (booking_id,)
        ).fetchone()

        refundable_paid = float(totals["refundable_paid"] or 0)
        already_refunded = float(totals["already_refunded"] or 0)

        return refundable_paid - already_refunded

    def get_refundable_amount_by_booking(self, booking_id: int):
        with self.db.get_conn() as conn:
            return self.get_refundable_amount(conn, booking_id)

    def add_payment(
            self,
            booking_id,
            payment_type,
            amount,
            payment_method,
            reference_number,
            payment_date,
            notes,
            created_by,
            created_by_role=None
    ):
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        is_admin = str(created_by_role or "").upper() == "ADMIN"

        verification_status = "Verified" if is_admin else "Pending"
        verified_by = created_by if is_admin else None
        verified_at_sql = "CURRENT_TIMESTAMP" if is_admin else "NULL"

        with self.db.get_conn() as conn:
            cursor = conn.execute(
                f"""
                INSERT INTO payments (
                    booking_id,
                    payment_type,
                    amount,
                    payment_method,
                    reference_number,
                    payment_date,
                    verification_status,
                    verified_by,
                    verified_at,
                    notes,
                    created_by
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, {verified_at_sql}, ?, ?)
                """,
                (
                    booking_id,
                    payment_type,
                    amount,
                    payment_method,
                    reference_number,
                    payment_date,
                    verification_status,
                    verified_by,
                    notes,
                    created_by
                )
            )

            payment_id = cursor.lastrowid

            if is_admin:
                self.sync_booking_balance(conn, booking_id)

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (
                    created_by,
                    "ADD_PAYMENT",
                    f"Added {payment_type} payment ID {payment_id} for booking ID {booking_id}"
                )
            )

    def verify_payment(self, payment_id: int, actor_id: int):
        with self.db.get_conn() as conn:
            payment = conn.execute(
                """
                SELECT *
                FROM payments
                WHERE id = ?
                """,
                (payment_id,)
            ).fetchone()

            if not payment:
                raise ValueError("Payment not found.")

            conn.execute(
                """
                UPDATE payments
                SET verification_status = 'Verified',
                    verified_by = ?,
                    verified_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (actor_id, payment_id)
            )

            self.sync_booking_balance(conn, payment["booking_id"])

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (
                    actor_id,
                    "VERIFY_PAYMENT",
                    f"Verified payment ID {payment_id}"
                )
            )

    def list_all_payments(self, filters=None):
        filters = filters or {}

        query = """
            SELECT
                pay.id,
                pay.booking_id,
                pay.payment_type,
                pay.amount,
                pay.payment_method,
                pay.reference_number,
                pay.payment_date,
                pay.verification_status,
                pay.created_at,
                c.full_name AS client_name,
                b.event_date,
                p.package_name,
                creator.full_name AS encoded_by,
                verifier.full_name AS verified_by,

                CASE
                    WHEN COALESCE(vp.total_verified_paid, 0) >= COALESCE(b.total_amount, 0)
                        THEN 'Paid'
                    WHEN COALESCE(vp.total_verified_paid, 0) > 0
                        THEN 'Partially Paid'
                    ELSE 'Unpaid'
                END AS booking_payment_status

            FROM payments pay
            LEFT JOIN bookings b ON pay.booking_id = b.id
            LEFT JOIN clients c ON b.client_id = c.id
            LEFT JOIN packages p ON b.package_id = p.id
            LEFT JOIN users creator ON pay.created_by = creator.id
            LEFT JOIN users verifier ON pay.verified_by = verifier.id

            LEFT JOIN (
                SELECT
                    booking_id,
                    SUM(
                        CASE
                            WHEN payment_type = 'Refund' THEN -amount
                            ELSE amount
                        END
                    ) AS total_verified_paid
                FROM payments
                WHERE verification_status = 'Verified'
                GROUP BY booking_id
            ) vp ON vp.booking_id = b.id

            WHERE 1 = 1
        """

        params = []

        search = filters.get("search", "").strip()
        verification_status = filters.get("verification_status", "All")
        payment_type = filters.get("payment_type", "All")
        payment_method = filters.get("payment_method", "All")
        booking_payment_status = filters.get("booking_payment_status", "All")

        if search:
            query += """
                AND (
                    c.full_name LIKE ?
                    OR CAST(pay.booking_id AS TEXT) LIKE ?
                    OR pay.reference_number LIKE ?
                    OR pay.payment_method LIKE ?
                    OR pay.payment_type LIKE ?
                    OR creator.full_name LIKE ?
                    OR verifier.full_name LIKE ?
                )
            """
            like_search = f"%{search}%"
            params.extend([
                like_search,
                like_search,
                like_search,
                like_search,
                like_search,
                like_search,
                like_search
            ])

        if verification_status != "All":
            query += " AND pay.verification_status = ?"
            params.append(verification_status)

        if payment_type != "All":
            query += " AND pay.payment_type = ?"
            params.append(payment_type)

        if payment_method != "All":
            query += " AND pay.payment_method = ?"
            params.append(payment_method)

        if booking_payment_status != "All":
            query += """
                AND (
                    CASE
                        WHEN COALESCE(vp.total_verified_paid, 0) >= COALESCE(b.total_amount, 0)
                            THEN 'Paid'
                        WHEN COALESCE(vp.total_verified_paid, 0) > 0
                            THEN 'Partially Paid'
                        ELSE 'Unpaid'
                    END
                ) = ?
            """
            params.append(booking_payment_status)

        query += """
            ORDER BY pay.payment_date DESC, pay.id DESC
        """

        with self.db.get_conn() as conn:
            rows = conn.execute(query, params).fetchall()

        return [dict(row) for row in rows]

    def reject_payment(self, payment_id: int, actor_id: int):
        with self.db.get_conn() as conn:
            payment = conn.execute(
                """
                SELECT *
                FROM payments
                WHERE id = ?
                """,
                (payment_id,)
            ).fetchone()

            if not payment:
                raise ValueError("Payment not found.")

            conn.execute(
                """
                UPDATE payments
                SET verification_status = 'Rejected',
                    verified_by = ?,
                    verified_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (actor_id, payment_id)
            )

            self.sync_booking_balance(conn, payment["booking_id"])

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (
                    actor_id,
                    "REJECT_PAYMENT",
                    f"Rejected payment ID {payment_id}"
                )
            )

    def sync_booking_balance(self, conn, booking_id: int):
        booking = conn.execute(
            """
            SELECT total_amount
            FROM bookings
            WHERE id = ?
            """,
            (booking_id,)
        ).fetchone()

        if not booking:
            return

        total_amount = float(booking["total_amount"] or 0)

        totals = conn.execute(
            """
            SELECT
                COALESCE(SUM(
                    CASE 
                        WHEN verification_status = 'Verified'
                         AND payment_type != 'Refund'
                        THEN amount
                        ELSE 0
                    END
                ), 0) AS total_paid,

                COALESCE(SUM(
                    CASE 
                        WHEN verification_status = 'Verified'
                         AND payment_type = 'Refund'
                        THEN amount
                        ELSE 0
                    END
                ), 0) AS total_refunded,

                COALESCE(SUM(
                    CASE 
                        WHEN verification_status = 'Verified'
                         AND payment_type = 'Down Payment'
                        THEN amount
                        ELSE 0
                    END
                ), 0) AS verified_down_payment
            FROM payments
            WHERE booking_id = ?
            """,
            (booking_id,)
        ).fetchone()

        total_paid = float(totals["total_paid"] or 0)
        total_refunded = float(totals["total_refunded"] or 0)
        verified_down_payment = float(totals["verified_down_payment"] or 0)

        net_paid = total_paid - total_refunded
        balance = total_amount - net_paid

        conn.execute(
            """
            UPDATE bookings
            SET down_payment_amount = ?,
                balance_amount = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                verified_down_payment,
                balance,
                booking_id
            )
        )