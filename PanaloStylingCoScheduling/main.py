import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

from auth_service import AuthService
from db import Database
from models import APP_NAME, APP_MODULES, SessionUser
from settings_service import SettingsService
from client_service import ClientService
from package_service import PackageService
from booking_service import BookingService


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
            "event_type",
            "event_date",
            "event_location",
            "status"
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
        self.table.heading("event_type", text="Event Type")
        self.table.heading("event_date", text="Event Date")
        self.table.heading("event_location", text="Location")
        self.table.heading("status", text="Status")

        self.table.column("id", width=50)
        self.table.column("full_name", width=180)
        self.table.column("contact_number", width=120)
        self.table.column("event_type", width=140)
        self.table.column("event_date", width=100)
        self.table.column("event_location", width=220)
        self.table.column("status", width=120)

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
                    client["event_type"] or "",
                    client["event_date"] or "",
                    client["event_location"] or "",
                    client["status"] or ""
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
                    client["event_type"] or "",
                    client["event_date"] or "",
                    client["event_location"] or "",
                    client["status"] or ""
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

class ClientFormWindow(tk.Toplevel):
    def __init__(self, app: PanaloApp, parent_page: ClientsPage, mode: str, client=None):
        super().__init__()

        self.app = app
        self.parent_page = parent_page
        self.mode = mode
        self.client = client

        self.event_type_options = []
        self.status_options = []

        self.title("Add Client" if mode == "add" else "Edit Client")
        self.geometry("520x680")
        self.resizable(False, False)

        self.full_name_var = tk.StringVar(value=client["full_name"] if client else "")
        self.contact_number_var = tk.StringVar(value=client["contact_number"] if client else "")
        self.event_date_var = tk.StringVar(value=client["event_date"] if client else "")
        self.event_location_var = tk.StringVar(value=client["event_location"] if client else "")
        self.guest_count_var = tk.StringVar(value=str(client["guest_count"]) if client and client["guest_count"] is not None else "")
        self.theme_motif_var = tk.StringVar(value=client["theme_motif"] if client else "")
        self.preferred_package_var = tk.StringVar(value=client["preferred_package"] if client else "")

        self.event_type_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.load_dropdown_options()
        self.build_ui()
        self.set_existing_dropdown_values()

    def load_dropdown_options(self):
        self.event_type_options = self.app.settings_service.list_event_types()
        self.status_options = self.app.settings_service.list_booking_statuses()

    def build_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Add Client" if self.mode == "add" else "Edit Client",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(0, 15))

        ttk.Label(frame, text="Client Full Name").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.full_name_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Contact Number").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.contact_number_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Event Type").pack(anchor="w")
        self.event_type_combo = ttk.Combobox(
            frame,
            textvariable=self.event_type_var,
            values=[item["name"] for item in self.event_type_options],
            state="readonly"
        )
        self.event_type_combo.pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Event Date").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.event_date_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Event Location").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.event_location_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Guest Count").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.guest_count_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Theme / Motif").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.theme_motif_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Preferred Package").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.preferred_package_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Status").pack(anchor="w")
        self.status_combo = ttk.Combobox(
            frame,
            textvariable=self.status_var,
            values=[item["name"] for item in self.status_options],
            state="readonly"
        )
        self.status_combo.pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Notes").pack(anchor="w")
        self.notes_box = tk.Text(frame, height=5, wrap="word")
        self.notes_box.pack(fill="x", pady=(3, 15))

        if self.client:
            self.notes_box.insert("1.0", self.client["notes"] or "")

        ttk.Button(
            frame,
            text="Save Client",
            command=self.save_client
        ).pack(fill="x")

    def set_existing_dropdown_values(self):
        if self.client:
            event_type_id = self.client["event_type_id"]
            status_id = self.client["status_id"]

            for item in self.event_type_options:
                if item["id"] == event_type_id:
                    self.event_type_var.set(item["name"])
                    break

            for item in self.status_options:
                if item["id"] == status_id:
                    self.status_var.set(item["name"])
                    break
        else:
            if self.event_type_options:
                self.event_type_var.set(self.event_type_options[0]["name"])

            if self.status_options:
                for item in self.status_options:
                    if item["name"] == "Inquiry":
                        self.status_var.set(item["name"])
                        return

                self.status_var.set(self.status_options[0]["name"])

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
            return int(value)
        except ValueError:
            raise ValueError("Guest count must be a whole number.")

    def save_client(self):
        try:
            guest_count = self.get_guest_count()

            if self.mode == "add":
                self.app.client_service.add_client(
                    full_name=self.full_name_var.get(),
                    contact_number=self.contact_number_var.get(),
                    event_type_id=self.get_selected_event_type_id(),
                    event_date=self.event_date_var.get(),
                    event_location=self.event_location_var.get(),
                    guest_count=guest_count,
                    theme_motif=self.theme_motif_var.get(),
                    preferred_package=self.preferred_package_var.get(),
                    status_id=self.get_selected_status_id(),
                    notes=self.notes_box.get("1.0", "end").strip(),
                    created_by=self.app.current_user.id
                )

                messagebox.showinfo("Success", "Client added successfully.")

            else:
                self.app.client_service.update_client(
                    client_id=self.client["id"],
                    full_name=self.full_name_var.get(),
                    contact_number=self.contact_number_var.get(),
                    event_type_id=self.get_selected_event_type_id(),
                    event_date=self.event_date_var.get(),
                    event_location=self.event_location_var.get(),
                    guest_count=guest_count,
                    theme_motif=self.theme_motif_var.get(),
                    preferred_package=self.preferred_package_var.get(),
                    status_id=self.get_selected_status_id(),
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
        self.geometry("580x760")
        self.resizable(False, False)

        self.client_var = tk.StringVar()
        self.package_var = tk.StringVar()
        self.event_type_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.event_date_var = tk.StringVar(value=booking["event_date"] if booking else "")
        self.event_time_var = tk.StringVar(value=booking["event_time"] if booking else "")
        self.event_location_var = tk.StringVar(value=booking["event_location"] if booking else "")
        self.guest_count_var = tk.StringVar(value=str(booking["guest_count"]) if booking and booking["guest_count"] is not None else "")
        self.theme_motif_var = tk.StringVar(value=booking["theme_motif"] if booking else "")
        self.total_amount_var = tk.StringVar(value=str(booking["total_amount"]) if booking and booking["total_amount"] is not None else "0")
        self.down_payment_var = tk.StringVar(value=str(booking["down_payment_amount"]) if booking and booking["down_payment_amount"] is not None else "0")
        self.balance_var = tk.StringVar(value=str(booking["balance_amount"]) if booking and booking["balance_amount"] is not None else "0")

        self.load_dropdown_options()
        self.build_ui()
        self.set_existing_dropdown_values()
        self.update_balance_preview()

    def load_dropdown_options(self):
        self.client_options = self.app.client_service.list_clients()
        self.package_options = self.app.package_service.list_packages()
        self.event_type_options = self.app.settings_service.list_event_types()
        self.status_options = self.app.settings_service.list_booking_statuses()

    def build_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Add Booking" if self.mode == "add" else "Edit Booking",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(0, 15))

        ttk.Label(frame, text="Client").pack(anchor="w")
        self.client_combo = ttk.Combobox(
            frame,
            textvariable=self.client_var,
            values=[self.format_client_option(item) for item in self.client_options],
            state="readonly"
        )
        self.client_combo.pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Package").pack(anchor="w")
        self.package_combo = ttk.Combobox(
            frame,
            textvariable=self.package_var,
            values=[self.format_package_option(item) for item in self.package_options],
            state="readonly"
        )
        self.package_combo.pack(fill="x", pady=(3, 10))
        self.package_combo.bind("<<ComboboxSelected>>", lambda event: self.auto_fill_package_price())

        ttk.Label(frame, text="Event Type").pack(anchor="w")
        self.event_type_combo = ttk.Combobox(
            frame,
            textvariable=self.event_type_var,
            values=[item["name"] for item in self.event_type_options],
            state="readonly"
        )
        self.event_type_combo.pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Status").pack(anchor="w")
        self.status_combo = ttk.Combobox(
            frame,
            textvariable=self.status_var,
            values=[item["name"] for item in self.status_options],
            state="readonly"
        )
        self.status_combo.pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Event Date").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.event_date_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Event Time").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.event_time_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Event Location").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.event_location_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Guest Count").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.guest_count_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Theme / Motif").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.theme_motif_var).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Total Amount").pack(anchor="w")
        total_entry = ttk.Entry(frame, textvariable=self.total_amount_var)
        total_entry.pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Down Payment Amount").pack(anchor="w")
        down_entry = ttk.Entry(frame, textvariable=self.down_payment_var)
        down_entry.pack(fill="x", pady=(3, 10))

        self.total_amount_var.trace_add("write", lambda *args: self.update_balance_preview())
        self.down_payment_var.trace_add("write", lambda *args: self.update_balance_preview())

        ttk.Label(frame, text="Balance").pack(anchor="w")
        ttk.Entry(
            frame,
            textvariable=self.balance_var,
            state="readonly"
        ).pack(fill="x", pady=(3, 10))

        ttk.Label(frame, text="Booking Notes").pack(anchor="w")
        self.notes_box = tk.Text(frame, height=4, wrap="word")
        self.notes_box.pack(fill="x", pady=(3, 15))

        if self.booking:
            self.notes_box.insert("1.0", self.booking["booking_notes"] or "")

        ttk.Button(
            frame,
            text="Save Booking",
            command=self.save_booking
        ).pack(fill="x")

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
            return int(value)
        except ValueError:
            raise ValueError("Guest count must be a whole number.")

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
            return

        for package in self.package_options:
            if package["id"] == package_id:
                min_price = package["min_price"]

                if min_price is not None:
                    self.total_amount_var.set(str(min_price))

                    try:
                        settings = self.app.settings_service.get_all_settings()
                        down_percentage = float(settings.get("down_payment_percentage", "50"))
                        down_amount = float(min_price) * (down_percentage / 100)
                        self.down_payment_var.set(f"{down_amount:.2f}")
                    except Exception:
                        pass

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