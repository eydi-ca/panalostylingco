from db import Database


class PackageService:
    def __init__(self, db: Database):
        self.db = db
        self.seed_default_packages()

    def seed_default_packages(self):
        default_packages = [
            {
                "package_name": "Munting Selebrasyon Package",
                "recommended_pax": "Up to 30 pax",
                "description": "Perfect for intimate family gatherings or home celebrations.",
                "inclusions": (
                    "Simple themed backdrop setup\n"
                    "Cake / dessert / focal table styling\n"
                    "Welcome sign\n"
                    "Basic table styling accents\n"
                    "Minimal balloon accents optional add-on\n"
                    "Setup and pull-out"
                ),
                "min_price": 12000,
                "max_price": 18000,
            },
            {
                "package_name": "Pinahahalagahang Pagdiriwang Package",
                "recommended_pax": "Up to 50 pax",
                "description": "Ideal for clients who want a polished, photo-worthy celebration.",
                "inclusions": (
                    "Enhanced themed backdrop setup\n"
                    "Cake / dessert / focal table styling\n"
                    "Welcome sign\n"
                    "Gift / souvenir table styling\n"
                    "Centerpiece styling for selected tables\n"
                    "Photo area styling\n"
                    "Minimal balloon accents optional add-on\n"
                    "Setup and pull-out"
                ),
                "min_price": 18000,
                "max_price": 28000,
            },
            {
                "package_name": "Magandang Alaala Package",
                "recommended_pax": "Up to 80 pax",
                "description": "Great for bigger gatherings, formal setups, or larger venues.",
                "inclusions": (
                    "Full event styling concept\n"
                    "Main backdrop setup\n"
                    "Cake / dessert / focal table styling\n"
                    "Welcome sign\n"
                    "Entrance styling\n"
                    "Gift / souvenir table styling\n"
                    "Guest table styling\n"
                    "Photo area styling\n"
                    "Minimal balloon accents optional add-on\n"
                    "Setup and pull-out"
                ),
                "min_price": 28000,
                "max_price": 45000,
            },
            {
                "package_name": "Panalong Selebrasyon Package",
                "recommended_pax": "Up to 100 pax",
                "description": "For clients who want a beautiful setup and smooth event flow.",
                "inclusions": (
                    "Full event styling concept\n"
                    "Main backdrop setup\n"
                    "Cake / dessert / focal table styling\n"
                    "Welcome sign\n"
                    "Entrance styling\n"
                    "Gift / souvenir table styling\n"
                    "Guest table styling\n"
                    "Photo area styling\n"
                    "Minimal balloon accents optional add-on\n"
                    "Event flow assistance / program planning\n"
                    "Supplier coordination\n"
                    "On-the-day coordination\n"
                    "Ceremony / reception flow support if applicable\n"
                    "Setup and pull-out"
                ),
                "min_price": 45000,
                "max_price": 70000,
            },
        ]

        with self.db.get_conn() as conn:
            for package in default_packages:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO packages (
                        package_name,
                        recommended_pax,
                        description,
                        inclusions,
                        min_price,
                        max_price,
                        is_active
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        package["package_name"],
                        package["recommended_pax"],
                        package["description"],
                        package["inclusions"],
                        package["min_price"],
                        package["max_price"],
                    )
                )

    def list_packages(self, search_text: str = ""):
        search_text = search_text.strip()

        with self.db.get_conn() as conn:
            if search_text:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM packages
                    WHERE 
                        package_name LIKE ?
                        OR recommended_pax LIKE ?
                        OR description LIKE ?
                        OR inclusions LIKE ?
                    ORDER BY id DESC
                    """,
                    (
                        f"%{search_text}%",
                        f"%{search_text}%",
                        f"%{search_text}%",
                        f"%{search_text}%",
                    )
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM packages
                    ORDER BY id DESC
                    """
                ).fetchall()

        return [dict(row) for row in rows]

    def get_package_by_id(self, package_id: int):
        with self.db.get_conn() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM packages
                WHERE id = ?
                """,
                (package_id,)
            ).fetchone()

        return dict(row) if row else None

    def add_package(
        self,
        package_name: str,
        recommended_pax: str,
        description: str,
        inclusions: str,
        min_price: float | None,
        max_price: float | None,
        created_by: int
    ):
        package_name = package_name.strip()

        if not package_name:
            raise ValueError("Package name is required.")

        if min_price is not None and min_price < 0:
            raise ValueError("Minimum price cannot be negative.")

        if max_price is not None and max_price < 0:
            raise ValueError("Maximum price cannot be negative.")

        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValueError("Minimum price cannot be greater than maximum price.")

        try:
            with self.db.get_conn() as conn:
                cur = conn.execute(
                    """
                    INSERT INTO packages (
                        package_name,
                        recommended_pax,
                        description,
                        inclusions,
                        min_price,
                        max_price,
                        is_active,
                        created_by
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                    """,
                    (
                        package_name,
                        recommended_pax.strip(),
                        description.strip(),
                        inclusions.strip(),
                        min_price,
                        max_price,
                        created_by
                    )
                )

                package_id = cur.lastrowid

                conn.execute(
                    """
                    INSERT INTO audit_logs (user_id, action, details)
                    VALUES (?, ?, ?)
                    """,
                    (
                        created_by,
                        "ADD_PACKAGE",
                        f"Added package ID {package_id}: {package_name}"
                    )
                )

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Package name already exists.")
            raise

    def update_package(
        self,
        package_id: int,
        package_name: str,
        recommended_pax: str,
        description: str,
        inclusions: str,
        min_price: float | None,
        max_price: float | None,
        actor_id: int
    ):
        package_name = package_name.strip()

        if not package_name:
            raise ValueError("Package name is required.")

        if min_price is not None and min_price < 0:
            raise ValueError("Minimum price cannot be negative.")

        if max_price is not None and max_price < 0:
            raise ValueError("Maximum price cannot be negative.")

        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValueError("Minimum price cannot be greater than maximum price.")

        try:
            with self.db.get_conn() as conn:
                existing = conn.execute(
                    """
                    SELECT id
                    FROM packages
                    WHERE id = ?
                    """,
                    (package_id,)
                ).fetchone()

                if not existing:
                    raise ValueError("Package not found.")

                conn.execute(
                    """
                    UPDATE packages
                    SET 
                        package_name = ?,
                        recommended_pax = ?,
                        description = ?,
                        inclusions = ?,
                        min_price = ?,
                        max_price = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        package_name,
                        recommended_pax.strip(),
                        description.strip(),
                        inclusions.strip(),
                        min_price,
                        max_price,
                        package_id
                    )
                )

                conn.execute(
                    """
                    INSERT INTO audit_logs (user_id, action, details)
                    VALUES (?, ?, ?)
                    """,
                    (
                        actor_id,
                        "UPDATE_PACKAGE",
                        f"Updated package ID {package_id}: {package_name}"
                    )
                )

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Package name already exists.")
            raise