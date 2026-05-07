from datetime import date

from db import Database


class ReportsService:
    def __init__(self, db: Database):
        self.db = db

    def get_booking_summary(self):
        with self.db.get_conn() as conn:
            total_bookings = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM bookings
                """
            ).fetchone()["count"]

            status_rows = conn.execute(
                """
                SELECT 
                    COALESCE(bs.name, 'No Status') AS status,
                    COUNT(b.id) AS count
                FROM bookings b
                LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                GROUP BY bs.name
                ORDER BY count DESC
                """
            ).fetchall()

            event_type_rows = conn.execute(
                """
                SELECT 
                    COALESCE(et.name, 'No Event Type') AS event_type,
                    COUNT(b.id) AS count
                FROM bookings b
                LEFT JOIN event_types et ON b.event_type_id = et.id
                GROUP BY et.name
                ORDER BY count DESC
                """
            ).fetchall()

        return {
            "total_bookings": total_bookings,
            "by_status": [dict(row) for row in status_rows],
            "by_event_type": [dict(row) for row in event_type_rows],
        }

    def get_payment_summary(self):
        with self.db.get_conn() as conn:
            expected_revenue = conn.execute(
                """
                SELECT COALESCE(SUM(total_amount), 0) AS total
                FROM bookings
                """
            ).fetchone()["total"]

            verified_paid = conn.execute(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM payments
                WHERE verification_status = 'Verified'
                  AND payment_type != 'Refund'
                """
            ).fetchone()["total"]

            pending_payment = conn.execute(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM payments
                WHERE verification_status = 'Pending'
                  AND payment_type != 'Refund'
                """
            ).fetchone()["total"]

            refunded_amount = conn.execute(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM payments
                WHERE verification_status = 'Verified'
                  AND payment_type = 'Refund'
                """
            ).fetchone()["total"]

            booking_rows = conn.execute(
                """
                SELECT
                    b.id AS booking_id,
                    c.full_name AS client_name,
                    b.total_amount,

                    COALESCE(SUM(
                        CASE
                            WHEN p.verification_status = 'Verified'
                             AND p.payment_type != 'Refund'
                            THEN p.amount
                            ELSE 0
                        END
                    ), 0) AS total_paid,

                    COALESCE(SUM(
                        CASE
                            WHEN p.verification_status = 'Verified'
                             AND p.payment_type = 'Refund'
                            THEN p.amount
                            ELSE 0
                        END
                    ), 0) AS total_refunded

                FROM bookings b
                LEFT JOIN clients c ON b.client_id = c.id
                LEFT JOIN payments p ON b.id = p.booking_id
                GROUP BY b.id
                ORDER BY b.id DESC
                """
            ).fetchall()

        booking_payment_statuses = []

        paid_count = 0
        partial_count = 0
        unpaid_count = 0
        total_balance = 0

        for row in booking_rows:
            item = dict(row)

            total_amount = float(item["total_amount"] or 0)
            total_paid = float(item["total_paid"] or 0)
            total_refunded = float(item["total_refunded"] or 0)

            net_paid = total_paid - total_refunded
            balance = total_amount - net_paid

            if balance <= 0 and total_amount > 0:
                payment_status = "Paid"
                paid_count += 1
            elif net_paid > 0:
                payment_status = "Partial"
                partial_count += 1
            else:
                payment_status = "Unpaid"
                unpaid_count += 1

            total_balance += balance

            item["net_paid"] = net_paid
            item["balance"] = balance
            item["payment_status"] = payment_status

            booking_payment_statuses.append(item)

        return {
            "expected_revenue": float(expected_revenue or 0),
            "verified_paid": float(verified_paid or 0),
            "pending_payment": float(pending_payment or 0),
            "refunded_amount": float(refunded_amount or 0),
            "total_balance": float(total_balance or 0),
            "paid_count": paid_count,
            "partial_count": partial_count,
            "unpaid_count": unpaid_count,
            "booking_payment_statuses": booking_payment_statuses,
        }

    def get_schedule_summary(self):
        today_text = date.today().strftime("%Y-%m-%d")
        month_prefix = date.today().strftime("%Y-%m")

        with self.db.get_conn() as conn:
            today_count = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM bookings
                WHERE event_date = ?
                """,
                (today_text,)
            ).fetchone()["count"]

            upcoming_count = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM bookings
                WHERE event_date >= ?
                """,
                (today_text,)
            ).fetchone()["count"]

            this_month_count = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM bookings
                WHERE event_date LIKE ?
                """,
                (f"{month_prefix}-%",)
            ).fetchone()["count"]

            cancelled_count = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM bookings b
                LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                WHERE LOWER(bs.name) = 'cancelled'
                """
            ).fetchone()["count"]

            upcoming_rows = conn.execute(
                """
                SELECT
                    b.id,
                    b.event_date,
                    b.event_time,
                    c.full_name AS client_name,
                    et.name AS event_type,
                    p.package_name,
                    b.event_location,
                    bs.name AS status
                FROM bookings b
                LEFT JOIN clients c ON b.client_id = c.id
                LEFT JOIN event_types et ON b.event_type_id = et.id
                LEFT JOIN packages p ON b.package_id = p.id
                LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                WHERE b.event_date >= ?
                ORDER BY b.event_date ASC, b.event_time ASC
                LIMIT 20
                """,
                (today_text,)
            ).fetchall()

        return {
            "today_count": today_count,
            "upcoming_count": upcoming_count,
            "this_month_count": this_month_count,
            "cancelled_count": cancelled_count,
            "upcoming_events": [dict(row) for row in upcoming_rows],
        }

    def get_client_summary(self):
        with self.db.get_conn() as conn:
            total_clients = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM clients
                """
            ).fetchone()["count"]

            clients_with_bookings = conn.execute(
                """
                SELECT COUNT(DISTINCT client_id) AS count
                FROM bookings
                WHERE client_id IS NOT NULL
                """
            ).fetchone()["count"]

            clients_without_bookings = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM clients c
                WHERE c.id NOT IN (
                    SELECT client_id
                    FROM bookings
                    WHERE client_id IS NOT NULL
                )
                """
            ).fetchone()["count"]

            recent_clients = conn.execute(
                """
                SELECT id, full_name, contact_number, notes, created_at
                FROM clients
                ORDER BY id DESC
                LIMIT 20
                """
            ).fetchall()

        return {
            "total_clients": total_clients,
            "clients_with_bookings": clients_with_bookings,
            "clients_without_bookings": clients_without_bookings,
            "recent_clients": [dict(row) for row in recent_clients],
        }

    def get_package_performance(self):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT
                    p.id,
                    p.package_name,
                    COUNT(b.id) AS booking_count,
                    COALESCE(SUM(b.total_amount), 0) AS total_revenue
                FROM packages p
                LEFT JOIN bookings b ON p.id = b.package_id
                GROUP BY p.id
                ORDER BY booking_count DESC, total_revenue DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def get_previous_range(self, start_date: str, end_date: str):
        from datetime import datetime, timedelta

        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        days_count = (end - start).days + 1

        previous_end = start - timedelta(days=1)
        previous_start = previous_end - timedelta(days=days_count - 1)

        return previous_start.strftime("%Y-%m-%d"), previous_end.strftime("%Y-%m-%d")

    def percent_change(self, current_value, previous_value):
        current_value = float(current_value or 0)
        previous_value = float(previous_value or 0)

        if previous_value == 0:
            if current_value > 0:
                return 100
            return 0

        return ((current_value - previous_value) / previous_value) * 100

    def get_dashboard_metrics_for_range(self, start_date: str, end_date: str):
        with self.db.get_conn() as conn:
            total_bookings = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM bookings
                WHERE event_date BETWEEN ? AND ?
                """,
                (start_date, end_date)
            ).fetchone()["count"]

            verified_payments = conn.execute(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM payments
                WHERE verification_status = 'Verified'
                  AND payment_type != 'Refund'
                  AND payment_date BETWEEN ? AND ?
                """,
                (start_date, end_date)
            ).fetchone()["total"]

            upcoming_events = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM bookings b
                LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                WHERE b.event_date BETWEEN ? AND ?
                  AND LOWER(COALESCE(bs.name, '')) != 'cancelled'
                """,
                (start_date, end_date)
            ).fetchone()["count"]

            new_clients = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM clients
                WHERE DATE(created_at) BETWEEN ? AND ?
                """,
                (start_date, end_date)
            ).fetchone()["count"]

        return {
            "total_bookings": total_bookings,
            "verified_payments": float(verified_payments or 0),
            "upcoming_events": upcoming_events,
            "new_clients": new_clients,
        }

    def get_dashboard_line_data(self, start_date: str, end_date: str):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT
                    event_date,
                    COUNT(*) AS booking_count
                FROM bookings
                WHERE event_date BETWEEN ? AND ?
                GROUP BY event_date
                ORDER BY event_date ASC
                """,
                (start_date, end_date)
            ).fetchall()

        return [dict(row) for row in rows]

    def get_dashboard_pie_data(self, start_date: str, end_date: str):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT
                    COALESCE(et.name, 'No Event Type') AS label,
                    COUNT(b.id) AS value
                FROM bookings b
                LEFT JOIN event_types et ON b.event_type_id = et.id
                WHERE b.event_date BETWEEN ? AND ?
                GROUP BY et.name
                ORDER BY value DESC
                """
                ,
                (start_date, end_date)
            ).fetchall()

        return [dict(row) for row in rows]

    def get_dashboard_upcoming_events(self, start_date: str, end_date: str):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT
                    b.id,
                    b.event_date,
                    b.event_time,
                    c.full_name AS client_name,
                    et.name AS event_type,
                    p.package_name,
                    b.event_location,
                    bs.name AS status
                FROM bookings b
                LEFT JOIN clients c ON b.client_id = c.id
                LEFT JOIN event_types et ON b.event_type_id = et.id
                LEFT JOIN packages p ON b.package_id = p.id
                LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                WHERE b.event_date BETWEEN ? AND ?
                ORDER BY b.event_date ASC, b.event_time ASC
                LIMIT 10
                """,
                (start_date, end_date)
            ).fetchall()

        return [dict(row) for row in rows]

    def get_dashboard_package_performance(self, start_date: str, end_date: str):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT
                    p.package_name,
                    COUNT(b.id) AS booking_count,
                    COALESCE(SUM(b.total_amount), 0) AS revenue
                FROM packages p
                LEFT JOIN bookings b ON p.id = b.package_id
                    AND b.event_date BETWEEN ? AND ?
                GROUP BY p.id
                ORDER BY booking_count DESC, revenue DESC
                LIMIT 8
                """,
                (start_date, end_date)
            ).fetchall()

        return [dict(row) for row in rows]

    def get_dashboard_today_schedule(self):
        from datetime import date

        today_text = date.today().strftime("%Y-%m-%d")

        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT
                    b.id,
                    b.event_date,
                    b.event_time,
                    c.full_name AS client_name,
                    et.name AS event_type,
                    p.package_name,
                    b.event_location,
                    bs.name AS status
                FROM bookings b
                LEFT JOIN clients c ON b.client_id = c.id
                LEFT JOIN event_types et ON b.event_type_id = et.id
                LEFT JOIN packages p ON b.package_id = p.id
                LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                WHERE b.event_date = ?
                ORDER BY b.event_time ASC
                LIMIT 8
                """,
                (today_text,)
            ).fetchall()

        return [dict(row) for row in rows]

    def get_dashboard_recent_bookings(self):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT
                    b.id,
                    b.event_date,
                    b.event_time,
                    c.full_name AS client_name,
                    p.package_name,
                    bs.name AS status
                FROM bookings b
                LEFT JOIN clients c ON b.client_id = c.id
                LEFT JOIN packages p ON b.package_id = p.id
                LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                ORDER BY b.id DESC
                LIMIT 8
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def get_dashboard_payment_queue(self):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT
                    pay.id,
                    pay.booking_id,
                    pay.payment_type,
                    pay.amount,
                    pay.payment_method,
                    pay.payment_date,
                    pay.verification_status,
                    c.full_name AS client_name,
                    p.package_name
                FROM payments pay
                LEFT JOIN bookings b ON pay.booking_id = b.id
                LEFT JOIN clients c ON b.client_id = c.id
                LEFT JOIN packages p ON b.package_id = p.id
                WHERE pay.verification_status = 'Pending'
                ORDER BY pay.id DESC
                LIMIT 8
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def get_dashboard_verified_payment_trend(self, start_date: str, end_date: str):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT
                    payment_date,
                    COALESCE(SUM(amount), 0) AS total_amount
                FROM payments
                WHERE verification_status = 'Verified'
                  AND payment_type != 'Refund'
                  AND payment_date BETWEEN ? AND ?
                GROUP BY payment_date
                ORDER BY payment_date ASC
                """,
                (start_date, end_date)
            ).fetchall()

        return [dict(row) for row in rows]

    def get_dashboard_data(self, start_date: str, end_date: str):
        previous_start, previous_end = self.get_previous_range(start_date, end_date)

        current_metrics = self.get_dashboard_metrics_for_range(start_date, end_date)
        previous_metrics = self.get_dashboard_metrics_for_range(previous_start, previous_end)

        progress = {
            "total_bookings": self.percent_change(
                current_metrics["total_bookings"],
                previous_metrics["total_bookings"]
            ),
            "verified_payments": self.percent_change(
                current_metrics["verified_payments"],
                previous_metrics["verified_payments"]
            ),
            "upcoming_events": self.percent_change(
                current_metrics["upcoming_events"],
                previous_metrics["upcoming_events"]
            ),
            "new_clients": self.percent_change(
                current_metrics["new_clients"],
                previous_metrics["new_clients"]
            ),
        }

        return {
            "start_date": start_date,
            "end_date": end_date,
            "previous_start": previous_start,
            "previous_end": previous_end,
            "metrics": current_metrics,
            "previous_metrics": previous_metrics,
            "progress": progress,

            "line_data": self.get_dashboard_line_data(start_date, end_date),
            "payment_trend": self.get_dashboard_verified_payment_trend(start_date, end_date),
            "pie_data": self.get_dashboard_pie_data(start_date, end_date),

            "today_schedule": self.get_dashboard_today_schedule(),
            "recent_bookings": self.get_dashboard_recent_bookings(),
            "payment_queue": self.get_dashboard_payment_queue(),

            "upcoming_events": self.get_dashboard_upcoming_events(start_date, end_date),
            "package_performance": self.get_dashboard_package_performance(start_date, end_date),
        }

    def get_all_reports(self):
        return {
            "booking": self.get_booking_summary(),
            "payment": self.get_payment_summary(),
            "schedule": self.get_schedule_summary(),
            "client": self.get_client_summary(),
            "packages": self.get_package_performance(),
        }