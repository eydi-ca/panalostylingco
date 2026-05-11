import hashlib
import re
import secrets
from typing import Optional

from db import Database
from models import APP_MODULES, ROLE_PERMISSIONS, SessionUser


class AuthService:
    def __init__(self, db: Database):
        self.db = db
        self.seed_default_admin()

    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        if salt is None:
            salt = secrets.token_hex(16)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100_000
        ).hex()

        return password_hash, salt

    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        new_hash, _ = self.hash_password(password, salt)
        return secrets.compare_digest(new_hash, password_hash)

    def validate_password(self, password: str):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters.")

        if len(password) > 50:
            raise ValueError("Password must not exceed 50 characters.")

        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;/`~]", password):
            raise ValueError("Password must contain at least one special character.")

    def seed_default_admin(self):
        admin_username = "admin"
        admin_password = "Panalo@2026"

        password_hash, salt = self.hash_password(admin_password)

        with self.db.get_conn() as conn:
            any_admin = conn.execute(
                """
                SELECT id
                FROM users
                WHERE role = 'ADMIN'
                  AND is_active = 1
                LIMIT 1
                """
            ).fetchone()

            if any_admin:
                return

            existing_admin = conn.execute(
                """
                SELECT id
                FROM users
                WHERE username = ?
                LIMIT 1
                """,
                (admin_username,)
            ).fetchone()

            if existing_admin:
                conn.execute(
                    """
                    UPDATE users
                    SET full_name = ?,
                        username = ?,
                        password_hash = ?,
                        password_salt = ?,
                        role = ?,
                        is_active = 1
                    WHERE id = ?
                    """,
                    (
                        "Panalo Styling Admin",
                        admin_username,
                        password_hash,
                        salt,
                        "ADMIN",
                        existing_admin["id"]
                    )
                )
                return

            conn.execute(
                """
                INSERT INTO users
                (full_name, username, email, phone_number, password_hash, password_salt, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "Panalo Styling Admin",
                    admin_username,
                    "admin@panalo.local",
                    "admin",
                    password_hash,
                    salt,
                    "ADMIN",
                    1
                )
            )

    def login(self, username: str, password: str) -> SessionUser:
        username = username.strip().lower()

        if not username or not password:
            raise ValueError("Username and password are required.")

        with self.db.get_conn() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM users
                WHERE username = ?
                """,
                (username,)
            ).fetchone()

        if not row:
            raise ValueError("Invalid username or password.")

        is_valid = self.verify_password(
            password,
            row["password_hash"],
            row["password_salt"]
        )

        if not is_valid:
            raise ValueError("Invalid username or password.")

        return SessionUser(
            id=row["id"],
            full_name=row["full_name"],
            username=row["username"],
            role=row["role"]
        )

    def ensure_admin(self, actor_id: int):
        with self.db.get_conn() as conn:
            row = conn.execute(
                "SELECT role FROM users WHERE id = ?",
                (actor_id,)
            ).fetchone()

        if not row or row["role"] != "ADMIN":
            raise ValueError("Only admin can perform this action.")

    def validate_user_data(self, full_name: str, username: str, role: str):
        if not full_name.strip():
            raise ValueError("Full name is required.")

        if not username.strip():
            raise ValueError("Username is required.")

        username_pattern = r"^[a-zA-Z0-9_]{4,30}$"
        if not re.match(username_pattern, username.strip()):
            raise ValueError("Username must be 4-30 characters and may only contain letters, numbers, and underscore.")

        if role not in ["ADMIN", "STAFF"]:
            raise ValueError("Invalid role.")

    def get_user_by_id(self, user_id: int):
        with self.db.get_conn() as conn:
            row = conn.execute(
                """
                SELECT id, full_name, username, role, created_at
                FROM users
                WHERE id = ?
                """,
                (user_id,)
            ).fetchone()

        if not row:
            raise ValueError("User not found.")

        return dict(row)

    def update_own_account(self, user_id: int, full_name: str, username: str, current_password: str):
        existing = self.get_user_by_id(user_id)

        if not current_password:
            raise ValueError("Current password is required.")

        full_name = full_name.strip()
        username = username.strip().lower()
        role = existing["role"]

        self.validate_user_data(full_name, username, role)

        try:
            with self.db.get_conn() as conn:
                password_row = conn.execute(
                    """
                    SELECT password_hash, password_salt
                    FROM users
                    WHERE id = ?
                    """,
                    (user_id,)
                ).fetchone()

                if not password_row:
                    raise ValueError("User not found.")

                if not self.verify_password(
                    current_password,
                    password_row["password_hash"],
                    password_row["password_salt"]
                ):
                    raise ValueError("Current password is incorrect.")

                conn.execute(
                    """
                    UPDATE users
                    SET full_name = ?,
                        username = ?
                    WHERE id = ?
                    """,
                    (full_name, username, user_id)
                )

                conn.execute(
                    """
                    INSERT INTO audit_logs (user_id, action, details)
                    VALUES (?, ?, ?)
                    """,
                    (user_id, "UPDATE_OWN_ACCOUNT", "Updated own account profile")
                )

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Username already exists.")
            raise

        return SessionUser(
            id=user_id,
            full_name=full_name,
            username=username,
            role=role
        )

    def change_own_password(self, user_id: int, current_password: str, new_password: str):
        if not current_password:
            raise ValueError("Current password is required.")

        self.validate_password(new_password)

        with self.db.get_conn() as conn:
            row = conn.execute(
                """
                SELECT password_hash, password_salt
                FROM users
                WHERE id = ?
                """,
                (user_id,)
            ).fetchone()

            if not row:
                raise ValueError("User not found.")

            if not self.verify_password(current_password, row["password_hash"], row["password_salt"]):
                raise ValueError("Current password is incorrect.")

            password_hash, salt = self.hash_password(new_password)

            conn.execute(
                """
                UPDATE users
                SET password_hash = ?,
                    password_salt = ?
                WHERE id = ?
                """,
                (password_hash, salt, user_id)
            )

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (user_id, "CHANGE_OWN_PASSWORD", "Changed own password")
            )

    def create_user_by_admin(
        self,
        actor_id: int,
        full_name: str,
        username: str,
        password: str,
        role: str
    ):
        self.ensure_admin(actor_id)

        full_name = full_name.strip()
        username = username.strip().lower()
        role = role.strip().upper()

        self.validate_user_data(full_name, username, role)
        self.validate_password(password)

        password_hash, salt = self.hash_password(password)

        try:
            with self.db.get_conn() as conn:
                cur = conn.execute(
                    """
                    INSERT INTO users
                    (full_name, username, email, phone_number, password_hash, password_salt, role, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        full_name,
                        username,
                        f"{username}@panalo.local",
                        username,
                        password_hash,
                        salt,
                        role,
                        1
                    )
                )

                user_id = cur.lastrowid

                for module in ROLE_PERMISSIONS.get(role, set()):
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO user_module_permissions
                        (user_id, module_name, is_allowed)
                        VALUES (?, ?, ?)
                        """,
                        (user_id, module, 1)
                    )

                conn.execute(
                    """
                    INSERT INTO audit_logs (user_id, action, details)
                    VALUES (?, ?, ?)
                    """,
                    (actor_id, "CREATE_USER", f"Created account for {username}")
                )

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Username already exists.")
            raise

    def list_users(self):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT id, full_name, username, role, created_at
                FROM users
                ORDER BY id DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def get_user_permissions(self, user_id: int, role: str) -> set[str]:
        default_permissions = set(ROLE_PERMISSIONS.get(role, set()))

        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT module_name, is_allowed
                FROM user_module_permissions
                WHERE user_id = ?
                """,
                (user_id,)
            ).fetchall()

        if not rows:
            return default_permissions

        allowed = set()

        for row in rows:
            if row["is_allowed"] == 1:
                allowed.add(row["module_name"])

        return allowed

    def update_user_by_admin(
        self,
        actor_id: int,
        user_id: int,
        full_name: str,
        username: str,
        role: str,
        new_password: str | None = None
    ):
        self.ensure_admin(actor_id)

        full_name = full_name.strip()
        username = username.strip().lower()
        role = role.strip().upper()

        self.validate_user_data(full_name, username, role)

        with self.db.get_conn() as conn:
            existing = conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()

            if not existing:
                raise ValueError("User not found.")

            if new_password:
                self.validate_password(new_password)
                password_hash, salt = self.hash_password(new_password)

                conn.execute(
                    """
                    UPDATE users
                    SET full_name = ?,
                        username = ?,
                        role = ?,
                        password_hash = ?,
                        password_salt = ?,
                        is_active = 1
                    WHERE id = ?
                    """,
                    (
                        full_name,
                        username,
                        role,
                        password_hash,
                        salt,
                        user_id
                    )
                )
            else:
                conn.execute(
                    """
                    UPDATE users
                    SET full_name = ?,
                        username = ?,
                        role = ?,
                        is_active = 1
                    WHERE id = ?
                    """,
                    (
                        full_name,
                        username,
                        role,
                        user_id
                    )
                )

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (actor_id, "UPDATE_USER", f"Updated account ID {user_id}")
            )

    def set_user_permissions(self, actor_id: int, user_id: int, permissions: dict[str, int]):
        self.ensure_admin(actor_id)

        with self.db.get_conn() as conn:
            conn.execute(
                "DELETE FROM user_module_permissions WHERE user_id = ?",
                (user_id,)
            )

            for module_name, is_allowed in permissions.items():
                if module_name not in APP_MODULES:
                    continue

                conn.execute(
                    """
                    INSERT INTO user_module_permissions
                    (user_id, module_name, is_allowed)
                    VALUES (?, ?, ?)
                    """,
                    (user_id, module_name, int(is_allowed))
                )

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (actor_id, "UPDATE_USER_PERMISSIONS", f"Updated permissions for user ID {user_id}")
            )
