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

    # ─────────────────────────────────────────────
    # Password helpers
    # ─────────────────────────────────────────────

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

    # ─────────────────────────────────────────────
    # Seed
    # ─────────────────────────────────────────────

    def seed_default_admin(self):
        admin_username = "admin"
        admin_password = "Panalo@2026"

        password_hash, salt = self.hash_password(admin_password)

        with self.db.get_conn() as conn:
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
                    None,
                    None,
                    password_hash,
                    salt,
                    "ADMIN",
                    1
                )
            )

    # ─────────────────────────────────────────────
    # Login
    # ─────────────────────────────────────────────

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

        if not row["is_active"]:
            raise ValueError("This account has been deactivated. Contact your administrator.")

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

    # ─────────────────────────────────────────────
    # Authorization guards
    # ─────────────────────────────────────────────

    def ensure_admin(self, actor_id: int):
        with self.db.get_conn() as conn:
            row = conn.execute(
                "SELECT role FROM users WHERE id = ?",
                (actor_id,)
            ).fetchone()

        if not row or row["role"] != "ADMIN":
            raise ValueError("Only admin can perform this action.")

    # ─────────────────────────────────────────────
    # Validation
    # ─────────────────────────────────────────────

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

    def validate_pin(self, pin: str):
        pin = pin.strip()
        if not pin:
            raise ValueError("PIN code is required.")
        if not re.match(r"^\d{4,6}$", pin):
            raise ValueError("PIN must be 4 to 6 digits.")

    # ─────────────────────────────────────────────
    # Create / Update user
    # ─────────────────────────────────────────────

    def create_user_by_admin(
        self,
        actor_id: int,
        full_name: str,
        username: str,
        password: str,
        role: str,
        email: str = "",
        phone_number: str = "",
    ):
        self.ensure_admin(actor_id)

        full_name = full_name.strip()
        username = username.strip().lower()
        role = role.strip().upper()
        email = email.strip() or None
        phone_number = phone_number.strip() or None

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
                        email,
                        phone_number,
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
                    (actor_id, "CREATE_USER", f"Created account for {username} (role: {role})")
                )

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Username already exists.")
            raise

    # ─────────────────────────────────────────────
    # List users
    # ─────────────────────────────────────────────

    def list_users(self):
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """
                SELECT u.id, u.full_name, u.username, u.role, u.is_active, u.email,
                       u.phone_number, u.created_at,
                       CASE WHEN bp.id IS NOT NULL AND bp.is_active = 1 THEN 1 ELSE 0 END AS has_bypass_pin
                FROM users u
                LEFT JOIN bypass_pins bp ON bp.user_id = u.id
                ORDER BY u.id DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    # ─────────────────────────────────────────────
    # Permissions
    # ─────────────────────────────────────────────

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

    # ─────────────────────────────────────────────
    # Update user
    # ─────────────────────────────────────────────

    def update_user_by_admin(
        self,
        actor_id: int,
        user_id: int,
        full_name: str,
        username: str,
        role: str,
        email: str = "",
        phone_number: str = "",
        is_active: int = 1,
        new_password: str | None = None
    ):
        self.ensure_admin(actor_id)

        full_name = full_name.strip()
        username = username.strip().lower()
        role = role.strip().upper()
        email = email.strip() or None
        phone_number = phone_number.strip() or None

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
                        email = ?,
                        phone_number = ?,
                        password_hash = ?,
                        password_salt = ?,
                        is_active = ?
                    WHERE id = ?
                    """,
                    (
                        full_name,
                        username,
                        role,
                        email,
                        phone_number,
                        password_hash,
                        salt,
                        is_active,
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
                        email = ?,
                        phone_number = ?,
                        is_active = ?
                    WHERE id = ?
                    """,
                    (
                        full_name,
                        username,
                        role,
                        email,
                        phone_number,
                        is_active,
                        user_id
                    )
                )

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (actor_id, "UPDATE_USER", f"Updated account ID {user_id} ({username})")
            )

    # ─────────────────────────────────────────────
    # Password recovery (admin only)
    # ─────────────────────────────────────────────

    def reset_password_by_admin(
        self,
        actor_id: int,
        target_user_id: int,
        new_password: str
    ):
        """Admin resets a staff member's forgotten password."""
        self.ensure_admin(actor_id)

        self.validate_password(new_password)

        password_hash, salt = self.hash_password(new_password)

        with self.db.get_conn() as conn:
            target = conn.execute(
                "SELECT id, username FROM users WHERE id = ?",
                (target_user_id,)
            ).fetchone()

            if not target:
                raise ValueError("User not found.")

            conn.execute(
                """
                UPDATE users
                SET password_hash = ?,
                    password_salt = ?
                WHERE id = ?
                """,
                (password_hash, salt, target_user_id)
            )

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (
                    actor_id,
                    "RESET_PASSWORD",
                    f"Admin reset password for user ID {target_user_id} ({target['username']})"
                )
            )

    # ─────────────────────────────────────────────
    # Bypass PIN management
    # ─────────────────────────────────────────────

    def set_bypass_pin(self, actor_id: int, target_user_id: int, pin: str):
        """Set or update the bypass PIN for a user. Only admin can call this."""
        self.ensure_admin(actor_id)
        self.validate_pin(pin)

        pin_hash, pin_salt = self.hash_password(pin)

        with self.db.get_conn() as conn:
            existing = conn.execute(
                "SELECT id FROM bypass_pins WHERE user_id = ?",
                (target_user_id,)
            ).fetchone()

            if existing:
                conn.execute(
                    """
                    UPDATE bypass_pins
                    SET pin_hash = ?,
                        pin_salt = ?,
                        is_active = 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                    """,
                    (pin_hash, pin_salt, target_user_id)
                )
            else:
                conn.execute(
                    """
                    INSERT INTO bypass_pins (user_id, pin_hash, pin_salt, is_active)
                    VALUES (?, ?, ?, 1)
                    """,
                    (target_user_id, pin_hash, pin_salt)
                )

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (actor_id, "SET_BYPASS_PIN", f"Set bypass PIN for user ID {target_user_id}")
            )

    def remove_bypass_pin(self, actor_id: int, target_user_id: int):
        """Deactivate the bypass PIN for a user. Only admin can call this."""
        self.ensure_admin(actor_id)

        with self.db.get_conn() as conn:
            conn.execute(
                """
                UPDATE bypass_pins
                SET is_active = 0,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                """,
                (target_user_id,)
            )

            conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (actor_id, "REMOVE_BYPASS_PIN", f"Removed bypass PIN for user ID {target_user_id}")
            )

    def verify_bypass_pin(self, user_id: int, pin: str) -> bool:
        """Verify if the supplied PIN matches the active bypass PIN for a user."""
        with self.db.get_conn() as conn:
            row = conn.execute(
                """
                SELECT pin_hash, pin_salt
                FROM bypass_pins
                WHERE user_id = ? AND is_active = 1
                """,
                (user_id,)
            ).fetchone()

        if not row:
            return False

        return self.verify_password(pin, row["pin_hash"], row["pin_salt"])

    def get_bypass_pin_status(self, user_id: int) -> bool:
        """Returns True if the user has an active bypass PIN set."""
        with self.db.get_conn() as conn:
            row = conn.execute(
                "SELECT id FROM bypass_pins WHERE user_id = ? AND is_active = 1",
                (user_id,)
            ).fetchone()
        return row is not None

    def get_user_by_id(self, user_id: int):
        """Fetch a single user record by ID."""
        with self.db.get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
        return dict(row) if row else None