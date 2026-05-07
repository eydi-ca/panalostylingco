import json
import tkinter as tk
import calendar
from datetime import date, datetime, timedelta
from pathlib import Path
from tkinter import ttk, messagebox

from auth_service import AuthService
from db import Database
from models import APP_NAME, APP_MODULES, SessionUser
from settings_service import SettingsService
from client_service import ClientService
from package_service import PackageService
from booking_service import BookingService
from schedule_service import ScheduleService
from payment_service import PaymentService

TIME_OPTIONS = [
    "06:00 AM", "06:30 AM",
    "07:00 AM", "07:30 AM",
    "08:00 AM", "08:30 AM",
    "09:00 AM", "09:30 AM",
    "10:00 AM", "10:30 AM",
    "11:00 AM", "11:30 AM",
    "12:00 PM", "12:30 PM",
    "01:00 PM", "01:30 PM",
    "02:00 PM", "02:30 PM",
    "03:00 PM", "03:30 PM",
    "04:00 PM", "04:30 PM",
    "05:00 PM", "05:30 PM",
    "06:00 PM", "06:30 PM",
    "07:00 PM", "07:30 PM",
    "08:00 PM", "08:30 PM",
    "09:00 PM", "09:30 PM",
    "10:00 PM"
]

REMEMBER_FILE = Path(__file__).resolve().parent / "data" / "remember_me.json"


class PanaloApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1100x700")
        self.minsize(950, 600)

        self.db = Database()
        self.auth_service = AuthService(self.db)
        self.settings_service = SettingsService(self.db)
        self.client_service = ClientService(self.db)
        self.package_service = PackageService(self.db)
        self.booking_service = BookingService(self.db)
        self.schedule_service = ScheduleService(self.db)
        self.payment_service = PaymentService(self.db)
        self.current_user: SessionUser | None = None

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.show_login_page()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login_page(self):
        self.clear_container()
        LoginPage(self.container, self).pack(fill="both", expand=True)

    def show_main_system(self, user: SessionUser):
        self.current_user = user
        self.clear_container()

        try:
            self.state("zoomed")
        except tk.TclError:
            self.attributes("-fullscreen", True)

        MainSystemPage(self.container, self, user).pack(fill="both", expand=True)

    def logout(self):
        self.current_user = None
        self.show_login_page()


class LoginPage(ttk.Frame):
    def __init__(self, parent, app: PanaloApp):
        super().__init__(parent)
        self.app = app

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_var = tk.BooleanVar(value=False)
        self.password_visible = False

        self.load_remembered_email()
        self.build_ui()

    def load_remembered_email(self):
        try:
            if REMEMBER_FILE.exists():
                with open(REMEMBER_FILE, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    self.username_var.set(data.get("username", ""))
                    self.remember_var.set(bool(data.get("remember", False)))
        except Exception:
            pass

    def save_remembered_email(self):
        REMEMBER_FILE.parent.mkdir(exist_ok=True)

        if self.remember_var.get():
            with open(REMEMBER_FILE, "w", encoding="utf-8") as file:
                json.dump(
                    {
                        "username": self.username_var.get().strip(),
                        "remember": True
                    },
                    file,
                    indent=4
                )
        else:
            if REMEMBER_FILE.exists():
                REMEMBER_FILE.unlink()

    def build_ui(self):
        wrapper = ttk.Frame(self, padding=30)
        wrapper.pack(expand=True)

        ttk.Label(
            wrapper,
            text="PanaloStylingCo",
            font=("Segoe UI", 28, "bold")
        ).pack(pady=(0, 5))

        ttk.Label(
            wrapper,
            text="Admin Login",
            font=("Segoe UI", 12)
        ).pack(pady=(0, 25))

        card = ttk.Frame(wrapper, padding=25, relief="ridge")
        card.pack(fill="x")

        ttk.Label(
            card,
            text="Login",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(0, 15))

        ttk.Label(card, text="Username").pack(anchor="w")
        username_entry = ttk.Entry(card, textvariable=self.username_var, width=42)
        username_entry.pack(fill="x", pady=(3, 12))

        ttk.Label(card, text="Password").pack(anchor="w")

        password_box = tk.Frame(
            card,
            bd=1,
            relief="solid",
            bg="white"
        )
        password_box.pack(fill="x", pady=(3, 12))

        self.password_entry = tk.Entry(
            password_box,
            textvariable=self.password_var,
            show="*",
            relief="flat",
            bg="white"
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(6, 2), pady=5)

        self.eye_button = tk.Button(
            password_box,
            text="👁",
            bd=0,
            bg="white",
            activebackground="white",
            command=self.toggle_password
        )
        self.eye_button.pack(side="right", padx=(2, 6))

        ttk.Checkbutton(
            card,
            text="Remember me",
            variable=self.remember_var
        ).pack(anchor="w", pady=(0, 15))

        ttk.Button(
            card,
            text="Login",
            command=self.handle_login
        ).pack(fill="x")

        ttk.Label(
            wrapper,
            text="Default admin: admin / Panalo@2026",
            font=("Segoe UI", 9)
        ).pack(pady=(15, 0))

        username_entry.focus_set()
        self.bind_all("<Return>", lambda event: self.handle_login())

    def toggle_password(self):
        self.password_visible = not self.password_visible

        if self.password_visible:
            self.password_entry.config(show="")
            self.eye_button.config(text="🙈")
        else:
            self.password_entry.config(show="*")
            self.eye_button.config(text="👁")

    def handle_login(self):
        try:
            user = self.app.auth_service.login(
                self.username_var.get(),
                self.password_var.get()
            )

            self.save_remembered_email()

            messagebox.showinfo(
                "Login Successful",
                f"Welcome, {user.full_name}!"
            )

            self.app.show_main_system(user)

        except ValueError as e:
            messagebox.showerror("Login Failed", str(e))


class MainSystemPage(ttk.Frame):
    def __init__(self, parent, app: PanaloApp, user: SessionUser):
        super().__init__(parent)
        self.app = app
        self.user = user
        self.content = None

        self.build_ui()

    def build_ui(self):
        sidebar = tk.Frame(self, bg="#222222", width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.content = ttk.Frame(self, padding=25)
        self.content.pack(side="left", fill="both", expand=True)

        tk.Label(
            sidebar,
            text="PanaloStylingCo",
            bg="#222222",
            fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(25, 5))

        tk.Label(
            sidebar,
            text=f"{self.user.full_name}\n{self.user.role}",
            bg="#222222",
            fg="#dddddd",
            font=("Segoe UI", 10),
            justify="center"
        ).pack(pady=(0, 25))

        allowed_modules = self.app.auth_service.get_user_permissions(
            self.user.id,
            self.user.role
        )

        for module in APP_MODULES:
            if module in allowed_modules:
                btn = tk.Button(
                    sidebar,
                    text=module,
                    anchor="w",
                    padx=20,
                    bg="#2f2f2f",
                    fg="white",
                    activebackground="#444444",
                    activeforeground="white",
                    relief="flat",
                    command=lambda name=module: self.show_module(name)
                )
                btn.pack(fill="x", pady=1)

        logout_btn = tk.Button(
            sidebar,
            text="Logout",
            anchor="w",
            padx=20,
            bg="#8b1e1e",
            fg="white",
            activebackground="#a82b2b",
            activeforeground="white",
            relief="flat",
            command=self.app.logout
        )
        logout_btn.pack(side="bottom", fill="x", pady=(0, 20))

        self.show_module("Dashboard")

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_module(self, module_name):
        self.clear_content()

        if module_name == "User Management":
            UserManagementPage(self.content, self.app).pack(fill="both", expand=True)
            return

        if module_name == "Settings":
            SettingsPage(self.content, self.app).pack(fill="both", expand=True)
            return

        if module_name == "Clients":
            ClientsPage(self.content, self.app).pack(fill="both", expand=True)
            return

        if module_name == "Packages":
            PackagesPage(self.content, self.app).pack(fill="both", expand=True)
            return

        if module_name == "Bookings":
            BookingsPage(self.content, self.app).pack(fill="both", expand=True)
            return

        if module_name == "Schedule":
            SchedulePage(self.content, self.app).pack(fill="both", expand=True)
            return

        if module_name == "Payment":
            PaymentPage(self.content, self.app).pack(fill="both", expand=True)
            return

        ttk.Label(
            self.content,
            text=module_name,
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w")

        ttk.Label(
            self.content,
            text=f"{module_name} module will be developed next.",
            font=("Segoe UI", 12)
        ).pack(anchor="w", pady=(10, 0))


class UserManagementPage(ttk.Frame):
    def __init__(self, parent, app: PanaloApp):
        super().__init__(parent)
        self.app = app
        self.selected_user_id = None
        self.users_cache = []

        self.build_ui()
        self.load_users()

    def build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            header,
            text="User Management",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Add User",
            command=self.open_add_user_window
        ).pack(side="right")

        columns = ("id", "full_name", "username", "role")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=14)

        self.table.heading("id", text="ID")
        self.table.heading("full_name", text="Full Name")
        self.table.heading("username", text="Username")
        self.table.heading("role", text="Role")

        self.table.column("id", width=60)
        self.table.column("full_name", width=250)
        self.table.column("username", width=180)
        self.table.column("role", width=100)

        self.table.pack(fill="both", expand=True)

        action_bar = ttk.Frame(self)
        action_bar.pack(fill="x", pady=(12, 0))

        ttk.Button(
            action_bar,
            text="Edit Selected User",
            command=self.open_edit_user_window
        ).pack(side="left")

        ttk.Button(
            action_bar,
            text="Edit Privileges",
            command=self.open_privileges_window
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            action_bar,
            text="Refresh",
            command=self.load_users
        ).pack(side="right")

    def load_users(self):
        for item in self.table.get_children():
            self.table.delete(item)

        self.users_cache = self.app.auth_service.list_users()

        for user in self.users_cache:
            self.table.insert(
                "",
                "end",
                values=(
                    user["id"],
                    user["full_name"],
                    user["username"],
                    user["role"]
                )
            )

    def get_selected_user(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning("No Selection", "Please select a user first.")
            return None

        values = self.table.item(selected[0], "values")
        user_id = int(values[0])

        for user in self.users_cache:
            if user["id"] == user_id:
                return user

        return None

    def open_add_user_window(self):
        UserFormWindow(self.app, self, mode="add")

    def open_edit_user_window(self):
        user = self.get_selected_user()

        if not user:
            return

        UserFormWindow(self.app, self, mode="edit", user=user)

    def open_privileges_window(self):
        user = self.get_selected_user()

        if not user:
            return

        PrivilegesWindow(self.app, self, user)


class UserFormWindow(tk.Toplevel):
    def __init__(self, app: PanaloApp, parent_page: UserManagementPage, mode: str, user=None):
        super().__init__()

        self.app = app
        self.parent_page = parent_page
        self.mode = mode
        self.user = user

        self.title("Add User" if mode == "add" else "Edit User")
        self.geometry("460x500")
        self.resizable(False, False)

        self.full_name_var = tk.StringVar(value=user["full_name"] if user else "")
        self.username_var = tk.StringVar(value=user["username"] if user else "")
        self.role_var = tk.StringVar(value=user["role"] if user else "STAFF")
        self.password_var = tk.StringVar()

        self.password_visible = False

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Add User" if self.mode == "add" else "Edit User",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(0, 15))

        ttk.Label(frame, text="Full Name").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.full_name_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Username").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.username_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Role").pack(anchor="w")
        ttk.Combobox(
            frame,
            textvariable=self.role_var,
            values=["ADMIN", "STAFF"],
            state="readonly"
        ).pack(fill="x", pady=(3, 10))

        password_label = "Password" if self.mode == "add" else "New Password, optional"
        ttk.Label(frame, text=password_label).pack(anchor="w")

        password_box = tk.Frame(frame, bd=1, relief="solid", bg="white")
        password_box.pack(fill="x", pady=(3, 15))

        self.password_entry = tk.Entry(
            password_box,
            textvariable=self.password_var,
            show="*",
            relief="flat",
            bg="white"
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(6, 2), pady=5)

        self.eye_button = tk.Button(
            password_box,
            text="👁",
            bd=0,
            bg="white",
            activebackground="white",
            command=self.toggle_password
        )
        self.eye_button.pack(side="right", padx=(2, 6))

        ttk.Button(
            frame,
            text="Save",
            command=self.save_user
        ).pack(fill="x", pady=(5, 0))

    def toggle_password(self):
        self.password_visible = not self.password_visible

        if self.password_visible:
            self.password_entry.config(show="")
            self.eye_button.config(text="🙈")
        else:
            self.password_entry.config(show="*")
            self.eye_button.config(text="👁")

    def save_user(self):
        try:
            actor_id = self.app.current_user.id

            if self.mode == "add":
                self.app.auth_service.create_user_by_admin(
                    actor_id=actor_id,
                    full_name=self.full_name_var.get(),
                    username=self.username_var.get(),
                    password=self.password_var.get(),
                    role=self.role_var.get()
                )
                messagebox.showinfo("Success", "User account created successfully.")

            else:
                self.app.auth_service.update_user_by_admin(
                    actor_id=actor_id,
                    user_id=self.user["id"],
                    full_name=self.full_name_var.get(),
                    username=self.username_var.get(),
                    role=self.role_var.get(),
                    new_password=self.password_var.get().strip() or None
                )
                messagebox.showinfo("Success", "User account updated successfully.")

            self.parent_page.load_users()
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))


class PrivilegesWindow(tk.Toplevel):
    def __init__(self, app: PanaloApp, parent_page: UserManagementPage, user):
        super().__init__()

        self.app = app
        self.parent_page = parent_page
        self.user = user

        self.title("Edit User Privileges")
        self.geometry("420x520")
        self.resizable(False, False)

        self.permission_vars = {}

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Edit Privileges",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(0, 5))

        ttk.Label(
            frame,
            text=f"User: {self.user['full_name']}",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 15))

        allowed = self.app.auth_service.get_user_permissions(
            self.user["id"],
            self.user["role"]
        )

        for module in APP_MODULES:
            var = tk.IntVar(value=1 if module in allowed else 0)
            self.permission_vars[module] = var

            ttk.Checkbutton(
                frame,
                text=module,
                variable=var
            ).pack(anchor="w", pady=3)

        ttk.Button(
            frame,
            text="Save Privileges",
            command=self.save_privileges
        ).pack(fill="x", pady=(20, 0))

    def save_privileges(self):
        try:
            permissions = {
                module: var.get()
                for module, var in self.permission_vars.items()
            }

            self.app.auth_service.set_user_permissions(
                actor_id=self.app.current_user.id,
                user_id=self.user["id"],
                permissions=permissions
            )

            messagebox.showinfo(
                "Success",
                "User privileges updated successfully. Changes will apply on next login."
            )

            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))

class SimpleNameWindow(tk.Toplevel):
    def __init__(self, parent, title, label, save_callback, initial_value=""):
        super().__init__()

        self.parent = parent
        self.save_callback = save_callback
        self.name_var = tk.StringVar(value=initial_value)

        self.title(title)
        self.geometry("380x180")
        self.resizable(False, False)

        self.build_ui(label)

    def build_ui(self, label):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=label
        ).pack(anchor="w", pady=(0, 5))

        entry = ttk.Entry(frame, textvariable=self.name_var)
        entry.pack(fill="x", pady=(0, 15))
        entry.focus_set()

        button_row = ttk.Frame(frame)
        button_row.pack(fill="x")

        ttk.Button(
            button_row,
            text="Cancel",
            command=self.destroy
        ).pack(side="right")

        ttk.Button(
            button_row,
            text="Save",
            command=self.save
        ).pack(side="right", padx=(0, 8))

        self.bind("<Return>", lambda event: self.save())

    def save(self):
        try:
            name = self.name_var.get().strip()

            if not name:
                raise ValueError("Name is required.")

            self.save_callback(name)

            messagebox.showinfo("Saved", "Record saved successfully.")
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))

class ClientsPage(ttk.Frame):
    def __init__(self, parent, app: PanaloApp):
        super().__init__(parent)

        self.app = app
        self.clients_cache = []
        self.search_var = tk.StringVar()

        self.build_ui()
        self.load_clients()

    def build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            header,
            text="Clients",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Add Client",
            command=self.open_add_client_window
        ).pack(side="right")

        search_bar = ttk.Frame(self)
        search_bar.pack(fill="x", pady=(0, 10))

        ttk.Label(search_bar, text="Search").pack(side="left")

        search_entry = ttk.Entry(
            search_bar,
            textvariable=self.search_var,
            width=35
        )
        search_entry.pack(side="left", padx=(8, 8))

        ttk.Button(
            search_bar,
            text="Search",
            command=self.search_clients
        ).pack(side="left")

        ttk.Button(
            search_bar,
            text="Clear",
            command=self.clear_search
        ).pack(side="left", padx=(8, 0))

        columns = (
            "id",
            "full_name",
            "contact_number",
            "notes",
            "created_at"
        )

        self.table = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=15
        )

        self.table.heading("id", text="ID")
        self.table.heading("full_name", text="Client Name")
        self.table.heading("contact_number", text="Contact")
        self.table.heading("notes", text="Notes")
        self.table.heading("created_at", text="Created At")

        self.table.column("id", width=50)
        self.table.column("full_name", width=220)
        self.table.column("contact_number", width=140)
        self.table.column("notes", width=350)
        self.table.column("created_at", width=150)

        self.table.pack(fill="both", expand=True)

        action_bar = ttk.Frame(self)
        action_bar.pack(fill="x", pady=(12, 0))

        ttk.Button(
            action_bar,
            text="Edit Selected Client",
            command=self.open_edit_client_window
        ).pack(side="left")

        ttk.Button(
            action_bar,
            text="Refresh",
            command=self.load_clients
        ).pack(side="right")

        self.bind_all("<Return>", lambda event: self.search_clients())

    def load_clients(self):
        for item in self.table.get_children():
            self.table.delete(item)

        self.clients_cache = self.app.client_service.list_clients()

        for client in self.clients_cache:
            self.table.insert(
                "",
                "end",
                values=(
                    client["id"],
                    client["full_name"],
                    client["contact_number"] or "",
                    client["notes"] or "",
                    client["created_at"] or ""
                )
            )

    def search_clients(self):
        keyword = self.search_var.get().strip()

        for item in self.table.get_children():
            self.table.delete(item)

        self.clients_cache = self.app.client_service.list_clients(keyword)

        for client in self.clients_cache:
            self.table.insert(
                "",
                "end",
                values=(
                    client["id"],
                    client["full_name"],
                    client["contact_number"] or "",
                    client["notes"] or "",
                    client["created_at"] or ""
                )
            )

    def clear_search(self):
        self.search_var.set("")
        self.load_clients()

    def get_selected_client(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning("No Selection", "Please select a client first.")
            return None

        values = self.table.item(selected[0], "values")
        client_id = int(values[0])

        client = self.app.client_service.get_client_by_id(client_id)

        if not client:
            messagebox.showerror("Error", "Client record not found.")
            return None

        return client

    def open_add_client_window(self):
        ClientFormWindow(
            app=self.app,
            parent_page=self,
            mode="add"
        )

    def open_edit_client_window(self):
        client = self.get_selected_client()

        if not client:
            return

        ClientFormWindow(
            app=self.app,
            parent_page=self,
            mode="edit",
            client=client
        )

class DatePickerWindow(tk.Toplevel):
    def __init__(self, app: PanaloApp, target_var: tk.StringVar, initial_date=None, exclude_booking_id=None):
        super().__init__()

        self.app = app
        self.target_var = target_var
        self.exclude_booking_id = exclude_booking_id

        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.minimum_date = today + timedelta(days=3)

        if initial_date:
            try:
                parsed = datetime.strptime(initial_date, "%Y-%m-%d").date()
                self.current_year = parsed.year
                self.current_month = parsed.month
            except Exception:
                pass

        self.title("Select Event Date")
        self.geometry("430x420")
        self.resizable(False, False)

        self.build_ui()
        self.render_calendar()

    def build_ui(self):
        main = ttk.Frame(self, padding=15)
        main.pack(fill="both", expand=True)

        nav = ttk.Frame(main)
        nav.pack(fill="x", pady=(0, 10))

        ttk.Button(
            nav,
            text="‹",
            width=4,
            command=self.previous_month
        ).pack(side="left")

        self.month_label = ttk.Label(
            nav,
            text="",
            font=("Segoe UI", 14, "bold")
        )
        self.month_label.pack(side="left", expand=True)

        ttk.Button(
            nav,
            text="›",
            width=4,
            command=self.next_month
        ).pack(side="right")

        self.calendar_frame = ttk.Frame(main)
        self.calendar_frame.pack(fill="both", expand=True)

        legend = ttk.Frame(main)
        legend.pack(fill="x", pady=(10, 0))

        tk.Label(
            legend,
            text="Available",
            bg="white",
            width=12,
            relief="solid",
            bd=1
        ).pack(side="left", padx=(0, 8))

        tk.Label(
            legend,
            text="Unavailable",
            bg="#f8d7da",
            width=12,
            relief="solid",
            bd=1
        ).pack(side="left")

    def previous_month(self):
        self.current_month -= 1

        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1

        self.render_calendar()

    def next_month(self):
        self.current_month += 1

        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1

        self.render_calendar()

    def get_booked_dates_for_month(self):
        schedules = self.app.schedule_service.list_schedules_for_month(
            self.current_year,
            self.current_month
        )

        booked_dates = set()

        for sched in schedules:
            status = (sched["status"] or "").lower()

            if status == "cancelled":
                continue

            if self.exclude_booking_id and sched["id"] == self.exclude_booking_id:
                continue

            if sched["event_date"]:
                booked_dates.add(sched["event_date"])

        return booked_dates

    def render_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.month_label.config(
            text=f"{calendar.month_name[self.current_month]} {self.current_year}"
        )

        booked_dates = self.get_booked_dates_for_month()

        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        for col, day_name in enumerate(day_names):
            ttk.Label(
                self.calendar_frame,
                text=day_name,
                anchor="center",
                font=("Segoe UI", 9, "bold")
            ).grid(row=0, column=col, sticky="nsew", padx=2, pady=2)

        cal = calendar.Calendar(firstweekday=6)
        weeks = cal.monthdayscalendar(self.current_year, self.current_month)

        for row_index, week in enumerate(weeks, start=1):
            for col_index, day_number in enumerate(week):
                if day_number == 0:
                    ttk.Label(self.calendar_frame, text="").grid(
                        row=row_index,
                        column=col_index,
                        sticky="nsew",
                        padx=2,
                        pady=2
                    )
                    continue

                current_date = date(
                    self.current_year,
                    self.current_month,
                    day_number
                )

                date_key = current_date.strftime("%Y-%m-%d")

                is_too_soon = current_date < self.minimum_date
                is_booked = date_key in booked_dates
                is_unavailable = is_too_soon or is_booked

                bg_color = "#f8d7da" if is_unavailable else "white"
                fg_color = "#842029" if is_unavailable else "black"

                btn = tk.Button(
                    self.calendar_frame,
                    text=str(day_number),
                    bg=bg_color,
                    fg=fg_color,
                    relief="solid",
                    bd=1,
                    width=6,
                    height=2,
                    command=lambda selected=current_date, unavailable=is_unavailable: self.select_date(selected, unavailable)
                )
                btn.grid(
                    row=row_index,
                    column=col_index,
                    sticky="nsew",
                    padx=2,
                    pady=2
                )

        for col in range(7):
            self.calendar_frame.columnconfigure(col, weight=1)

    def select_date(self, selected_date, unavailable):
        if unavailable:
            messagebox.showwarning(
                "Unavailable Date",
                "This date cannot be selected. It may be too soon or already booked."
            )
            return

        self.target_var.set(selected_date.strftime("%Y-%m-%d"))
        self.destroy()

class ClientFormWindow(tk.Toplevel):
    def __init__(self, app: PanaloApp, parent_page: ClientsPage, mode: str, client=None):
        super().__init__()

        self.app = app
        self.parent_page = parent_page
        self.mode = mode
        self.client = client

        self.title("Add Client" if mode == "add" else "Edit Client")
        self.geometry("520x420")
        self.resizable(False, False)

        self.full_name_var = tk.StringVar(value=client["full_name"] if client else "")
        self.contact_number_var = tk.StringVar(value=client["contact_number"] if client else "")

        self.build_ui()

    def build_ui(self):
        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Add Client" if self.mode == "add" else "Edit Client",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(0, 15))

        ttk.Label(container, text="Client Full Name").pack(anchor="w")
        ttk.Entry(
            container,
            textvariable=self.full_name_var
        ).pack(fill="x", pady=(3, 10))

        ttk.Label(container, text="Contact Number").pack(anchor="w")
        ttk.Entry(
            container,
            textvariable=self.contact_number_var
        ).pack(fill="x", pady=(3, 10))

        ttk.Label(container, text="Notes").pack(anchor="w")
        self.notes_box = tk.Text(container, height=7, wrap="word")
        self.notes_box.pack(fill="both", expand=True, pady=(3, 15))

        if self.client:
            self.notes_box.insert("1.0", self.client["notes"] or "")

        button_row = ttk.Frame(container)
        button_row.pack(fill="x")

        ttk.Button(
            button_row,
            text="Cancel",
            command=self.destroy
        ).pack(side="right")

        ttk.Button(
            button_row,
            text="Confirm",
            command=self.save_client
        ).pack(side="right", padx=(0, 8))

    def save_client(self):
        try:
            if self.mode == "add":
                self.app.client_service.add_client(
                    full_name=self.full_name_var.get(),
                    contact_number=self.contact_number_var.get(),
                    event_type_id=None,
                    event_date="",
                    event_location="",
                    guest_count=None,
                    theme_motif="",
                    preferred_package="",
                    status_id=None,
                    notes=self.notes_box.get("1.0", "end").strip(),
                    created_by=self.app.current_user.id
                )

                messagebox.showinfo("Success", "Client added successfully.")

            else:
                self.app.client_service.update_client(
                    client_id=self.client["id"],
                    full_name=self.full_name_var.get(),
                    contact_number=self.contact_number_var.get(),
                    event_type_id=None,
                    event_date="",
                    event_location="",
                    guest_count=None,
                    theme_motif="",
                    preferred_package="",
                    status_id=None,
                    notes=self.notes_box.get("1.0", "end").strip(),
                    actor_id=self.app.current_user.id
                )

                messagebox.showinfo("Success", "Client updated successfully.")

            self.parent_page.load_clients()
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))

class PackagesPage(ttk.Frame):
    def __init__(self, parent, app: PanaloApp):
        super().__init__(parent)

        self.app = app
        self.packages_cache = []
        self.search_var = tk.StringVar()

        self.build_ui()
        self.load_packages()

    def build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            header,
            text="Packages",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Add Package",
            command=self.open_add_package_window
        ).pack(side="right")

        search_bar = ttk.Frame(self)
        search_bar.pack(fill="x", pady=(0, 10))

        ttk.Label(search_bar, text="Search").pack(side="left")

        search_entry = ttk.Entry(
            search_bar,
            textvariable=self.search_var,
            width=35
        )
        search_entry.pack(side="left", padx=(8, 8))

        ttk.Button(
            search_bar,
            text="Search",
            command=self.search_packages
        ).pack(side="left")

        ttk.Button(
            search_bar,
            text="Clear",
            command=self.clear_search
        ).pack(side="left", padx=(8, 0))

        columns = (
            "id",
            "package_name",
            "recommended_pax",
            "min_price",
            "max_price"
        )

        self.table = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=15
        )

        self.table.heading("id", text="ID")
        self.table.heading("package_name", text="Package Name")
        self.table.heading("recommended_pax", text="Recommended Pax")
        self.table.heading("min_price", text="Min Price")
        self.table.heading("max_price", text="Max Price")

        self.table.column("id", width=50)
        self.table.column("package_name", width=280)
        self.table.column("recommended_pax", width=160)
        self.table.column("min_price", width=120)
        self.table.column("max_price", width=120)

        self.table.pack(fill="both", expand=True)

        action_bar = ttk.Frame(self)
        action_bar.pack(fill="x", pady=(12, 0))

        ttk.Button(
            action_bar,
            text="Edit Selected Package",
            command=self.open_edit_package_window
        ).pack(side="left")

        ttk.Button(
            action_bar,
            text="Refresh",
            command=self.load_packages
        ).pack(side="right")

        self.bind_all("<Return>", lambda event: self.search_packages())

    def format_price(self, value):
        if value is None or value == "":
            return ""

        try:
            return f"₱{float(value):,.2f}"
        except ValueError:
            return str(value)

    def load_packages(self):
        for item in self.table.get_children():
            self.table.delete(item)

        self.packages_cache = self.app.package_service.list_packages()

        for package in self.packages_cache:
            self.table.insert(
                "",
                "end",
                values=(
                    package["id"],
                    package["package_name"],
                    package["recommended_pax"] or "",
                    self.format_price(package["min_price"]),
                    self.format_price(package["max_price"])
                )
            )

    def search_packages(self):
        keyword = self.search_var.get().strip()

        for item in self.table.get_children():
            self.table.delete(item)

        self.packages_cache = self.app.package_service.list_packages(keyword)

        for package in self.packages_cache:
            self.table.insert(
                "",
                "end",
                values=(
                    package["id"],
                    package["package_name"],
                    package["recommended_pax"] or "",
                    self.format_price(package["min_price"]),
                    self.format_price(package["max_price"])
                )
            )

    def clear_search(self):
        self.search_var.set("")
        self.load_packages()

    def get_selected_package(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning("No Selection", "Please select a package first.")
            return None

        values = self.table.item(selected[0], "values")
        package_id = int(values[0])

        package = self.app.package_service.get_package_by_id(package_id)

        if not package:
            messagebox.showerror("Error", "Package record not found.")
            return None

        return package

    def open_add_package_window(self):
        PackageFormWindow(
            app=self.app,
            parent_page=self,
            mode="add"
        )

    def open_edit_package_window(self):
        package = self.get_selected_package()

        if not package:
            return

        PackageFormWindow(
            app=self.app,
            parent_page=self,
            mode="edit",
            package=package
        )

class PackageFormWindow(tk.Toplevel):
    def __init__(self, app: PanaloApp, parent_page: PackagesPage, mode: str, package=None):
        super().__init__()

        self.app = app
        self.parent_page = parent_page
        self.mode = mode
        self.package = package

        self.title("Add Package" if mode == "add" else "Edit Package")
        self.geometry("560x650")
        self.resizable(False, False)

        self.package_name_var = tk.StringVar(value=package["package_name"] if package else "")
        self.recommended_pax_var = tk.StringVar(value=package["recommended_pax"] if package else "")
        self.min_price_var = tk.StringVar(value=str(package["min_price"]) if package and package["min_price"] is not None else "")
        self.max_price_var = tk.StringVar(value=str(package["max_price"]) if package and package["max_price"] is not None else "")

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Add Package" if self.mode == "add" else "Edit Package",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(0, 15))

        ttk.Label(frame, text="Package Name").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.package_name_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Recommended Pax").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.recommended_pax_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Minimum Price").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.min_price_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Maximum Price").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.max_price_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Description").pack(anchor="w")
        self.description_box = tk.Text(frame, height=5, wrap="word")
        self.description_box.pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Inclusions").pack(anchor="w")
        self.inclusions_box = tk.Text(frame, height=10, wrap="word")
        self.inclusions_box.pack(fill="x", pady=(3, 15))

        if self.package:
            self.description_box.insert("1.0", self.package["description"] or "")
            self.inclusions_box.insert("1.0", self.package["inclusions"] or "")

        ttk.Button(
            frame,
            text="Save Package",
            command=self.save_package
        ).pack(fill="x")

    def get_price_value(self, value, label):
        value = value.strip()

        if not value:
            return None

        try:
            return float(value)
        except ValueError:
            raise ValueError(f"{label} must be a valid number.")

    def save_package(self):
        try:
            min_price = self.get_price_value(
                self.min_price_var.get(),
                "Minimum price"
            )

            max_price = self.get_price_value(
                self.max_price_var.get(),
                "Maximum price"
            )

            if self.mode == "add":
                self.app.package_service.add_package(
                    package_name=self.package_name_var.get(),
                    recommended_pax=self.recommended_pax_var.get(),
                    description=self.description_box.get("1.0", "end").strip(),
                    inclusions=self.inclusions_box.get("1.0", "end").strip(),
                    min_price=min_price,
                    max_price=max_price,
                    created_by=self.app.current_user.id
                )

                messagebox.showinfo("Success", "Package added successfully.")

            else:
                self.app.package_service.update_package(
                    package_id=self.package["id"],
                    package_name=self.package_name_var.get(),
                    recommended_pax=self.recommended_pax_var.get(),
                    description=self.description_box.get("1.0", "end").strip(),
                    inclusions=self.inclusions_box.get("1.0", "end").strip(),
                    min_price=min_price,
                    max_price=max_price,
                    actor_id=self.app.current_user.id
                )

                messagebox.showinfo("Success", "Package updated successfully.")

            self.parent_page.load_packages()
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))

class BookingsPage(ttk.Frame):
    def __init__(self, parent, app: PanaloApp):
        super().__init__(parent)

        self.app = app
        self.bookings_cache = []
        self.search_var = tk.StringVar()

        self.build_ui()
        self.load_bookings()

    def build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            header,
            text="Bookings",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Add Booking",
            command=self.open_add_booking_window
        ).pack(side="right")

        search_bar = ttk.Frame(self)
        search_bar.pack(fill="x", pady=(0, 10))

        ttk.Label(search_bar, text="Search").pack(side="left")

        ttk.Entry(
            search_bar,
            textvariable=self.search_var,
            width=35
        ).pack(side="left", padx=(8, 8))

        ttk.Button(
            search_bar,
            text="Search",
            command=self.search_bookings
        ).pack(side="left")

        ttk.Button(
            search_bar,
            text="Clear",
            command=self.clear_search
        ).pack(side="left", padx=(8, 0))

        columns = (
            "id",
            "client_name",
            "package_name",
            "event_type",
            "event_date",
            "event_time",
            "status",
            "total_amount",
            "balance_amount"
        )

        self.table = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=15
        )

        self.table.heading("id", text="ID")
        self.table.heading("client_name", text="Client")
        self.table.heading("package_name", text="Package")
        self.table.heading("event_type", text="Event Type")
        self.table.heading("event_date", text="Date")
        self.table.heading("event_time", text="Time")
        self.table.heading("status", text="Status")
        self.table.heading("total_amount", text="Total")
        self.table.heading("balance_amount", text="Balance")

        self.table.column("id", width=50)
        self.table.column("client_name", width=150)
        self.table.column("package_name", width=200)
        self.table.column("event_type", width=130)
        self.table.column("event_date", width=100)
        self.table.column("event_time", width=90)
        self.table.column("status", width=120)
        self.table.column("total_amount", width=100)
        self.table.column("balance_amount", width=100)

        self.table.pack(fill="both", expand=True)

        action_bar = ttk.Frame(self)
        action_bar.pack(fill="x", pady=(12, 0))

        ttk.Button(
            action_bar,
            text="Edit Selected Booking",
            command=self.open_edit_booking_window
        ).pack(side="left")

        ttk.Button(
            action_bar,
            text="Refresh",
            command=self.load_bookings
        ).pack(side="right")

    def format_price(self, value):
        if value is None or value == "":
            return ""

        try:
            return f"₱{float(value):,.2f}"
        except ValueError:
            return str(value)

    def load_bookings(self):
        for item in self.table.get_children():
            self.table.delete(item)

        self.bookings_cache = self.app.booking_service.list_bookings()

        for booking in self.bookings_cache:
            self.table.insert(
                "",
                "end",
                values=(
                    booking["id"],
                    booking["client_name"] or "",
                    booking["package_name"] or "",
                    booking["event_type"] or "",
                    booking["event_date"] or "",
                    booking["event_time"] or "",
                    booking["status"] or "",
                    self.format_price(booking["total_amount"]),
                    self.format_price(booking["balance_amount"])
                )
            )

    def search_bookings(self):
        keyword = self.search_var.get().strip()

        for item in self.table.get_children():
            self.table.delete(item)

        self.bookings_cache = self.app.booking_service.list_bookings(keyword)

        for booking in self.bookings_cache:
            self.table.insert(
                "",
                "end",
                values=(
                    booking["id"],
                    booking["client_name"] or "",
                    booking["package_name"] or "",
                    booking["event_type"] or "",
                    booking["event_date"] or "",
                    booking["event_time"] or "",
                    booking["status"] or "",
                    self.format_price(booking["total_amount"]),
                    self.format_price(booking["balance_amount"])
                )
            )

    def clear_search(self):
        self.search_var.set("")
        self.load_bookings()

    def get_selected_booking(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning("No Selection", "Please select a booking first.")
            return None

        values = self.table.item(selected[0], "values")
        booking_id = int(values[0])

        booking = self.app.booking_service.get_booking_by_id(booking_id)

        if not booking:
            messagebox.showerror("Error", "Booking record not found.")
            return None

        return booking

    def open_add_booking_window(self):
        BookingFormWindow(
            app=self.app,
            parent_page=self,
            mode="add"
        )

    def open_edit_booking_window(self):
        booking = self.get_selected_booking()

        if not booking:
            return

        BookingFormWindow(
            app=self.app,
            parent_page=self,
            mode="edit",
            booking=booking
        )

class BookingFormWindow(tk.Toplevel):
    def __init__(self, app: PanaloApp, parent_page: BookingsPage, mode: str, booking=None):
        super().__init__()

        self.app = app
        self.parent_page = parent_page
        self.mode = mode
        self.booking = booking

        self.client_options = []
        self.package_options = []
        self.event_type_options = []
        self.status_options = []

        self.title("Add Booking" if mode == "add" else "Edit Booking")
        self.geometry("760x620")
        self.minsize(720, 560)
        self.resizable(True, True)

        self.client_var = tk.StringVar()
        self.package_var = tk.StringVar()
        self.event_type_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.event_date_var = tk.StringVar(value=booking["event_date"] if booking else "")
        self.event_time_var = tk.StringVar(value=booking["event_time"] if booking else "")
        self.event_location_var = tk.StringVar(value=booking["event_location"] if booking else "")
        self.guest_count_var = tk.StringVar(
            value=str(booking["guest_count"]) if booking and booking["guest_count"] is not None else "1"
        )
        self.theme_motif_var = tk.StringVar(value=booking["theme_motif"] if booking else "")
        self.total_amount_var = tk.StringVar(
            value=str(booking["total_amount"]) if booking and booking["total_amount"] is not None else "0"
        )
        self.down_payment_var = tk.StringVar(
            value=str(booking["down_payment_amount"]) if booking and booking["down_payment_amount"] is not None else "0"
        )
        self.balance_var = tk.StringVar(
            value=str(booking["balance_amount"]) if booking and booking["balance_amount"] is not None else "0"
        )

        self.load_dropdown_options()
        self.build_ui()
        self.set_existing_dropdown_values()
        self.update_balance_preview()

    def load_dropdown_options(self):
        exclude_booking_id = self.booking["id"] if self.booking else None

        self.client_options = self.app.client_service.list_clients_available_for_booking(
            exclude_booking_id=exclude_booking_id
        )

        self.package_options = self.app.package_service.list_packages()
        self.event_type_options = self.app.settings_service.list_event_types()
        self.status_options = self.app.settings_service.list_booking_statuses()

    def build_ui(self):
        outer = ttk.Frame(self, padding=16)
        outer.pack(fill="both", expand=True)

        ttk.Label(
            outer,
            text="Add Booking" if self.mode == "add" else "Edit Booking",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(0, 12))

        body = ttk.Frame(outer)
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # LEFT COLUMN

        ttk.Label(left, text="Client").pack(anchor="w")
        self.client_combo = ttk.Combobox(
            left,
            textvariable=self.client_var,
            values=[self.format_client_option(item) for item in self.client_options],
            state="readonly"
        )
        self.client_combo.pack(fill="x", pady=(3, 10))

        ttk.Label(left, text="Package").pack(anchor="w")
        self.package_combo = ttk.Combobox(
            left,
            textvariable=self.package_var,
            values=[self.format_package_option(item) for item in self.package_options],
            state="readonly"
        )
        self.package_combo.pack(fill="x", pady=(3, 10))
        self.package_combo.bind("<<ComboboxSelected>>", lambda event: self.auto_fill_package_price())

        ttk.Label(left, text="Event Type").pack(anchor="w")
        self.event_type_combo = ttk.Combobox(
            left,
            textvariable=self.event_type_var,
            values=[item["name"] for item in self.event_type_options],
            state="readonly"
        )
        self.event_type_combo.pack(fill="x", pady=(3, 10))

        ttk.Label(left, text="Status").pack(anchor="w")
        self.status_combo = ttk.Combobox(
            left,
            textvariable=self.status_var,
            values=[item["name"] for item in self.status_options],
            state="readonly"
        )
        self.status_combo.pack(fill="x", pady=(3, 10))

        ttk.Label(left, text="Event Date").pack(anchor="w")
        date_row = ttk.Frame(left)
        date_row.pack(fill="x", pady=(3, 4))

        ttk.Entry(
            date_row,
            textvariable=self.event_date_var,
            state="readonly"
        ).pack(side="left", fill="x", expand=True)

        ttk.Button(
            date_row,
            text="Select Date",
            command=self.open_date_picker
        ).pack(side="left", padx=(8, 0))

        ttk.Label(
            left,
            text="Only available dates can be selected. Minimum booking date is 3 days from today.",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(left, text="Event Time").pack(anchor="w")
        ttk.Combobox(
            left,
            textvariable=self.event_time_var,
            values=TIME_OPTIONS,
            state="readonly"
        ).pack(fill="x", pady=(3, 4))

        ttk.Label(
            left,
            text="Event time is required.",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 10))

        # RIGHT COLUMN

        ttk.Label(right, text="Event Location Address").pack(anchor="w")
        ttk.Entry(right, textvariable=self.event_location_var).pack(fill="x", pady=(3, 10))

        ttk.Label(right, text="Guest Count").pack(anchor="w")
        tk.Spinbox(
            right,
            from_=1,
            to=1000,
            textvariable=self.guest_count_var
        ).pack(fill="x", pady=(3, 10))

        ttk.Label(right, text="Theme / Motif").pack(anchor="w")
        ttk.Entry(right, textvariable=self.theme_motif_var).pack(fill="x", pady=(3, 10))

        ttk.Label(right, text="Total Amount").pack(anchor="w")
        ttk.Entry(
            right,
            textvariable=self.total_amount_var,
            state="readonly"
        ).pack(fill="x", pady=(3, 10))

        ttk.Label(right, text="Required Down Payment").pack(anchor="w")
        ttk.Entry(
            right,
            textvariable=self.down_payment_var,
            state="readonly"
        ).pack(fill="x", pady=(3, 10))

        ttk.Label(right, text="Balance").pack(anchor="w")
        ttk.Entry(
            right,
            textvariable=self.balance_var,
            state="readonly"
        ).pack(fill="x", pady=(3, 10))

        ttk.Label(right, text="Booking Notes").pack(anchor="w")
        self.notes_box = tk.Text(right, height=7, wrap="word")
        self.notes_box.pack(fill="both", expand=True, pady=(3, 0))

        if self.booking:
            self.notes_box.insert("1.0", self.booking["booking_notes"] or "")

        # Bottom action buttons - always visible
        button_row = ttk.Frame(outer)
        button_row.pack(fill="x", pady=(16, 0))

        ttk.Button(
            button_row,
            text="Cancel",
            command=self.destroy
        ).pack(side="right")

        ttk.Button(
            button_row,
            text="Confirm",
            command=self.save_booking
        ).pack(side="right", padx=(0, 8))

        self.total_amount_var.trace_add("write", lambda *args: self.update_balance_preview())
        self.down_payment_var.trace_add("write", lambda *args: self.update_balance_preview())

    def open_date_picker(self):
        exclude_booking_id = self.booking["id"] if self.booking else None

        DatePickerWindow(
            app=self.app,
            target_var=self.event_date_var,
            initial_date=self.event_date_var.get(),
            exclude_booking_id=exclude_booking_id
        )

    def format_client_option(self, client):
        return f"{client['id']} - {client['full_name']}"

    def format_package_option(self, package):
        return f"{package['id']} - {package['package_name']}"

    def get_selected_id_from_option(self, selected_value):
        if not selected_value:
            return None

        try:
            return int(selected_value.split(" - ")[0])
        except Exception:
            return None

    def set_existing_dropdown_values(self):
        if self.booking:
            for item in self.client_options:
                if item["id"] == self.booking["client_id"]:
                    self.client_var.set(self.format_client_option(item))
                    break

            for item in self.package_options:
                if item["id"] == self.booking["package_id"]:
                    self.package_var.set(self.format_package_option(item))
                    break

            for item in self.event_type_options:
                if item["id"] == self.booking["event_type_id"]:
                    self.event_type_var.set(item["name"])
                    break

            for item in self.status_options:
                if item["id"] == self.booking["status_id"]:
                    self.status_var.set(item["name"])
                    break

        else:
            if self.client_options:
                self.client_var.set(self.format_client_option(self.client_options[0]))

            if self.package_options:
                self.package_var.set(self.format_package_option(self.package_options[0]))
                self.auto_fill_package_price()

            if self.event_type_options:
                self.event_type_var.set(self.event_type_options[0]["name"])

            if self.status_options:
                for item in self.status_options:
                    if item["name"] == "Inquiry":
                        self.status_var.set(item["name"])
                        break

                if not self.status_var.get():
                    self.status_var.set(self.status_options[0]["name"])

            if not self.event_time_var.get() and TIME_OPTIONS:
                self.event_time_var.set(TIME_OPTIONS[0])

    def get_selected_event_type_id(self):
        selected_name = self.event_type_var.get()

        for item in self.event_type_options:
            if item["name"] == selected_name:
                return item["id"]

        return None

    def get_selected_status_id(self):
        selected_name = self.status_var.get()

        for item in self.status_options:
            if item["name"] == selected_name:
                return item["id"]

        return None

    def get_guest_count(self):
        value = self.guest_count_var.get().strip()

        if not value:
            return None

        try:
            guest_count = int(value)
        except ValueError:
            raise ValueError("Guest count must be a whole number.")

        if guest_count < 1:
            raise ValueError("Guest count must be at least 1.")

        return guest_count

    def get_money_value(self, value, label):
        value = value.strip()

        if not value:
            return 0.0

        try:
            return float(value)
        except ValueError:
            raise ValueError(f"{label} must be a valid number.")

    def update_balance_preview(self):
        try:
            total = float(self.total_amount_var.get() or 0)
            down = float(self.down_payment_var.get() or 0)
            balance = total - down

            if balance < 0:
                self.balance_var.set("Invalid")
            else:
                self.balance_var.set(f"{balance:.2f}")

        except ValueError:
            self.balance_var.set("Invalid")

    def auto_fill_package_price(self):
        package_id = self.get_selected_id_from_option(self.package_var.get())

        if not package_id:
            self.total_amount_var.set("0")
            self.down_payment_var.set("0")
            self.balance_var.set("0")
            return

        for package in self.package_options:
            if package["id"] == package_id:
                min_price = package["min_price"] or 0

                self.total_amount_var.set(str(min_price))

                try:
                    settings = self.app.settings_service.get_all_settings()
                    down_percentage = float(settings.get("down_payment_percentage", "50"))
                    down_amount = float(min_price) * (down_percentage / 100)
                    balance = float(min_price) - down_amount

                    self.down_payment_var.set(f"{down_amount:.2f}")
                    self.balance_var.set(f"{balance:.2f}")

                except Exception:
                    self.down_payment_var.set("0")
                    self.balance_var.set(str(min_price))

                break

    def save_booking(self):
        try:
            client_id = self.get_selected_id_from_option(self.client_var.get())
            package_id = self.get_selected_id_from_option(self.package_var.get())
            event_type_id = self.get_selected_event_type_id()
            status_id = self.get_selected_status_id()
            guest_count = self.get_guest_count()

            total_amount = self.get_money_value(
                self.total_amount_var.get(),
                "Total amount"
            )

            down_payment_amount = self.get_money_value(
                self.down_payment_var.get(),
                "Down payment amount"
            )

            if self.mode == "add":
                self.app.booking_service.add_booking(
                    client_id=client_id,
                    package_id=package_id,
                    event_type_id=event_type_id,
                    status_id=status_id,
                    event_date=self.event_date_var.get(),
                    event_time=self.event_time_var.get(),
                    event_location=self.event_location_var.get(),
                    guest_count=guest_count,
                    theme_motif=self.theme_motif_var.get(),
                    total_amount=total_amount,
                    down_payment_amount=down_payment_amount,
                    booking_notes=self.notes_box.get("1.0", "end").strip(),
                    created_by=self.app.current_user.id
                )

                messagebox.showinfo("Success", "Booking added successfully.")

            else:
                self.app.booking_service.update_booking(
                    booking_id=self.booking["id"],
                    client_id=client_id,
                    package_id=package_id,
                    event_type_id=event_type_id,
                    status_id=status_id,
                    event_date=self.event_date_var.get(),
                    event_time=self.event_time_var.get(),
                    event_location=self.event_location_var.get(),
                    guest_count=guest_count,
                    theme_motif=self.theme_motif_var.get(),
                    total_amount=total_amount,
                    down_payment_amount=down_payment_amount,
                    booking_notes=self.notes_box.get("1.0", "end").strip(),
                    actor_id=self.app.current_user.id
                )

                messagebox.showinfo("Success", "Booking updated successfully.")

            self.parent_page.load_bookings()
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))


class SchedulePage(ttk.Frame):
    def __init__(self, parent, app: PanaloApp):
        super().__init__(parent)

        self.app = app

        today = date.today()
        self.selected_date = today
        self.current_year = today.year
        self.current_month = today.month

        self.current_view = "month"
        self.search_var = tk.StringVar()

        self.selected_schedule_id = None

        self.build_ui()
        self.render_current_view()


    def build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 12))

        ttk.Label(
            header,
            text="Schedule",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Refresh",
            command=self.render_current_view
        ).pack(side="right")

        nav_bar = ttk.Frame(self)
        nav_bar.pack(fill="x", pady=(0, 10))

        ttk.Button(
            nav_bar,
            text="Today",
            command=self.go_today
        ).pack(side="left")

        ttk.Button(
            nav_bar,
            text="‹",
            width=4,
            command=self.previous_period
        ).pack(side="left", padx=(8, 2))

        ttk.Button(
            nav_bar,
            text="›",
            width=4,
            command=self.next_period
        ).pack(side="left", padx=(2, 15))

        self.title_label = ttk.Label(
            nav_bar,
            text="",
            font=("Segoe UI", 16, "bold")
        )
        self.title_label.pack(side="left")

        view_buttons = ttk.Frame(nav_bar)
        view_buttons.pack(side="right")

        ttk.Button(
            view_buttons,
            text="Month",
            command=lambda: self.change_view("month")
        ).pack(side="left", padx=2)

        ttk.Button(
            view_buttons,
            text="Week",
            command=lambda: self.change_view("week")
        ).pack(side="left", padx=2)

        ttk.Button(
            view_buttons,
            text="Day",
            command=lambda: self.change_view("day")
        ).pack(side="left", padx=2)

        ttk.Button(
            view_buttons,
            text="List",
            command=lambda: self.change_view("list")
        ).pack(side="left", padx=2)

        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill="both", expand=True)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def change_view(self, view_name):
        self.current_view = view_name

        if view_name == "month":
            self.current_year = self.selected_date.year
            self.current_month = self.selected_date.month

        self.render_current_view()

    def render_current_view(self):
        self.clear_content()

        if self.current_view == "month":
            self.render_month_view()
        elif self.current_view == "week":
            self.render_week_view()
        elif self.current_view == "day":
            self.render_day_view()
        elif self.current_view == "list":
            self.render_list_view()

    def go_today(self):
        today = date.today()
        self.selected_date = today
        self.current_year = today.year
        self.current_month = today.month
        self.render_current_view()

    def previous_period(self):
        if self.current_view == "month":
            self.current_month -= 1

            if self.current_month == 0:
                self.current_month = 12
                self.current_year -= 1

            self.selected_date = date(self.current_year, self.current_month, 1)

        elif self.current_view == "week":
            self.selected_date -= timedelta(days=7)

        elif self.current_view == "day":
            self.selected_date -= timedelta(days=1)

        elif self.current_view == "list":
            self.selected_date -= timedelta(days=30)

        self.render_current_view()

    def next_period(self):
        if self.current_view == "month":
            self.current_month += 1

            if self.current_month == 13:
                self.current_month = 1
                self.current_year += 1

            self.selected_date = date(self.current_year, self.current_month, 1)

        elif self.current_view == "week":
            self.selected_date += timedelta(days=7)

        elif self.current_view == "day":
            self.selected_date += timedelta(days=1)

        elif self.current_view == "list":
            self.selected_date += timedelta(days=30)

        self.render_current_view()

    def parse_date(self, date_text):
        try:
            return datetime.strptime(date_text, "%Y-%m-%d").date()
        except Exception:
            return None

    def format_schedule_text(self, schedule):
        event_time = schedule["event_time"] or "No time"
        client = schedule["client_name"] or "Client"
        return f"{event_time} - {client}"

    def get_schedule_colors(self, schedule):
        status = (schedule["status"] or "").lower()

        if status == "cancelled":
            return "#f8d7da", "#842029"

        if status == "completed":
            return "#d1e7dd", "#0f5132"

        if status == "booked":
            return "#dbeafe", "#1d4ed8"

        return "#e8f0fe", "#1a73e8"

    def get_week_dates(self):
        start = self.selected_date - timedelta(days=(self.selected_date.weekday() + 1) % 7)
        return [start + timedelta(days=i) for i in range(7)]


    def render_month_view(self):
        month_name = calendar.month_name[self.current_month]
        self.title_label.config(text=f"{month_name} {self.current_year}")

        calendar_frame = ttk.Frame(self.content_frame)
        calendar_frame.pack(fill="both", expand=True)

        schedules = self.app.schedule_service.list_schedules_for_month(
            self.current_year,
            self.current_month
        )

        schedules_by_date = {}

        for sched in schedules:
            event_date = sched["event_date"]

            if event_date:
                schedules_by_date.setdefault(event_date, []).append(sched)

        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        for col, day_name in enumerate(day_names):
            ttk.Label(
                calendar_frame,
                text=day_name,
                anchor="center",
                font=("Segoe UI", 10, "bold")
            ).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdayscalendar(self.current_year, self.current_month)

        today = date.today()

        for row_index, week in enumerate(month_days, start=1):
            for col_index, day_number in enumerate(week):
                cell_bg = "white"

                cell = tk.Frame(
                    calendar_frame,
                    bg=cell_bg,
                    relief="solid",
                    bd=1,
                    height=115
                )
                cell.grid(
                    row=row_index,
                    column=col_index,
                    sticky="nsew",
                    padx=1,
                    pady=1
                )
                cell.grid_propagate(False)

                if day_number == 0:
                    continue

                date_key = f"{self.current_year:04d}-{self.current_month:02d}-{day_number:02d}"
                cell_date = date(self.current_year, self.current_month, day_number)

                if cell_date == today:
                    cell.config(bg="#e8f0fe")
                    cell_bg = "#e8f0fe"

                day_label = tk.Label(
                    cell,
                    text=str(day_number),
                    bg=cell_bg,
                    fg="#1a73e8" if cell_date == today else "black",
                    anchor="w",
                    font=("Segoe UI", 10, "bold"),
                    cursor="hand2"
                )
                day_label.pack(anchor="nw", padx=5, pady=(4, 2))

                day_label.bind(
                    "<Button-1>",
                    lambda event, selected_date=cell_date: self.open_day_from_date(selected_date)
                )

                cell.bind(
                    "<Button-1>",
                    lambda event, selected_date=cell_date: self.open_day_from_date(selected_date)
                )

                day_schedules = schedules_by_date.get(date_key, [])

                for sched in day_schedules[:3]:
                    bg_color, fg_color = self.get_schedule_colors(sched)

                    event_label = tk.Label(
                        cell,
                        text=self.format_schedule_text(sched),
                        bg=bg_color,
                        fg=fg_color,
                        anchor="w",
                        font=("Segoe UI", 8),
                        cursor="hand2"
                    )
                    event_label.pack(fill="x", padx=4, pady=1)

                    event_label.bind(
                        "<Button-1>",
                        lambda event, selected_date=cell_date: self.open_day_from_date(selected_date)
                    )

                if len(day_schedules) > 3:
                    more_label = tk.Label(
                        cell,
                        text=f"+{len(day_schedules) - 3} more",
                        bg=cell_bg,
                        fg="#555555",
                        anchor="w",
                        font=("Segoe UI", 8),
                        cursor="hand2"
                    )
                    more_label.pack(fill="x", padx=4, pady=1)

                    more_label.bind(
                        "<Button-1>",
                        lambda event, selected_date=cell_date: self.open_day_from_date(selected_date)
                    )

        for col in range(7):
            calendar_frame.columnconfigure(col, weight=1)

        for row in range(7):
            calendar_frame.rowconfigure(row, weight=1)

    def render_week_view(self):
        week_dates = self.get_week_dates()
        start_date = week_dates[0]
        end_date = week_dates[-1]

        self.title_label.config(
            text=f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        )

        week_frame = ttk.Frame(self.content_frame)
        week_frame.pack(fill="both", expand=True)

        for col, day in enumerate(week_dates):
            day_header = tk.Frame(
                week_frame,
                bg="#f8f9fa",
                relief="solid",
                bd=1
            )
            day_header.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

            tk.Label(
                day_header,
                text=day.strftime("%a\n%b %d"),
                bg="#f8f9fa",
                font=("Segoe UI", 10, "bold"),
                cursor="hand2"
            ).pack(fill="x", pady=6)

            day_body = tk.Frame(
                week_frame,
                bg="white",
                relief="solid",
                bd=1
            )
            day_body.grid(row=1, column=col, sticky="nsew", padx=1, pady=1)

            day_key = day.strftime("%Y-%m-%d")
            schedules = self.app.schedule_service.list_schedules_for_date(day_key)

            day_body.bind(
                "<Button-1>",
                lambda event, selected_date=day: self.open_day_from_date(selected_date)
            )

            for sched in schedules:
                bg_color, fg_color = self.get_schedule_colors(sched)

                event_card = tk.Label(
                    day_body,
                    text=self.format_schedule_text(sched),
                    bg=bg_color,
                    fg=fg_color,
                    anchor="w",
                    justify="left",
                    wraplength=120,
                    font=("Segoe UI", 8),
                    cursor="hand2"
                )

        for col in range(7):
            week_frame.columnconfigure(col, weight=1)

        week_frame.rowconfigure(1, weight=1)

    def render_day_view(self):
        selected_text = self.selected_date.strftime("%A, %B %d, %Y")
        self.title_label.config(text=selected_text)

        self.selected_schedule_id = None

        main = ttk.Frame(self.content_frame)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True)

        right = ttk.Frame(main, width=250)
        right.pack(side="right", fill="y", padx=(15, 0))
        right.pack_propagate(False)

        date_key = self.selected_date.strftime("%Y-%m-%d")
        schedules = self.app.schedule_service.list_schedules_for_date(date_key)

        columns = (
            "id",
            "time",
            "client",
            "event_type",
            "package",
            "location",
            "status"
        )

        self.day_table = ttk.Treeview(
            left,
            columns=columns,
            show="headings",
            height=16
        )

        self.day_table.tag_configure("cancelled", background="#f8d7da", foreground="#842029")
        self.day_table.tag_configure("completed", background="#d1e7dd", foreground="#0f5132")
        self.day_table.tag_configure("normal", background="white", foreground="black")

        self.day_table.heading("id", text="ID")
        self.day_table.heading("time", text="Time")
        self.day_table.heading("client", text="Client")
        self.day_table.heading("event_type", text="Event Type")
        self.day_table.heading("package", text="Package")
        self.day_table.heading("location", text="Location")
        self.day_table.heading("status", text="Status")

        self.day_table.column("id", width=50)
        self.day_table.column("time", width=90)
        self.day_table.column("client", width=150)
        self.day_table.column("event_type", width=130)
        self.day_table.column("package", width=180)
        self.day_table.column("location", width=200)
        self.day_table.column("status", width=110)

        self.day_table.pack(fill="both", expand=True)

        for sched in schedules:
            status_text = (sched["status"] or "").lower()

            if status_text == "cancelled":
                tag = "cancelled"
            elif status_text == "completed":
                tag = "completed"
            else:
                tag = "normal"

            self.day_table.insert(
                "",
                "end",
                values=(
                    sched["id"],
                    sched["event_time"] or "",
                    sched["client_name"] or "",
                    sched["event_type"] or "",
                    sched["package_name"] or "",
                    sched["event_location"] or "",
                    sched["status"] or ""
                ),
                tags=(tag,)
            )

        self.day_table.bind("<<TreeviewSelect>>", self.handle_day_selection)

        ttk.Label(
            right,
            text="Actions",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 10))

        ttk.Button(
            right,
            text="View Details",
            command=self.view_selected_details
        ).pack(fill="x", pady=4)

        ttk.Button(
            right,
            text="Reschedule",
            command=self.open_reschedule_window
        ).pack(fill="x", pady=4)

        ttk.Button(
            right,
            text="Cancel Schedule",
            command=self.cancel_selected_schedule
        ).pack(fill="x", pady=4)

        ttk.Button(
            right,
            text="Refresh Day",
            command=self.render_current_view
        ).pack(fill="x", pady=(20, 4))

        ttk.Label(
            right,
            text="Tip: Select a schedule from the table first.",
            wraplength=220,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(20, 0))

    def handle_day_selection(self, event=None):
        selected = self.day_table.selection()

        if not selected:
            self.selected_schedule_id = None
            return

        values = self.day_table.item(selected[0], "values")
        self.selected_schedule_id = int(values[0])

    def render_list_view(self):
        self.title_label.config(text="All Schedules")

        top = ttk.Frame(self.content_frame)
        top.pack(fill="x", pady=(0, 10))

        ttk.Label(top, text="Search").pack(side="left")

        ttk.Entry(
            top,
            textvariable=self.search_var,
            width=35
        ).pack(side="left", padx=(8, 8))

        ttk.Button(
            top,
            text="Search",
            command=self.search_list_view
        ).pack(side="left")

        ttk.Button(
            top,
            text="Clear",
            command=self.clear_list_search
        ).pack(side="left", padx=(8, 0))

        columns = (
            "id",
            "date",
            "time",
            "client",
            "event_type",
            "package",
            "location",
            "status"
        )

        self.list_table = ttk.Treeview(
            self.content_frame,
            columns=columns,
            show="headings",
            height=16
        )

        self.list_table.heading("id", text="ID")
        self.list_table.heading("date", text="Date")
        self.list_table.heading("time", text="Time")
        self.list_table.heading("client", text="Client")
        self.list_table.heading("event_type", text="Event Type")
        self.list_table.heading("package", text="Package")
        self.list_table.heading("location", text="Location")
        self.list_table.heading("status", text="Status")

        self.list_table.column("id", width=50)
        self.list_table.column("date", width=100)
        self.list_table.column("time", width=90)
        self.list_table.column("client", width=150)
        self.list_table.column("event_type", width=130)
        self.list_table.column("package", width=190)
        self.list_table.column("location", width=180)
        self.list_table.column("status", width=110)

        self.list_table.pack(fill="both", expand=True)

        action_bar = ttk.Frame(self.content_frame)
        action_bar.pack(fill="x", pady=(10, 0))

        ttk.Button(
            action_bar,
            text="Open Selected Day",
            command=self.open_selected_day_from_list
        ).pack(side="left")

        ttk.Button(
            action_bar,
            text="View Details",
            command=self.view_selected_details_from_list
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            action_bar,
            text="Refresh",
            command=self.render_current_view
        ).pack(side="right")

        self.load_list_table()

    def load_list_table(self, search_text=""):
        for item in self.list_table.get_children():
            self.list_table.delete(item)

        schedules = self.app.schedule_service.list_all_schedules(search_text)

        for sched in schedules:
            self.list_table.insert(
                "",
                "end",
                values=(
                    sched["id"],
                    sched["event_date"] or "",
                    sched["event_time"] or "",
                    sched["client_name"] or "",
                    sched["event_type"] or "",
                    sched["package_name"] or "",
                    sched["event_location"] or "",
                    sched["status"] or ""
                )
            )

    def search_list_view(self):
        self.load_list_table(self.search_var.get())

    def clear_list_search(self):
        self.search_var.set("")
        self.load_list_table()

    def open_day_from_date(self, selected_date):
        self.selected_date = selected_date
        self.current_view = "day"
        self.render_current_view()

    def open_selected_day_from_list(self):
        selected = self.list_table.selection()

        if not selected:
            messagebox.showwarning("No Selection", "Please select a schedule first.")
            return

        values = self.list_table.item(selected[0], "values")
        selected_date = self.parse_date(values[1])

        if not selected_date:
            messagebox.showerror("Error", "Selected schedule has no valid event date.")
            return

        self.open_day_from_date(selected_date)

    def get_selected_schedule_id_from_list(self):
        selected = self.list_table.selection()

        if not selected:
            messagebox.showwarning("No Selection", "Please select a schedule first.")
            return None

        values = self.list_table.item(selected[0], "values")
        return int(values[0])

    def view_selected_details_from_list(self):
        booking_id = self.get_selected_schedule_id_from_list()

        if not booking_id:
            return

        self.show_schedule_details(booking_id)

    def view_selected_details(self):
        if not self.selected_schedule_id:
            messagebox.showwarning("No Selection", "Please select a schedule first.")
            return

        self.show_schedule_details(self.selected_schedule_id)

    def show_schedule_details(self, booking_id):
        sched = self.app.schedule_service.get_schedule_by_booking_id(booking_id)

        if not sched:
            messagebox.showerror("Error", "Schedule not found.")
            return

        details = (
            f"Client: {sched['client_name'] or ''}\n"
            f"Event Type: {sched['event_type'] or ''}\n"
            f"Package: {sched['package_name'] or ''}\n"
            f"Date: {sched['event_date'] or ''}\n"
            f"Time: {sched['event_time'] or ''}\n"
            f"Location: {sched['event_location'] or ''}\n"
            f"Guest Count: {sched['guest_count'] or ''}\n"
            f"Theme / Motif: {sched['theme_motif'] or ''}\n"
            f"Status: {sched['status'] or ''}\n"
            f"Total Amount: {sched['total_amount'] or 0}\n"
            f"Down Payment: {sched['down_payment_amount'] or 0}\n"
            f"Balance: {sched['balance_amount'] or 0}\n\n"
            f"Notes:\n{sched['booking_notes'] or ''}"
        )

        messagebox.showinfo("Schedule Details", details)

    def open_reschedule_window(self):
        if not self.selected_schedule_id:
            messagebox.showwarning("No Selection", "Please select a schedule first.")
            return

        sched = self.app.schedule_service.get_schedule_by_booking_id(
            self.selected_schedule_id
        )

        if not sched:
            messagebox.showerror("Error", "Schedule not found.")
            return

        ScheduleRescheduleWindow(
            app=self.app,
            schedule=sched,
            refresh_callback=self.render_current_view
        )

    def cancel_selected_schedule(self):
        if not self.selected_schedule_id:
            messagebox.showwarning("No Selection", "Please select a schedule first.")
            return

        confirm = messagebox.askyesno(
            "Confirm Cancel",
            "Are you sure you want to cancel this schedule?"
        )

        if not confirm:
            return

        try:
            self.app.schedule_service.cancel_schedule(
                booking_id=self.selected_schedule_id,
                actor_id=self.app.current_user.id
            )

            messagebox.showinfo("Cancelled", "Schedule cancelled successfully.")
            self.render_current_view()

        except ValueError as e:
            messagebox.showerror("Error", str(e))

class ScheduleRescheduleWindow(tk.Toplevel):
    def __init__(self, app: PanaloApp, schedule, refresh_callback):
        super().__init__()

        self.app = app
        self.schedule = schedule
        self.refresh_callback = refresh_callback

        self.title("Reschedule Booking")
        self.geometry("460x320")
        self.resizable(False, False)

        self.date_var = tk.StringVar(value=schedule["event_date"] or "")
        self.time_var = tk.StringVar(value=schedule["event_time"] or "")

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Reschedule Booking",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(
            frame,
            text=f"Client: {self.schedule['client_name'] or ''}",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 15))

        ttk.Label(frame, text="New Event Date").pack(anchor="w")

        date_row = ttk.Frame(frame)
        date_row.pack(fill="x", pady=(3, 5))

        ttk.Entry(
            date_row,
            textvariable=self.date_var,
            state="readonly"
        ).pack(side="left", fill="x", expand=True)

        ttk.Button(
            date_row,
            text="Select Date",
            command=self.open_date_picker
        ).pack(side="left", padx=(8, 0))

        ttk.Label(
            frame,
            text="Only available dates can be selected. Minimum reschedule date is 3 days from today.",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 12))

        ttk.Label(frame, text="New Event Time").pack(anchor="w")

        ttk.Combobox(
            frame,
            textvariable=self.time_var,
            values=TIME_OPTIONS,
            state="readonly"
        ).pack(fill="x", pady=(3, 15))

        button_row = ttk.Frame(frame)
        button_row.pack(fill="x", pady=(15, 0))

        ttk.Button(
            button_row,
            text="Cancel",
            command=self.destroy
        ).pack(side="right")

        ttk.Button(
            button_row,
            text="Confirm",
            command=self.save_reschedule
        ).pack(side="right", padx=(0, 8))

    def open_date_picker(self):
        DatePickerWindow(
            app=self.app,
            target_var=self.date_var,
            initial_date=self.date_var.get(),
            exclude_booking_id=self.schedule["id"]
        )

    def save_reschedule(self):
        try:
            self.app.schedule_service.reschedule_booking(
                booking_id=self.schedule["id"],
                new_event_date=self.date_var.get(),
                new_event_time=self.time_var.get(),
                actor_id=self.app.current_user.id
            )

            messagebox.showinfo(
                "Success",
                "Booking schedule was updated successfully."
            )

            self.refresh_callback()
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))


class PaymentPage(ttk.Frame):
    def __init__(self, parent, app: PanaloApp):
        super().__init__(parent)

        self.app = app
        self.search_var = tk.StringVar()
        self.selected_booking_id = None
        self.selected_payment_id = None

        self.build_ui()
        self.load_booking_summaries()

    def build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            header,
            text="Payment",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Refresh",
            command=self.refresh_all
        ).pack(side="right")

        search_bar = ttk.Frame(self)
        search_bar.pack(fill="x", pady=(0, 10))

        ttk.Label(search_bar, text="Search Booking").pack(side="left")

        ttk.Entry(
            search_bar,
            textvariable=self.search_var,
            width=35
        ).pack(side="left", padx=(8, 8))

        ttk.Button(
            search_bar,
            text="Search",
            command=self.search_booking_summaries
        ).pack(side="left")

        ttk.Button(
            search_bar,
            text="Clear",
            command=self.clear_search
        ).pack(side="left", padx=(8, 0))

        main = ttk.Frame(self)
        main.pack(fill="both", expand=True)

        booking_frame = ttk.LabelFrame(main, text="Bookings / Payment Summary", padding=10)
        booking_frame.pack(fill="both", expand=True, pady=(0, 10))

        booking_columns = (
            "booking_id",
            "client_name",
            "event_date",
            "package_name",
            "total_amount",
            "net_paid",
            "balance",
            "payment_status"
        )

        self.booking_table = ttk.Treeview(
            booking_frame,
            columns=booking_columns,
            show="headings",
            height=9
        )

        self.booking_table.heading("booking_id", text="ID")
        self.booking_table.heading("client_name", text="Client")
        self.booking_table.heading("event_date", text="Event Date")
        self.booking_table.heading("package_name", text="Package")
        self.booking_table.heading("total_amount", text="Total")
        self.booking_table.heading("net_paid", text="Paid")
        self.booking_table.heading("balance", text="Balance")
        self.booking_table.heading("payment_status", text="Status")

        self.booking_table.column("booking_id", width=50)
        self.booking_table.column("client_name", width=150)
        self.booking_table.column("event_date", width=100)
        self.booking_table.column("package_name", width=220)
        self.booking_table.column("total_amount", width=100)
        self.booking_table.column("net_paid", width=100)
        self.booking_table.column("balance", width=100)
        self.booking_table.column("payment_status", width=100)

        self.booking_table.pack(fill="both", expand=True)
        self.booking_table.bind("<<TreeviewSelect>>", self.handle_booking_selection)

        payment_frame = ttk.LabelFrame(main, text="Payment History", padding=10)
        payment_frame.pack(fill="both", expand=True)

        payment_columns = (
            "id",
            "payment_type",
            "amount",
            "payment_method",
            "reference_number",
            "payment_date",
            "verification_status"
        )

        self.payment_table = ttk.Treeview(
            payment_frame,
            columns=payment_columns,
            show="headings",
            height=8
        )

        self.payment_table.heading("id", text="ID")
        self.payment_table.heading("payment_type", text="Type")
        self.payment_table.heading("amount", text="Amount")
        self.payment_table.heading("payment_method", text="Method")
        self.payment_table.heading("reference_number", text="Reference")
        self.payment_table.heading("payment_date", text="Date")
        self.payment_table.heading("verification_status", text="Verification")

        self.payment_table.column("id", width=50)
        self.payment_table.column("payment_type", width=130)
        self.payment_table.column("amount", width=100)
        self.payment_table.column("payment_method", width=120)
        self.payment_table.column("reference_number", width=150)
        self.payment_table.column("payment_date", width=100)
        self.payment_table.column("verification_status", width=120)

        self.payment_table.pack(fill="both", expand=True)
        self.payment_table.bind("<<TreeviewSelect>>", self.handle_payment_selection)

        action_bar = ttk.Frame(self)
        action_bar.pack(fill="x", pady=(12, 0))

        ttk.Button(
            action_bar,
            text="Add Payment",
            command=self.open_add_payment_window
        ).pack(side="left")

        ttk.Button(
            action_bar,
            text="Verify Selected Payment",
            command=self.verify_selected_payment
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            action_bar,
            text="Reject Selected Payment",
            command=self.reject_selected_payment
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            action_bar,
            text="Refresh",
            command=self.refresh_all
        ).pack(side="right")

    def format_price(self, value):
        try:
            return f"₱{float(value or 0):,.2f}"
        except Exception:
            return "₱0.00"



    def load_booking_summaries(self, search_text=""):
        for item in self.booking_table.get_children():
            self.booking_table.delete(item)

        summaries = self.app.payment_service.list_booking_payment_summaries(search_text)

        for item in summaries:
            self.booking_table.insert(
                "",
                "end",
                values=(
                    item["booking_id"],
                    item["client_name"] or "",
                    item["event_date"] or "",
                    item["package_name"] or "",
                    self.format_price(item["total_amount"]),
                    self.format_price(item["net_paid"]),
                    self.format_price(item["balance"]),
                    item["payment_status"]
                )
            )

    def load_payment_history(self):
        for item in self.payment_table.get_children():
            self.payment_table.delete(item)

        if not self.selected_booking_id:
            return

        payments = self.app.payment_service.list_payments_by_booking(
            self.selected_booking_id
        )

        for payment in payments:
            self.payment_table.insert(
                "",
                "end",
                values=(
                    payment["id"],
                    payment["payment_type"],
                    self.format_price(payment["amount"]),
                    payment["payment_method"] or "",
                    payment["reference_number"] or "",
                    payment["payment_date"] or "",
                    payment["verification_status"]
                )
            )

    def handle_booking_selection(self, event=None):
        selected = self.booking_table.selection()

        if not selected:
            self.selected_booking_id = None
            return

        values = self.booking_table.item(selected[0], "values")
        self.selected_booking_id = int(values[0])
        self.selected_payment_id = None
        self.load_payment_history()

    def handle_payment_selection(self, event=None):
        selected = self.payment_table.selection()

        if not selected:
            self.selected_payment_id = None
            return

        values = self.payment_table.item(selected[0], "values")
        self.selected_payment_id = int(values[0])

    def search_booking_summaries(self):
        self.load_booking_summaries(self.search_var.get())

    def clear_search(self):
        self.search_var.set("")
        self.load_booking_summaries()

    def refresh_all(self):
        current_booking = self.selected_booking_id
        self.load_booking_summaries(self.search_var.get())

        if current_booking:
            self.selected_booking_id = current_booking
            self.load_payment_history()

    def open_add_payment_window(self):
        if not self.selected_booking_id:
            messagebox.showwarning("No Booking Selected", "Please select a booking first.")
            return

        PaymentFormWindow(
            app=self.app,
            parent_page=self,
            booking_id=self.selected_booking_id
        )

    def verify_selected_payment(self):
        if not self.selected_payment_id:
            messagebox.showwarning("No Payment Selected", "Please select a payment first.")
            return

        confirm = messagebox.askyesno(
            "Confirm Verification",
            "Verify this payment?"
        )

        if not confirm:
            return

        try:
            self.app.payment_service.verify_payment(
                payment_id=self.selected_payment_id,
                actor_id=self.app.current_user.id
            )

            messagebox.showinfo("Verified", "Payment verified successfully.")
            self.refresh_all()

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def reject_selected_payment(self):
        if not self.selected_payment_id:
            messagebox.showwarning("No Payment Selected", "Please select a payment first.")
            return

        confirm = messagebox.askyesno(
            "Confirm Rejection",
            "Reject this payment?"
        )

        if not confirm:
            return

        try:
            self.app.payment_service.reject_payment(
                payment_id=self.selected_payment_id,
                actor_id=self.app.current_user.id
            )

            messagebox.showinfo("Rejected", "Payment rejected successfully.")
            self.refresh_all()

        except ValueError as e:
            messagebox.showerror("Error", str(e))
            
class SimpleDatePickerWindow(tk.Toplevel):
    def __init__(self, target_var: tk.StringVar, initial_date=None):
        super().__init__()

        self.target_var = target_var

        today = date.today()
        self.current_year = today.year
        self.current_month = today.month

        if initial_date:
            try:
                parsed = datetime.strptime(initial_date, "%Y-%m-%d").date()
                self.current_year = parsed.year
                self.current_month = parsed.month
            except Exception:
                pass

        self.title("Select Payment Date")
        self.geometry("420x380")
        self.resizable(False, False)

        self.build_ui()
        self.render_calendar()

    def build_ui(self):
        main = ttk.Frame(self, padding=15)
        main.pack(fill="both", expand=True)

        nav = ttk.Frame(main)
        nav.pack(fill="x", pady=(0, 10))

        ttk.Button(
            nav,
            text="‹",
            width=4,
            command=self.previous_month
        ).pack(side="left")

        self.month_label = ttk.Label(
            nav,
            text="",
            font=("Segoe UI", 14, "bold")
        )
        self.month_label.pack(side="left", expand=True)

        ttk.Button(
            nav,
            text="›",
            width=4,
            command=self.next_month
        ).pack(side="right")

        self.calendar_frame = ttk.Frame(main)
        self.calendar_frame.pack(fill="both", expand=True)

        ttk.Button(
            main,
            text="Use Today",
            command=self.use_today
        ).pack(fill="x", pady=(10, 0))

    def previous_month(self):
        self.current_month -= 1

        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1

        self.render_calendar()

    def next_month(self):
        self.current_month += 1

        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1

        self.render_calendar()

    def use_today(self):
        self.target_var.set(date.today().strftime("%Y-%m-%d"))
        self.destroy()

    def render_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.month_label.config(
            text=f"{calendar.month_name[self.current_month]} {self.current_year}"
        )

        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        for col, day_name in enumerate(day_names):
            ttk.Label(
                self.calendar_frame,
                text=day_name,
                anchor="center",
                font=("Segoe UI", 9, "bold")
            ).grid(row=0, column=col, sticky="nsew", padx=2, pady=2)

        cal = calendar.Calendar(firstweekday=6)
        weeks = cal.monthdayscalendar(self.current_year, self.current_month)

        today = date.today()

        for row_index, week in enumerate(weeks, start=1):
            for col_index, day_number in enumerate(week):
                if day_number == 0:
                    ttk.Label(self.calendar_frame, text="").grid(
                        row=row_index,
                        column=col_index,
                        sticky="nsew",
                        padx=2,
                        pady=2
                    )
                    continue

                current_date = date(
                    self.current_year,
                    self.current_month,
                    day_number
                )

                bg_color = "#e8f0fe" if current_date == today else "white"
                fg_color = "#1a73e8" if current_date == today else "black"

                btn = tk.Button(
                    self.calendar_frame,
                    text=str(day_number),
                    bg=bg_color,
                    fg=fg_color,
                    relief="solid",
                    bd=1,
                    width=6,
                    height=2,
                    command=lambda selected=current_date: self.select_date(selected)
                )
                btn.grid(
                    row=row_index,
                    column=col_index,
                    sticky="nsew",
                    padx=2,
                    pady=2
                )

        for col in range(7):
            self.calendar_frame.columnconfigure(col, weight=1)

    def select_date(self, selected_date):
        self.target_var.set(selected_date.strftime("%Y-%m-%d"))
        self.destroy()


class PaymentFormWindow(tk.Toplevel):
    def __init__(self, app: PanaloApp, parent_page: PaymentPage, booking_id: int):
        super().__init__()

        self.app = app
        self.parent_page = parent_page
        self.booking_id = booking_id

        self.summary = self.app.payment_service.get_booking_payment_summary(booking_id)

        if not self.summary:
            messagebox.showerror("Error", "Booking payment summary not found.")
            self.destroy()
            return

        self.title("Add Payment")
        self.geometry("720x540")
        self.minsize(680, 500)
        self.resizable(True, True)

        self.payment_type_var = tk.StringVar(value="Down Payment")
        self.amount_var = tk.StringVar()
        self.payment_method_var = tk.StringVar(value="GCash")
        self.reference_number_var = tk.StringVar()
        self.payment_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))

        self.build_ui()
        self.update_amount_by_type()

    def build_ui(self):
        # Main container uses grid so buttons stay visible at the bottom
        outer = ttk.Frame(self, padding=18)
        outer.pack(fill="both", expand=True)

        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        ttk.Label(
            outer,
            text="Add Payment",
            font=("Segoe UI", 18, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        body = ttk.Frame(outer)
        body.grid(row=1, column=0, sticky="nsew")

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left = ttk.LabelFrame(body, text="Booking Summary", padding=14)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        right = ttk.LabelFrame(body, text="Payment Details", padding=14)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        total_amount = float(self.summary["total_amount"] or 0)
        net_paid = float(self.summary["net_paid"] or 0)
        balance = float(self.summary["balance"] or 0)

        summary_text = (
            f"Booking ID: {self.booking_id}\n\n"
            f"Client:\n{self.summary['client_name'] or ''}\n\n"
            f"Package:\n{self.summary['package_name'] or ''}\n\n"
            f"Event Date:\n{self.summary['event_date'] or ''}\n\n"
            f"Total Amount:\n₱{total_amount:,.2f}\n\n"
            f"Verified Paid Amount:\n₱{net_paid:,.2f}\n\n"
            f"Remaining Balance:\n₱{balance:,.2f}\n\n"
            f"Payment Status:\n{self.summary['payment_status']}"
        )

        ttk.Label(
            left,
            text=summary_text,
            justify="left",
            font=("Segoe UI", 10)
        ).pack(anchor="nw")

        ttk.Label(right, text="Payment Type").pack(anchor="w")
        payment_combo = ttk.Combobox(
            right,
            textvariable=self.payment_type_var,
            values=[
                "Down Payment",
                "Full Payment",
                "Refund"
            ],
            state="readonly"
        )
        payment_combo.pack(fill="x", pady=(3, 10))
        payment_combo.bind("<<ComboboxSelected>>", lambda event: self.update_amount_by_type())

        ttk.Label(right, text="Amount").pack(anchor="w")
        ttk.Entry(
            right,
            textvariable=self.amount_var,
            state="readonly"
        ).pack(fill="x", pady=(3, 10))

        ttk.Label(right, text="Payment Method").pack(anchor="w")
        ttk.Combobox(
            right,
            textvariable=self.payment_method_var,
            values=[
                "Cash",
                "GCash",
                "Bank Transfer",
                "Maya",
                "Other"
            ],
            state="readonly"
        ).pack(fill="x", pady=(3, 10))

        ttk.Label(right, text="Reference Number").pack(anchor="w")
        ttk.Entry(
            right,
            textvariable=self.reference_number_var
        ).pack(fill="x", pady=(3, 10))

        ttk.Label(right, text="Payment Date").pack(anchor="w")

        date_row = ttk.Frame(right)
        date_row.pack(fill="x", pady=(3, 4))

        ttk.Entry(
            date_row,
            textvariable=self.payment_date_var,
            state="readonly"
        ).pack(side="left", fill="x", expand=True)

        ttk.Button(
            date_row,
            text="Select Date",
            command=self.open_payment_date_picker
        ).pack(side="left", padx=(8, 0))

        ttk.Label(
            right,
            text="Select the actual date the payment was received.",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(right, text="Notes").pack(anchor="w")
        self.notes_box = tk.Text(right, height=4, wrap="word")
        self.notes_box.pack(fill="both", expand=True, pady=(3, 0))

        # Fixed bottom action buttons
        button_row = ttk.Frame(outer)
        button_row.grid(row=2, column=0, sticky="ew", pady=(14, 0))

        ttk.Button(
            button_row,
            text="Cancel",
            command=self.destroy
        ).pack(side="right")

        ttk.Button(
            button_row,
            text="Confirm",
            command=self.save_payment
        ).pack(side="right", padx=(0, 8))

    def open_payment_date_picker(self):
        SimpleDatePickerWindow(
            target_var=self.payment_date_var,
            initial_date=self.payment_date_var.get()
        )

    def update_amount_by_type(self):
        payment_type = self.payment_type_var.get()

        total_amount = float(self.summary["total_amount"] or 0)
        balance = float(self.summary["balance"] or 0)
        net_paid = float(self.summary["net_paid"] or 0)

        if payment_type == "Down Payment":
            settings = self.app.settings_service.get_all_settings()
            down_percentage = float(settings.get("down_payment_percentage", "50"))
            required_down_payment = total_amount * (down_percentage / 100)

            amount = required_down_payment - net_paid

            if amount < 0:
                amount = 0

        elif payment_type == "Full Payment":
            amount = balance

        elif payment_type == "Refund":
            amount = self.app.payment_service.get_refundable_amount_by_booking(
                self.booking_id
            )

        else:
            amount = 0

        if amount < 0:
            amount = 0

        self.amount_var.set(f"{amount:.2f}")

    def get_amount(self):
        try:
            amount = float(self.amount_var.get() or 0)
        except ValueError:
            raise ValueError("Amount must be a valid number.")

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        return amount

    def validate_payment_before_save(self):
        payment_type = self.payment_type_var.get()
        balance = float(self.summary["balance"] or 0)

        if payment_type == "Full Payment" and balance <= 0:
            raise ValueError("This booking is already fully paid.")

        if payment_type == "Refund":
            refundable = self.app.payment_service.get_refundable_amount_by_booking(
                self.booking_id
            )

            if refundable <= 0:
                raise ValueError(
                    "No refundable amount available. Down payment is non-refundable."
                )

        if not self.payment_date_var.get().strip():
            raise ValueError("Payment date is required.")

    def save_payment(self):
        try:
            self.validate_payment_before_save()
            amount = self.get_amount()

            self.app.payment_service.add_payment(
                booking_id=self.booking_id,
                payment_type=self.payment_type_var.get(),
                amount=amount,
                payment_method=self.payment_method_var.get(),
                reference_number=self.reference_number_var.get(),
                payment_date=self.payment_date_var.get(),
                notes=self.notes_box.get("1.0", "end").strip(),
                created_by=self.app.current_user.id
            )

            messagebox.showinfo(
                "Payment Saved",
                "Payment recorded successfully. It is pending verification."
            )

            self.parent_page.refresh_all()
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))


class SettingsPage(ttk.Frame):
    def __init__(self, parent, app: PanaloApp):
        super().__init__(parent)

        self.app = app
        self.setting_vars = {}

        self.build_ui()
        self.load_settings()

    def build_ui(self):
        ttk.Label(
            self,
            text="Settings",
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w", pady=(0, 5))

        ttk.Label(
            self,
            text="Manage administrative system settings.",
            font=("Segoe UI", 11)
        ).pack(anchor="w", pady=(0, 15))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.business_tab = ttk.Frame(self.notebook, padding=20)
        self.payment_tab = ttk.Frame(self.notebook, padding=20)
        self.booking_tab = ttk.Frame(self.notebook, padding=20)
        self.event_types_tab = ttk.Frame(self.notebook, padding=20)
        self.booking_statuses_tab = ttk.Frame(self.notebook, padding=20)

        self.notebook.add(self.business_tab, text="Business Profile")
        self.notebook.add(self.payment_tab, text="Payment Policy")
        self.notebook.add(self.booking_tab, text="Booking Policy")
        self.notebook.add(self.event_types_tab, text="Event Types")
        self.notebook.add(self.booking_statuses_tab, text="Booking Statuses")

        self.build_business_tab()
        self.build_payment_tab()
        self.build_booking_tab()
        self.build_event_types_tab()
        self.build_booking_statuses_tab()

        action_bar = ttk.Frame(self)
        action_bar.pack(fill="x", pady=(15, 0))

        ttk.Button(
            action_bar,
            text="Save Settings",
            command=self.save_settings
        ).pack(side="right")

        ttk.Button(
            action_bar,
            text="Refresh",
            command=self.load_settings
        ).pack(side="right", padx=(0, 8))

    def create_input(self, parent, label, key):
        ttk.Label(parent, text=label).pack(anchor="w", pady=(0, 3))

        var = tk.StringVar()
        self.setting_vars[key] = var

        entry = ttk.Entry(parent, textvariable=var)
        entry.pack(fill="x", pady=(0, 10))

        return entry

    def create_combo(self, parent, label, key, values):
        ttk.Label(parent, text=label).pack(anchor="w", pady=(0, 3))

        var = tk.StringVar()
        self.setting_vars[key] = var

        combo = ttk.Combobox(
            parent,
            textvariable=var,
            values=values,
            state="readonly"
        )
        combo.pack(fill="x", pady=(0, 10))

        return combo

    def create_textbox(self, parent, label, key, height=4):
        ttk.Label(parent, text=label).pack(anchor="w", pady=(0, 3))

        textbox = tk.Text(parent, height=height, wrap="word")
        textbox.pack(fill="x", pady=(0, 10))

        self.setting_vars[key] = textbox

        return textbox

    def build_business_tab(self):
        self.create_input(
            self.business_tab,
            "Business Name",
            "business_name"
        )

        self.create_input(
            self.business_tab,
            "Business Tagline",
            "business_tagline"
        )

        self.create_input(
            self.business_tab,
            "Business Location",
            "business_location"
        )

        self.create_input(
            self.business_tab,
            "Contact Number",
            "business_contact"
        )

        self.create_input(
            self.business_tab,
            "Email Address",
            "business_email"
        )

        self.create_input(
            self.business_tab,
            "Facebook Page",
            "facebook_page"
        )

        self.create_input(
            self.business_tab,
            "Instagram Page",
            "instagram_page"
        )

    def build_payment_tab(self):
        self.create_input(
            self.payment_tab,
            "Default Down Payment Percentage",
            "down_payment_percentage"
        )

        self.create_input(
            self.payment_tab,
            "Full Payment Due Days Before Event",
            "full_payment_due_days"
        )

        self.create_combo(
            self.payment_tab,
            "Payment Verification Required",
            "payment_verification_required",
            ["Yes", "No"]
        )

        self.create_textbox(
            self.payment_tab,
            "Refund Policy",
            "refund_policy",
            height=5
        )

    def build_booking_tab(self):
        self.create_combo(
            self.booking_tab,
            "Allow Reschedule",
            "allow_reschedule",
            ["Yes", "No"]
        )

        self.create_input(
            self.booking_tab,
            "Maximum Reschedule Count",
            "max_reschedule_count"
        )

        self.create_textbox(
            self.booking_tab,
            "Reschedule Policy",
            "reschedule_policy",
            height=5
        )

        self.create_textbox(
            self.booking_tab,
            "Cancellation Policy",
            "cancellation_policy",
            height=5
        )

    def build_event_types_tab(self):
        top_bar = ttk.Frame(self.event_types_tab)
        top_bar.pack(fill="x", pady=(0, 10))

        ttk.Label(
            top_bar,
            text="Manage event type options used in clients and bookings.",
            font=("Segoe UI", 10)
        ).pack(side="left")

        ttk.Button(
            top_bar,
            text="Add Event Type",
            command=self.open_add_event_type_window
        ).pack(side="right")

        columns = ("id", "name")
        self.event_types_table = ttk.Treeview(
            self.event_types_tab,
            columns=columns,
            show="headings",
            height=12
        )

        self.event_types_table.heading("id", text="ID")
        self.event_types_table.heading("name", text="Event Type")

        self.event_types_table.column("id", width=80)
        self.event_types_table.column("name", width=400)

        self.event_types_table.pack(fill="both", expand=True)

        action_bar = ttk.Frame(self.event_types_tab)
        action_bar.pack(fill="x", pady=(10, 0))

        ttk.Button(
            action_bar,
            text="Edit Selected",
            command=self.open_edit_event_type_window
        ).pack(side="left")

        ttk.Button(
            action_bar,
            text="Delete Selected",
            command=self.delete_selected_event_type
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            action_bar,
            text="Refresh",
            command=self.load_event_types
        ).pack(side="right")

    def build_booking_statuses_tab(self):
        top_bar = ttk.Frame(self.booking_statuses_tab)
        top_bar.pack(fill="x", pady=(0, 10))

        ttk.Label(
            top_bar,
            text="Manage booking status options used in bookings and reports.",
            font=("Segoe UI", 10)
        ).pack(side="left")

        ttk.Button(
            top_bar,
            text="Add Booking Status",
            command=self.open_add_booking_status_window
        ).pack(side="right")

        columns = ("id", "name")
        self.booking_statuses_table = ttk.Treeview(
            self.booking_statuses_tab,
            columns=columns,
            show="headings",
            height=12
        )

        self.booking_statuses_table.heading("id", text="ID")
        self.booking_statuses_table.heading("name", text="Booking Status")

        self.booking_statuses_table.column("id", width=80)
        self.booking_statuses_table.column("name", width=400)

        self.booking_statuses_table.pack(fill="both", expand=True)

        action_bar = ttk.Frame(self.booking_statuses_tab)
        action_bar.pack(fill="x", pady=(10, 0))

        ttk.Button(
            action_bar,
            text="Edit Selected",
            command=self.open_edit_booking_status_window
        ).pack(side="left")

        ttk.Button(
            action_bar,
            text="Delete Selected",
            command=self.delete_selected_booking_status
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            action_bar,
            text="Refresh",
            command=self.load_booking_statuses
        ).pack(side="right")

    def load_event_types(self):
        for item in self.event_types_table.get_children():
            self.event_types_table.delete(item)

        event_types = self.app.settings_service.list_event_types()

        for event_type in event_types:
            self.event_types_table.insert(
                "",
                "end",
                values=(
                    event_type["id"],
                    event_type["name"]
                )
            )

    def load_booking_statuses(self):
        for item in self.booking_statuses_table.get_children():
            self.booking_statuses_table.delete(item)

        statuses = self.app.settings_service.list_booking_statuses()

        for status in statuses:
            self.booking_statuses_table.insert(
                "",
                "end",
                values=(
                    status["id"],
                    status["name"]
                )
            )

    def get_selected_event_type(self):
        selected = self.event_types_table.selection()

        if not selected:
            messagebox.showwarning("No Selection", "Please select an event type first.")
            return None

        values = self.event_types_table.item(selected[0], "values")

        return {
            "id": int(values[0]),
            "name": values[1]
        }

    def get_selected_booking_status(self):
        selected = self.booking_statuses_table.selection()

        if not selected:
            messagebox.showwarning("No Selection", "Please select a booking status first.")
            return None

        values = self.booking_statuses_table.item(selected[0], "values")

        return {
            "id": int(values[0]),
            "name": values[1]
        }

    def open_add_event_type_window(self):
        SimpleNameWindow(
            parent=self,
            title="Add Event Type",
            label="Event Type Name",
            save_callback=self.add_event_type
        )

    def open_edit_event_type_window(self):
        event_type = self.get_selected_event_type()

        if not event_type:
            return

        SimpleNameWindow(
            parent=self,
            title="Edit Event Type",
            label="Event Type Name",
            save_callback=lambda name: self.update_event_type(event_type["id"], name),
            initial_value=event_type["name"]
        )

    def open_add_booking_status_window(self):
        SimpleNameWindow(
            parent=self,
            title="Add Booking Status",
            label="Booking Status Name",
            save_callback=self.add_booking_status
        )

    def open_edit_booking_status_window(self):
        status = self.get_selected_booking_status()

        if not status:
            return

        SimpleNameWindow(
            parent=self,
            title="Edit Booking Status",
            label="Booking Status Name",
            save_callback=lambda name: self.update_booking_status(status["id"], name),
            initial_value=status["name"]
        )

    def add_event_type(self, name):
        self.app.settings_service.add_event_type(
            name,
            actor_id=self.app.current_user.id
        )
        self.load_event_types()

    def update_event_type(self, event_type_id, name):
        self.app.settings_service.update_event_type(
            event_type_id,
            name,
            actor_id=self.app.current_user.id
        )
        self.load_event_types()

    def delete_selected_event_type(self):
        event_type = self.get_selected_event_type()

        if not event_type:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete event type '{event_type['name']}'?"
        )

        if not confirm:
            return

        self.app.settings_service.delete_event_type(
            event_type["id"],
            actor_id=self.app.current_user.id
        )

        self.load_event_types()

    def add_booking_status(self, name):
        self.app.settings_service.add_booking_status(
            name,
            actor_id=self.app.current_user.id
        )
        self.load_booking_statuses()

    def update_booking_status(self, status_id, name):
        self.app.settings_service.update_booking_status(
            status_id,
            name,
            actor_id=self.app.current_user.id
        )
        self.load_booking_statuses()

    def delete_selected_booking_status(self):
        status = self.get_selected_booking_status()

        if not status:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete booking status '{status['name']}'?"
        )

        if not confirm:
            return

        self.app.settings_service.delete_booking_status(
            status["id"],
            actor_id=self.app.current_user.id
        )

        self.load_booking_statuses()

    def load_settings(self):
        settings = self.app.settings_service.get_all_settings()

        for key, widget_or_var in self.setting_vars.items():
            value = settings.get(key, "")

            if isinstance(widget_or_var, tk.Text):
                widget_or_var.delete("1.0", "end")
                widget_or_var.insert("1.0", value)
            else:
                widget_or_var.set(value)
        self.load_event_types()
        self.load_booking_statuses()

    def collect_settings(self):
        settings = {}

        for key, widget_or_var in self.setting_vars.items():
            if isinstance(widget_or_var, tk.Text):
                settings[key] = widget_or_var.get("1.0", "end").strip()
            else:
                settings[key] = widget_or_var.get().strip()

        return settings

    def validate_settings(self, settings):
        if not settings["business_name"]:
            raise ValueError("Business name is required.")

        try:
            down_payment = float(settings["down_payment_percentage"])
        except ValueError:
            raise ValueError("Down payment percentage must be a number.")

        if down_payment < 0 or down_payment > 100:
            raise ValueError("Down payment percentage must be between 0 and 100.")

        try:
            due_days = int(settings["full_payment_due_days"])
        except ValueError:
            raise ValueError("Full payment due days must be a whole number.")

        if due_days < 0:
            raise ValueError("Full payment due days cannot be negative.")

        try:
            max_reschedule = int(settings["max_reschedule_count"])
        except ValueError:
            raise ValueError("Maximum reschedule count must be a whole number.")

        if max_reschedule < 0:
            raise ValueError("Maximum reschedule count cannot be negative.")

    def save_settings(self):
        try:
            settings = self.collect_settings()
            self.validate_settings(settings)

            self.app.settings_service.update_settings(
                settings,
                actor_id=self.app.current_user.id
            )

            messagebox.showinfo(
                "Settings Saved",
                "System settings were saved successfully."
            )

        except ValueError as e:
            messagebox.showerror("Invalid Settings", str(e))


if __name__ == "__main__":
    app = PanaloApp()
    app.mainloop()