import json
import tkinter as tk
import calendar
import os
import json
from PIL import Image, ImageTk
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
from reports_service import ReportsService

ASSETS_DIR = "assets"
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

LOGIN_BACKGROUND_PATH = os.path.join(IMAGES_DIR, "login_background.png")
APP_ICON_PATH = os.path.join(IMAGES_DIR, "app_icon.png")

SIDEBAR_LOGO_PATH = os.path.join(IMAGES_DIR, "sidebar_logo.png")
SIDEBAR_BACKGROUND_PATH = os.path.join(IMAGES_DIR, "sidebar_background.png")
MAIN_BACKGROUND_PATH = os.path.join(IMAGES_DIR, "main_background.png")

REMEMBER_ME_PATH = os.path.join("data", "remember_me.json")

APP_BG = "#fbf7ef"
SIDEBAR_BG = "#fbf7ef"
SIDEBAR_ACTIVE_BG = "#e9e7d3"
TEXT_DARK = "#2f2b1f"
TEXT_MUTED = "#756f60"
ACCENT_OLIVE = "#68713f"
DANGER_RED = "#9c1f1f"
CARD_BG = "#fbf7ef"
TABLE_BG = "#fbf7ef"
TABLE_HEADER_BG = "#f1eadc"
BORDER_SOFT = "#d8cbb6"

SIDEBAR_SHADOW = "#ddd4c4"
HEADING_FONT = ("Georgia", 22, "bold")
SUBHEADING_FONT = ("Segoe UI", 11)
SECTION_FONT = ("Segoe UI", 11, "bold")
BODY_FONT = ("Segoe UI", 10)
SMALL_FONT = ("Segoe UI", 9)
SIDEBAR_FONT = ("Georgia", 13)

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

        self.set_window_icon()

        self.title("Panalo Styling Co. Admin System")
        self.configure(bg=APP_BG)
        self.configure_app_styles()
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
        self.reports_service = ReportsService(self.db)
        self.current_user: SessionUser | None = None

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.show_login_page()

    def set_window_icon(self):
        try:
            if os.path.exists(APP_ICON_PATH):
                icon_image = tk.PhotoImage(file=APP_ICON_PATH)
                self.iconphoto(True, icon_image)
                self.app_icon_image = icon_image  # keep reference so Tkinter does not remove it
        except Exception:
            pass

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def configure_app_styles(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "TFrame",
            background=APP_BG
        )

        style.configure(
            "TLabel",
            background=APP_BG,
            foreground=TEXT_DARK,
            font=BODY_FONT
        )

        style.configure(
            "Header.TLabel",
            background=APP_BG,
            foreground=TEXT_DARK,
            font=HEADING_FONT
        )

        style.configure(
            "Subheader.TLabel",
            background=APP_BG,
            foreground=TEXT_MUTED,
            font=SUBHEADING_FONT
        )

        style.configure(
            "Section.TLabel",
            background=APP_BG,
            foreground=TEXT_DARK,
            font=SECTION_FONT
        )

        style.configure(
            "TButton",
            font=SMALL_FONT,
            padding=(10, 5),
            background="#f8f3e8",
            foreground=TEXT_DARK,
            bordercolor=BORDER_SOFT,
            focusthickness=0,
            focuscolor="#f8f3e8"
        )

        style.map(
            "TButton",
            background=[
                ("active", "#efe8d8"),
                ("pressed", "#e8e0ce")
            ],
            foreground=[
                ("active", TEXT_DARK),
                ("pressed", TEXT_DARK)
            ]
        )

        style.configure(
            "TLabelframe",
            background=APP_BG,
            foreground=TEXT_DARK,
            bordercolor=BORDER_SOFT,
            lightcolor=BORDER_SOFT,
            darkcolor=BORDER_SOFT,
            relief="solid"
        )

        style.configure(
            "TLabelframe.Label",
            background=APP_BG,
            foreground=ACCENT_OLIVE,
            font=SECTION_FONT
        )

        style.configure(
            "Treeview",
            background=APP_BG,
            fieldbackground=APP_BG,
            foreground=TEXT_DARK,
            rowheight=26,
            borderwidth=1,
            relief="solid",
            font=BODY_FONT
        )

        style.configure(
            "Treeview.Heading",
            background=TABLE_HEADER_BG,
            foreground=TEXT_DARK,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            borderwidth=0
        )

        style.map(
            "Treeview",
            background=[("selected", SIDEBAR_ACTIVE_BG)],
            foreground=[("selected", TEXT_DARK)]
        )


    def show_login_page(self):
        self.clear_container()

        try:
            self.state("normal")
        except tk.TclError:
            self.attributes("-fullscreen", False)

        self.geometry("1100x680")
        self.minsize(1000, 620)
        self.resizable(True, True)

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


class LoginPage(tk.Frame):
    def __init__(self, parent, app: PanaloApp):
        super().__init__(parent)

        self.app = app

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_var = tk.BooleanVar(value=False)
        self.show_password_var = tk.BooleanVar(value=False)

        self.bg_original = None
        self.bg_photo = None

        self.configure(bg="#f7f2e8")

        self.load_remembered_login()
        self.load_background_image()
        self.build_ui()

    def load_background_image(self):
        try:
            if os.path.exists(LOGIN_BACKGROUND_PATH):
                self.bg_original = Image.open(LOGIN_BACKGROUND_PATH)
        except Exception:
            self.bg_original = None

    def build_ui(self):
        self.canvas = tk.Canvas(
            self,
            highlightthickness=0,
            bd=0,
            bg="#f7f2e8"
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", self.redraw_background)

        self.card = tk.Frame(
            self.canvas,
            bg="#fffdf7"
        )

        self.card_window = self.canvas.create_window(
            0,
            0,
            window=self.card,
            anchor="center"
        )

        self.build_login_card()

    def build_login_card(self):
        for widget in self.card.winfo_children():
            widget.destroy()

        inner = tk.Frame(self.card, bg="#fffdf7")
        inner.pack(fill="both", expand=True, padx=46, pady=32)

        tk.Label(
            inner,
            text="❧",
            bg="#fffdf7",
            fg="#7c7f3f",
            font=("Georgia", 22)
        ).pack(pady=(0, 4))

        tk.Label(
            inner,
            text="Welcome Back!",
            bg="#fffdf7",
            fg="#4f5f2f",
            font=("Georgia", 25, "bold")
        ).pack()

        tk.Label(
            inner,
            text="Sign in to your Panalo Styling Co.\nAdmin Account",
            bg="#fffdf7",
            fg="#555555",
            font=("Segoe UI", 11),
            justify="center"
        ).pack(pady=(8, 26))

        tk.Label(
            inner,
            text="Username / Email Address",
            bg="#fffdf7",
            fg="#333333",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        username_box = tk.Frame(
            inner,
            bg="white",
            highlightbackground="#d8cbb6",
            highlightthickness=1
        )
        username_box.pack(fill="x", pady=(6, 18), ipady=3)

        tk.Label(
            username_box,
            text="👤",
            bg="white",
            fg="#7c7f3f",
            font=("Segoe UI", 12)
        ).pack(side="left", padx=(14, 8), pady=8)

        self.username_entry = tk.Entry(
            username_box,
            textvariable=self.username_var,
            bd=0,
            bg="white",
            fg="#333333",
            insertbackground="#333333",
            font=("Segoe UI", 11)
        )
        self.username_entry.pack(side="left", fill="x", expand=True, pady=10, padx=(0, 12))

        tk.Label(
            inner,
            text="Password",
            bg="#fffdf7",
            fg="#333333",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        password_box = tk.Frame(
            inner,
            bg="white",
            highlightbackground="#d8cbb6",
            highlightthickness=1
        )
        password_box.pack(fill="x", pady=(6, 14), ipady=3)

        tk.Label(
            password_box,
            text="🔒",
            bg="white",
            fg="#7c7f3f",
            font=("Segoe UI", 12)
        ).pack(side="left", padx=(14, 8), pady=8)

        self.password_entry = tk.Entry(
            password_box,
            textvariable=self.password_var,
            bd=0,
            bg="white",
            fg="#333333",
            insertbackground="#333333",
            show="*" if not self.show_password_var.get() else "",
            font=("Segoe UI", 11)
        )
        self.password_entry.pack(side="left", fill="x", expand=True, pady=10)

        self.eye_button = tk.Button(
            password_box,
            text="👁",
            command=self.toggle_password_visibility,
            bd=0,
            bg="white",
            fg="#5b5f35",
            activebackground="white",
            cursor="hand2",
            font=("Segoe UI", 10)
        )
        self.eye_button.pack(side="right", padx=(8, 14))

        options_row = tk.Frame(inner, bg="#fffdf7")
        options_row.pack(fill="x", pady=(0, 22))

        tk.Checkbutton(
            options_row,
            text="Remember me",
            variable=self.remember_var,
            bg="#fffdf7",
            fg="#444444",
            activebackground="#fffdf7",
            selectcolor="#fffdf7",
            font=("Segoe UI", 10)
        ).pack(side="left")

        login_button = tk.Button(
            inner,
            text="Login",
            command=self.handle_login,
            bg="#6f742e",
            fg="white",
            activebackground="#5f6427",
            activeforeground="white",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 13, "bold"),
            height=2
        )
        login_button.pack(fill="x", pady=(2, 14))

        tk.Label(
            inner,
            text="Need help? Contact System Administrator",
            bg="#fffdf7",
            fg="#777777",
            font=("Segoe UI", 9)
        ).pack(pady=(8, 0))

        self.username_entry.focus_set()
        self.bind_enter_key()

    def bind_enter_key(self):
        self.username_entry.bind("<Return>", lambda event: self.handle_login())
        self.password_entry.bind("<Return>", lambda event: self.handle_login())

    def resize_image_cover(self, image, target_width, target_height):
        image_width, image_height = image.size

        image_ratio = image_width / image_height
        target_ratio = target_width / target_height

        if image_ratio > target_ratio:
            new_height = target_height
            new_width = int(target_height * image_ratio)
        else:
            new_width = target_width
            new_height = int(target_width / image_ratio)

        resized = image.resize((new_width, new_height), Image.LANCZOS)

        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height

        return resized.crop((left, top, right, bottom))

    def create_round_rectangle(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]

        return canvas.create_polygon(
            points,
            smooth=True,
            **kwargs
        )

    def redraw_background(self, event=None):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        self.canvas.delete("background")
        self.canvas.delete("card_shape")

        if self.bg_original:
            fitted = self.resize_image_cover(
                self.bg_original,
                width,
                height
            )

            self.bg_photo = ImageTk.PhotoImage(fitted)

            self.canvas.create_image(
                0,
                0,
                image=self.bg_photo,
                anchor="nw",
                tags="background"
            )
        else:
            self.canvas.create_rectangle(
                0,
                0,
                width,
                height,
                fill="#f7f2e8",
                outline="",
                tags="background"
            )

        card_width = 500
        card_height = 610

        x_position = int(width * 0.72)
        y_position = int(height * 0.50)

        if width < 1000:
            x_position = width // 2

        x1 = x_position - card_width // 2
        y1 = y_position - card_height // 2
        x2 = x_position + card_width // 2
        y2 = y_position + card_height // 2

        # Soft shadow
        self.create_round_rectangle(
            self.canvas,
            x1 + 8,
            y1 + 10,
            x2 + 8,
            y2 + 10,
            radius=24,
            fill="#000000",
            outline="",
            stipple="gray25",
            tags="card_shape"
        )

        # Rounded card background
        self.create_round_rectangle(
            self.canvas,
            x1,
            y1,
            x2,
            y2,
            radius=24,
            fill="#fffdf7",
            outline="#d8cbb6",
            tags="card_shape"
        )

        self.canvas.itemconfigure(
            self.card_window,
            width=card_width - 34,
            height=card_height - 34
        )

        self.canvas.coords(
            self.card_window,
            x_position,
            y_position
        )

        self.canvas.tag_lower("card_shape", self.card_window)
        self.canvas.tag_lower("background")

    def toggle_password_visibility(self):
        self.show_password_var.set(not self.show_password_var.get())

        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def load_remembered_login(self):
        try:
            if not os.path.exists(REMEMBER_ME_PATH):
                return

            with open(REMEMBER_ME_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

            if data.get("remember"):
                self.username_var.set(data.get("username", ""))
                self.password_var.set(data.get("password", ""))
                self.remember_var.set(True)

        except Exception:
            self.username_var.set("")
            self.password_var.set("")
            self.remember_var.set(False)

    def save_remembered_login(self):
        os.makedirs("data", exist_ok=True)

        if self.remember_var.get():
            data = {
                "remember": True,
                "username": self.username_var.get().strip(),
                "password": self.password_var.get()
            }
        else:
            data = {
                "remember": False,
                "username": "",
                "password": ""
            }

        with open(REMEMBER_ME_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def authenticate_user(self, username, password):
        auth = self.app.auth_service

        if hasattr(auth, "login"):
            return auth.login(username, password)

        if hasattr(auth, "authenticate"):
            return auth.authenticate(username, password)

        if hasattr(auth, "authenticate_user"):
            return auth.authenticate_user(username, password)

        raise ValueError("No login method found in AuthService.")

    def handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username:
            messagebox.showerror("Login Failed", "Please enter your username or email.")
            return

        if not password:
            messagebox.showerror("Login Failed", "Please enter your password.")
            return

        try:
            user = self.authenticate_user(username, password)

            if not user:
                messagebox.showerror("Login Failed", "Invalid username or password.")
                return

        except ValueError as e:
            messagebox.showerror("Login Failed", str(e))
            return

        except Exception as e:
            messagebox.showerror("Login Failed", f"Unable to login: {e}")
            return

        self.save_remembered_login()
        self.app.show_main_system(user)


class DashboardPage(ttk.Frame):
    def __init__(self, parent, app: PanaloApp):
        super().__init__(parent)

        self.app = app

        today = date.today()
        first_day = date(today.year, today.month, 1)
        last_day = date(
            today.year,
            today.month,
            calendar.monthrange(today.year, today.month)[1]
        )

        self.start_date_var = tk.StringVar(value=first_day.strftime("%Y-%m-%d"))
        self.end_date_var = tk.StringVar(value=last_day.strftime("%Y-%m-%d"))

        self.build_ui()
        self.load_dashboard()

    def build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 12))

        left_header = ttk.Frame(header)
        left_header.pack(side="left", fill="x", expand=True)

        ttk.Label(
            left_header,
            text=f"Good day, {self.app.current_user.full_name}!",
            style="Header.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            left_header,
            text="Here’s what’s happening with Panalo Styling Co.",
            style="Subheader.TLabel"
        ).pack(anchor="w", pady=(2, 0))

        ttk.Button(
            header,
            text="Refresh",
            command=self.load_dashboard
        ).pack(side="right")

        filter_bar = ttk.Frame(self)
        filter_bar.pack(fill="x", pady=(0, 12))

        ttk.Label(filter_bar, text="From").pack(side="left")

        ttk.Entry(
            filter_bar,
            textvariable=self.start_date_var,
            width=14,
            state="readonly"
        ).pack(side="left", padx=(6, 4))

        ttk.Button(
            filter_bar,
            text="Select",
            command=lambda: self.open_simple_date_picker(self.start_date_var)
        ).pack(side="left", padx=(0, 10))

        ttk.Label(filter_bar, text="To").pack(side="left")

        ttk.Entry(
            filter_bar,
            textvariable=self.end_date_var,
            width=14,
            state="readonly"
        ).pack(side="left", padx=(6, 4))

        ttk.Button(
            filter_bar,
            text="Select",
            command=lambda: self.open_simple_date_picker(self.end_date_var)
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            filter_bar,
            text="Apply Filter",
            command=self.load_dashboard
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            filter_bar,
            text="This Month",
            command=self.set_this_month
        ).pack(side="right", padx=(6, 0))

        ttk.Button(
            filter_bar,
            text="This Year",
            command=self.set_this_year
        ).pack(side="right", padx=(6, 0))

        self.content = ttk.Frame(self)
        self.content.pack(fill="both", expand=True)

    def open_simple_date_picker(self, target_var):
        SimpleDatePickerWindow(
            target_var=target_var,
            initial_date=target_var.get()
        )

    def set_this_month(self):
        today = date.today()
        first_day = date(today.year, today.month, 1)
        last_day = date(
            today.year,
            today.month,
            calendar.monthrange(today.year, today.month)[1]
        )

        self.start_date_var.set(first_day.strftime("%Y-%m-%d"))
        self.end_date_var.set(last_day.strftime("%Y-%m-%d"))
        self.load_dashboard()

    def set_this_year(self):
        today = date.today()
        first_day = date(today.year, 1, 1)

        self.start_date_var.set(first_day.strftime("%Y-%m-%d"))
        self.end_date_var.set(today.strftime("%Y-%m-%d"))
        self.load_dashboard()

    def clear_dashboard(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def format_price(self, value):
        try:
            return f"₱{float(value or 0):,.2f}"
        except Exception:
            return "₱0.00"

    def format_progress(self, value):
        value = float(value or 0)

        if value > 0:
            return f"▲ {value:.1f}%"
        if value < 0:
            return f"▼ {abs(value):.1f}%"
        return "— 0.0%"

    def get_progress_color(self, value):
        value = float(value or 0)

        if value > 0:
            return "#198754"

        if value < 0:
            return "#dc3545"

        return "#6c757d"

    def create_metric_card(self, parent, title, value, progress_value, subtitle="vs previous period"):
        card = tk.Frame(
            parent,
            bg=APP_BG,
            relief="solid",
            bd=1,
            highlightbackground=BORDER_SOFT,
            highlightthickness=1,
            height=105
        )
        card.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        card.pack_propagate(False)

        tk.Label(
            card,
            text=title,
            bg=APP_BG,
            fg="#555555",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=12, pady=(10, 2))

        tk.Label(
            card,
            text=value,
            bg=APP_BG,
            fg="#111111",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=12)

        progress_frame = tk.Frame(card, bg=APP_BG)
        progress_frame.pack(anchor="w", padx=12, pady=(5, 0))

        tk.Label(
            progress_frame,
            text=self.format_progress(progress_value),
            bg=APP_BG,
            fg=self.get_progress_color(progress_value),
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")

        tk.Label(
            progress_frame,
            text=f" {subtitle}",
            bg=APP_BG,
            fg="#777777",
            font=("Segoe UI", 8)
        ).pack(side="left")

    def create_table(self, parent, columns, headings, widths=None, height=6):
        table_container = tk.Frame(
            parent,
            bg=APP_BG,
            highlightthickness=0,
            bd=0
        )
        table_container.pack(fill="both", expand=False)

        table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=height
        )

        for index, column in enumerate(columns):
            table.heading(column, text=headings[index])
            width = widths[index] if widths else 120
            table.column(column, width=width, anchor="w")

        table.tag_configure(
            "normal",
            background=APP_BG,
            foreground=TEXT_DARK
        )

        table.pack(fill="x", expand=False)

        return table

    def draw_line_graph(self, parent, line_data, title, value_key, label_key):
        canvas = tk.Canvas(
            parent,
            bg=APP_BG,
            height=220,
            highlightthickness=1,
            highlightbackground=BORDER_SOFT
        )
        canvas.pack(fill="both", expand=True)

        def redraw(event=None):
            canvas.delete("all")

            width = canvas.winfo_width()
            height = canvas.winfo_height()

            padding_left = 45
            padding_right = 20
            padding_top = 30
            padding_bottom = 42

            chart_width = width - padding_left - padding_right
            chart_height = height - padding_top - padding_bottom

            canvas.create_text(
                12,
                12,
                text=title,
                anchor="w",
                font=("Segoe UI", 11, "bold")
            )

            if not line_data:
                canvas.create_text(
                    width / 2,
                    height / 2,
                    text="No data for selected range",
                    fill="#777777",
                    font=("Segoe UI", 11)
                )
                return

            values = [float(item[value_key] or 0) for item in line_data]
            labels = [item[label_key] for item in line_data]

            max_value = max(values)

            if max_value <= 0:
                max_value = 1

            x0 = padding_left
            y0 = height - padding_bottom
            x1 = width - padding_right
            y1 = padding_top

            canvas.create_line(x0, y0, x1, y0, fill="#999999")
            canvas.create_line(x0, y0, x0, y1, fill="#999999")

            for i in range(5):
                y = y0 - (chart_height * i / 4)
                canvas.create_line(x0, y, x1, y, fill="#eeeeee")

                value_label = max_value * i / 4

                if max_value >= 1000:
                    display = f"{value_label / 1000:.0f}k"
                else:
                    display = str(int(value_label))

                canvas.create_text(
                    x0 - 8,
                    y,
                    text=display,
                    anchor="e",
                    fill="#666666",
                    font=("Segoe UI", 8)
                )

            points = []

            if len(values) == 1:
                x = x0 + chart_width / 2
                y = y0 - (values[0] / max_value) * chart_height
                points.append((x, y))
            else:
                for index, value in enumerate(values):
                    x = x0 + (chart_width * index / (len(values) - 1))
                    y = y0 - (value / max_value) * chart_height
                    points.append((x, y))

            for index in range(len(points) - 1):
                canvas.create_line(
                    points[index][0],
                    points[index][1],
                    points[index + 1][0],
                    points[index + 1][1],
                    fill="#1a73e8",
                    width=3
                )

            for index, (x, y) in enumerate(points):
                canvas.create_oval(
                    x - 4,
                    y - 4,
                    x + 4,
                    y + 4,
                    fill="#1a73e8",
                    outline="#1a73e8"
                )

                if len(points) <= 8 or index in [0, len(points) - 1]:
                    label_text = labels[index][5:] if len(labels[index]) >= 10 else labels[index]

                    canvas.create_text(
                        x,
                        y0 + 16,
                        text=label_text,
                        anchor="n",
                        fill="#666666",
                        font=("Segoe UI", 8)
                    )

        canvas.bind("<Configure>", redraw)
        canvas.after(100, redraw)

    def draw_pie_chart(self, parent, pie_data):
        canvas = tk.Canvas(
            parent,
            bg="white",
            height=220,
            highlightthickness=1,
            highlightbackground="#dddddd"
        )
        canvas.pack(fill="both", expand=True)

        colors = [
            "#1a73e8",
            "#34a853",
            "#fbbc04",
            "#ea4335",
            "#9334e6",
            "#00acc1",
            "#ff7043",
            "#6c757d"
        ]

        def redraw(event=None):
            canvas.delete("all")

            width = canvas.winfo_width()
            height = canvas.winfo_height()

            canvas.create_text(
                12,
                12,
                text="Bookings by Event Type",
                anchor="w",
                font=("Segoe UI", 11, "bold")
            )

            if not pie_data:
                canvas.create_text(
                    width / 2,
                    height / 2,
                    text="No event type data",
                    fill="#777777",
                    font=("Segoe UI", 11)
                )
                return

            total = sum(int(item["value"]) for item in pie_data)

            if total <= 0:
                canvas.create_text(
                    width / 2,
                    height / 2,
                    text="No event type data",
                    fill="#777777",
                    font=("Segoe UI", 11)
                )
                return

            size = min(height - 65, width * 0.38)
            x0 = 25
            y0 = 45
            x1 = x0 + size
            y1 = y0 + size

            start_angle = 0

            for index, item in enumerate(pie_data):
                value = int(item["value"])
                extent = (value / total) * 360
                color = colors[index % len(colors)]

                canvas.create_arc(
                    x0,
                    y0,
                    x1,
                    y1,
                    start=start_angle,
                    extent=extent,
                    fill=color,
                    outline="white"
                )

                start_angle += extent

            legend_x = x1 + 25
            legend_y = 50

            for index, item in enumerate(pie_data[:8]):
                color = colors[index % len(colors)]

                canvas.create_rectangle(
                    legend_x,
                    legend_y + index * 23,
                    legend_x + 12,
                    legend_y + 12 + index * 23,
                    fill=color,
                    outline=color
                )

                percent = (int(item["value"]) / total) * 100

                canvas.create_text(
                    legend_x + 18,
                    legend_y + 6 + index * 23,
                    text=f"{item['label']} ({percent:.1f}%)",
                    anchor="w",
                    fill="#333333",
                    font=("Segoe UI", 9)
                )

        canvas.bind("<Configure>", redraw)
        canvas.after(100, redraw)

    def validate_filter_dates(self):
        start_date = self.start_date_var.get().strip()
        end_date = self.end_date_var.get().strip()

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except Exception:
            raise ValueError("Date filter must use YYYY-MM-DD format.")

        if start > end:
            raise ValueError("Start date cannot be later than end date.")

        return start_date, end_date

    def load_dashboard(self):
        self.clear_dashboard()

        try:
            start_date, end_date = self.validate_filter_dates()

            data = self.app.reports_service.get_dashboard_data(
                start_date,
                end_date
            )

        except Exception as e:
            messagebox.showerror("Dashboard Error", str(e))
            return

        metrics = data["metrics"]
        progress = data["progress"]

        kpi_row = ttk.Frame(self.content)
        kpi_row.pack(fill="x", pady=(0, 8))

        self.create_metric_card(
            kpi_row,
            "Total Bookings",
            str(metrics["total_bookings"]),
            progress["total_bookings"]
        )

        self.create_metric_card(
            kpi_row,
            "Verified Payments",
            self.format_price(metrics["verified_payments"]),
            progress["verified_payments"]
        )

        self.create_metric_card(
            kpi_row,
            "Upcoming Events",
            str(metrics["upcoming_events"]),
            progress["upcoming_events"]
        )

        self.create_metric_card(
            kpi_row,
            "New Clients",
            str(metrics["new_clients"]),
            progress["new_clients"]
        )

        graph_row = ttk.Frame(self.content)
        graph_row.pack(fill="both", expand=True, pady=(6, 8))

        booking_graph = ttk.LabelFrame(graph_row, text="Booking Trend", padding=10)
        booking_graph.pack(side="left", fill="both", expand=True, padx=(0, 5))

        payment_graph = ttk.LabelFrame(graph_row, text="Payment Trend", padding=10)
        payment_graph.pack(side="left", fill="both", expand=True, padx=(5, 5))

        pie_box = ttk.LabelFrame(graph_row, text="Distribution", padding=10)
        pie_box.pack(side="left", fill="both", expand=True, padx=(5, 0))

        self.draw_line_graph(
            booking_graph,
            data["line_data"],
            "Bookings Over Time",
            "booking_count",
            "event_date"
        )

        self.draw_line_graph(
            payment_graph,
            data["payment_trend"],
            "Verified Payments Over Time",
            "total_amount",
            "payment_date"
        )

        self.draw_pie_chart(
            pie_box,
            data["pie_data"]
        )

        operational_row = ttk.Frame(self.content)
        operational_row.pack(fill="both", expand=True, pady=(6, 8))

        today_box = ttk.LabelFrame(operational_row, text="Today's Schedule", padding=10)
        today_box.pack(side="left", fill="both", expand=True, padx=(0, 5))

        recent_box = ttk.LabelFrame(operational_row, text="Recent Bookings", padding=10)
        recent_box.pack(side="left", fill="both", expand=True, padx=(5, 5))

        queue_box = ttk.LabelFrame(operational_row, text="Payment Verification Queue", padding=10)
        queue_box.pack(side="left", fill="both", expand=True, padx=(5, 0))

        today_table = self.create_table(
            today_box,
            columns=("time", "client", "event_type", "status"),
            headings=("Time", "Client", "Event", "Status"),
            widths=(75, 140, 120, 90),
            height=6
        )

        for item in data["today_schedule"]:
            today_table.insert(
                "",
                "end",
                values=(
                    item["event_time"] or "",
                    item["client_name"] or "",
                    item["event_type"] or "",
                    item["status"] or ""
                )

            )

        recent_table = self.create_table(
            recent_box,
            columns=("date", "client", "package", "status"),
            headings=("Date", "Client", "Package", "Status"),
            widths=(90, 130, 180, 90),
            height=6
        )

        for item in data["recent_bookings"]:
            recent_table.insert(
                "",
                "end",
                values=(
                    item["event_date"] or "",
                    item["client_name"] or "",
                    item["package_name"] or "",
                    item["status"] or ""
                )
            )

        queue_table = self.create_table(
            queue_box,
            columns=("client", "type", "amount", "method"),
            headings=("Client", "Type", "Amount", "Method"),
            widths=(130, 110, 100, 90),
            height=6
        )

        for item in data["payment_queue"]:
            queue_table.insert(
                "",
                "end",
                values=(
                    item["client_name"] or "",
                    item["payment_type"] or "",
                    self.format_price(item["amount"]),
                    item["payment_method"] or ""
                )
            )

        bottom_row = ttk.Frame(self.content)
        bottom_row.pack(fill="x", expand=False, pady=(6, 0))

        package_box = ttk.LabelFrame(bottom_row, text="Packages at a Glance", padding=10)
        package_box.pack(side="left", fill="both", expand=True, padx=(0, 5))

        upcoming_box = ttk.LabelFrame(bottom_row, text="Upcoming Events", padding=10)
        upcoming_box.pack(side="left", fill="both", expand=True, padx=(5, 0))

        package_table = self.create_table(
            package_box,
            columns=("package", "bookings", "revenue"),
            headings=("Package", "Bookings", "Revenue"),
            widths=(260, 80, 120),
            height=4
        )

        for item in data["package_performance"]:
            package_table.insert(
                "",
                "end",
                values=(
                    item["package_name"] or "",
                    item["booking_count"],
                    self.format_price(item["revenue"])
                )
            )

        upcoming_table = self.create_table(
            upcoming_box,
            columns=("date", "time", "client", "status"),
            headings=("Date", "Time", "Client", "Status"),
            widths=(90, 80, 180, 100),
            height=4
        )

        for item in data["upcoming_events"]:
            upcoming_table.insert(
                "",
                "end",
                values=(
                    item["event_date"] or "",
                    item["event_time"] or "",
                    item["client_name"] or "",
                    item["status"] or ""
                ),
                tags=("normal",)
            )

class MainSystemPage(tk.Frame):
    SIDEBAR_WIDTH = 255
    SIDEBAR_COLLAPSED_WIDTH = 72

    def __init__(self, parent, app: PanaloApp, user: SessionUser):
        super().__init__(parent)

        self.app = app
        self.user = user
        self.active_module = "Dashboard"
        self.sidebar_collapsed = False

        self.sidebar_bg_original = None
        self.sidebar_bg_photo = None

        self.main_bg_original = None
        self.main_bg_photo = None

        self.logo_original = None
        self.logo_photo = None

        self.nav_widgets = []

        self.load_images()
        self.build_ui()

    def create_top_collapse_button(self, y):
        sidebar_width = self.SIDEBAR_COLLAPSED_WIDTH if self.sidebar_collapsed else self.SIDEBAR_WIDTH

        button_frame = tk.Frame(
            self.sidebar_canvas,
            bg=SIDEBAR_BG,
            bd=0,
            highlightthickness=0
        )

        collapse_button = tk.Button(
            button_frame,
            text="\uE76B" if not self.sidebar_collapsed else "\uE76C",
            command=self.toggle_sidebar,
            bg="#efecd8",
            fg=ACCENT_OLIVE,
            activebackground="#e4e1ca",
            activeforeground=ACCENT_OLIVE,
            bd=0,
            cursor="hand2",
            font=("Segoe MDL2 Assets", 11),
            width=4
        )
        collapse_button.pack(side="right", padx=(0, 10), pady=6)

        self.sidebar_canvas.create_window(
            sidebar_width - 8,
            y,
            window=button_frame,
            anchor="ne",
            width=60,
            height=42,
            tags="nav"
        )

    def load_images(self):
        self.sidebar_bg_original = None
        self.main_bg_original = None

        try:
            if os.path.exists(SIDEBAR_LOGO_PATH):
                self.logo_original = Image.open(SIDEBAR_LOGO_PATH)
        except Exception:
            self.logo_original = None

    def resize_image_cover(self, image, target_width, target_height):
        image_width, image_height = image.size

        image_ratio = image_width / image_height
        target_ratio = target_width / target_height

        if image_ratio > target_ratio:
            new_height = target_height
            new_width = int(target_height * image_ratio)
        else:
            new_width = target_width
            new_height = int(target_width / image_ratio)

        resized = image.resize((new_width, new_height), Image.LANCZOS)

        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height

        return resized.crop((left, top, right, bottom))

    def resize_image_contain(self, image, max_width, max_height):
        image_width, image_height = image.size

        ratio = min(max_width / image_width, max_height / image_height)

        new_width = int(image_width * ratio)
        new_height = int(image_height * ratio)

        return image.resize((new_width, new_height), Image.LANCZOS)

    def build_ui(self):
        self.configure(bg=APP_BG)

        shell = tk.Frame(self, bg=APP_BG)
        shell.pack(fill="both", expand=True)

        self.sidebar_wrap = tk.Frame(shell, bg=SIDEBAR_SHADOW, width=self.SIDEBAR_WIDTH + 4)
        self.sidebar_wrap.pack(side="left", fill="y")
        self.sidebar_wrap.pack_propagate(False)

        self.sidebar_canvas = tk.Canvas(
            self.sidebar_wrap,
            width=self.SIDEBAR_WIDTH,
            highlightthickness=0,
            bd=0,
            bg=SIDEBAR_BG
        )
        self.sidebar_canvas.pack(side="left", fill="y")
        self.sidebar_canvas.pack_propagate(False)

        self.shadow_line = tk.Frame(self.sidebar_wrap, bg=SIDEBAR_SHADOW, width=4)
        self.shadow_line.pack(side="right", fill="y")

        self.main_canvas = tk.Canvas(
            shell,
            highlightthickness=0,
            bd=0,
            bg=APP_BG
        )
        self.main_canvas.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(
            self.main_canvas,
            bg=APP_BG
        )

        self.content_window = self.main_canvas.create_window(
            24,
            24,
            window=self.content,
            anchor="nw"
        )

        self.sidebar_canvas.bind("<Configure>", self.redraw_sidebar_background)
        self.main_canvas.bind("<Configure>", self.redraw_main_background)

        self.build_sidebar()
        self.show_module("Dashboard")

    def get_nav_items(self):
        return [
            {
                "module": "Dashboard",
                "label": "Dashboard",
                "icon": "\uE80F",
                "subtitle": ""
            },
            {
                "module": "Clients",
                "label": "Clients",
                "icon": "\uE716",
                "subtitle": ""
            },
            {
                "module": "Bookings",
                "label": "Bookings",
                "icon": "\uE8FD",
                "subtitle": ""
            },
            {
                "module": "Packages",
                "label": "Packages",
                "icon": "\uE8B7",
                "subtitle": ""
            },
            {
                "module": "Schedule",
                "label": "Schedules",
                "icon": "\uE787",
                "subtitle": ""
            },
            {
                "module": "Payment",
                "label": "Payments",
                "icon": "\uE8C7",
                "subtitle": "verification / refunds"
            },
            {
                "module": "Reports",
                "label": "Reports",
                "icon": "\uE9D2",
                "subtitle": ""
            },
            {
                "module": "User Management",
                "label": "Accounts",
                "icon": "\uE77B",
                "subtitle": "add, edit, delete"
            },
            {
                "module": "Settings",
                "label": "Settings",
                "icon": "\uE713",
                "subtitle": ""
            },
        ]

    def can_access_module(self, module_name):
        role = (self.user.role or "").lower()

        if role == "admin":
            return True

        # Flexible support in case your SessionUser stores privileges differently.
        possible_attrs = [
            "allowed_modules",
            "accessible_modules",
            "modules",
            "privileges",
            "permissions"
        ]

        for attr in possible_attrs:
            if hasattr(self.user, attr):
                value = getattr(self.user, attr)

                if isinstance(value, str):
                    return module_name in value

                if isinstance(value, (list, tuple, set)):
                    return module_name in value

        # Fallback for staff accounts.
        restricted = ["User Management", "Settings"]
        return module_name not in restricted

    def build_sidebar(self):
        self.sidebar_canvas.delete("nav")
        self.nav_widgets.clear()

        sidebar_width = self.SIDEBAR_COLLAPSED_WIDTH if self.sidebar_collapsed else self.SIDEBAR_WIDTH

        self.sidebar_canvas.config(width=sidebar_width)

        if hasattr(self, "sidebar_wrap"):
            self.sidebar_wrap.config(width=sidebar_width + 4)

        y = 18

        self.create_top_collapse_button(y)
        y += 48

        if not self.sidebar_collapsed:
            self.draw_logo(y)
            y += 220
        else:
            y += 8

        for item in self.get_nav_items():
            if not self.can_access_module(item["module"]):
                continue

            self.create_nav_item(
                module_name=item["module"],
                label=item["label"],
                icon=item["icon"],
                subtitle=item["subtitle"],
                y=y
            )

            if item["subtitle"] and not self.sidebar_collapsed:
                y += 56
            else:
                y += 47

        self.create_sidebar_footer()

    def draw_logo(self, y):
        if self.logo_original:
            logo = self.resize_image_contain(self.logo_original, 150, 135)
            self.logo_photo = ImageTk.PhotoImage(logo)

            self.sidebar_canvas.create_image(
                self.SIDEBAR_WIDTH // 2,
                y + 72,
                image=self.logo_photo,
                anchor="center",
                tags="nav"
            )
        else:
            self.sidebar_canvas.create_text(
                self.SIDEBAR_WIDTH // 2,
                y + 58,
                text="P",
                fill=ACCENT_OLIVE,
                font=("Georgia", 54, "bold"),
                justify="center",
                tags="nav"
            )

        self.sidebar_canvas.create_text(
            self.SIDEBAR_WIDTH // 2,
            y + 155,
            text="Panalo Styling Co.",
            fill=ACCENT_OLIVE,
            font=("Georgia", 18, "bold"),
            justify="center",
            tags="nav"
        )

        self.sidebar_canvas.create_text(
            self.SIDEBAR_WIDTH // 2,
            y + 180,
            text="Admin System",
            fill=TEXT_MUTED,
            font=("Segoe UI", 9),
            justify="center",
            tags="nav"
        )

    def create_nav_item(self, module_name, label, icon, subtitle, y):
        sidebar_width = self.SIDEBAR_COLLAPSED_WIDTH if self.sidebar_collapsed else self.SIDEBAR_WIDTH

        is_active = self.active_module == module_name

        item_height = 44 if not subtitle or self.sidebar_collapsed else 56

        x1 = 12
        x2 = sidebar_width - 12

        bg_color = SIDEBAR_ACTIVE_BG if is_active else SIDEBAR_BG
        text_color = TEXT_DARK
        icon_color = ACCENT_OLIVE

        button_frame = tk.Frame(
            self.sidebar_canvas,
            bg=bg_color,
            cursor="hand2",
            highlightthickness=0,
            bd=0
        )

        button_frame.bind(
            "<Button-1>",
            lambda event, name=module_name: self.show_module(name)
        )

        icon_label = tk.Label(
            button_frame,
            text=icon,
            bg=bg_color,
            fg=icon_color,
            font=("Segoe MDL2 Assets", 16),
            width=3,
            cursor="hand2",
            bd = 0,
            highlightthickness = 0
        )
        icon_label.pack(side="left", padx=(13, 8), pady=8)
        icon_label.bind(
            "<Button-1>",
            lambda event, name=module_name: self.show_module(name)
        )

        if not self.sidebar_collapsed:
            text_frame = tk.Frame(button_frame, bg=bg_color, cursor="hand2")
            text_frame.pack(side="left", fill="both", expand=True, pady=6)

            label_widget = tk.Label(
                text_frame,
                text=label,
                bg=bg_color,
                fg=text_color,
                font=("Georgia", 13),
                anchor="w",
                cursor="hand2",
                bd = 0,
                highlightthickness = 0
            )
            label_widget.pack(anchor="w")

            label_widget.bind(
                "<Button-1>",
                lambda event, name=module_name: self.show_module(name)
            )

            if subtitle:
                subtitle_widget = tk.Label(
                    text_frame,
                    text=subtitle,
                    bg=bg_color,
                    fg=TEXT_MUTED,
                    font=("Segoe UI", 8),
                    anchor="w",
                    cursor="hand2"
                )
                subtitle_widget.pack(anchor="w", pady=(1, 0))

                subtitle_widget.bind(
                    "<Button-1>",
                    lambda event, name=module_name: self.show_module(name)
                )

        self.sidebar_canvas.create_window(
            x1,
            y,
            window=button_frame,
            anchor="nw",
            width=x2 - x1,
            height=item_height,
            tags="nav"
        )

        self.nav_widgets.append(button_frame)

    def create_sidebar_footer(self):
        sidebar_width = self.SIDEBAR_COLLAPSED_WIDTH if self.sidebar_collapsed else self.SIDEBAR_WIDTH
        canvas_height = self.sidebar_canvas.winfo_height()

        if canvas_height <= 1:
            return

        footer_height = 58
        footer_y = canvas_height - footer_height

        footer_frame = tk.Frame(
            self.sidebar_canvas,
            bg=SIDEBAR_BG
        )

        logout_button = tk.Button(
            footer_frame,
            text="Logout" if not self.sidebar_collapsed else "\uE8AC",
            command=self.app.show_login_page,
            bg=SIDEBAR_BG,
            fg=DANGER_RED,
            activebackground="#f3e4de",
            activeforeground=DANGER_RED,
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold")
        )
        logout_button.pack(fill="both", expand=True, padx=12, pady=8)

        self.sidebar_canvas.create_window(
            0,
            footer_y,
            window=footer_frame,
            anchor="nw",
            width=sidebar_width,
            height=footer_height,
            tags="nav footer"
        )

    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed

        self.build_sidebar()
        self.redraw_sidebar_background()

        self.update_idletasks()
        self.redraw_main_background()

    def redraw_sidebar_background(self, event=None):
        width = self.sidebar_canvas.winfo_width()
        height = self.sidebar_canvas.winfo_height()

        self.sidebar_canvas.delete("sidebar_bg")

        self.sidebar_canvas.create_rectangle(
            0,
            0,
            width,
            height,
            fill=SIDEBAR_BG,
            outline="",
            width=0,
            tags="sidebar_bg"
        )

        self.sidebar_canvas.tag_lower("sidebar_bg")

        self.sidebar_canvas.delete("footer")
        self.create_sidebar_footer()

    def redraw_main_background(self, event=None):
        width = self.main_canvas.winfo_width()
        height = self.main_canvas.winfo_height()

        self.main_canvas.delete("main_bg")

        self.main_canvas.create_rectangle(
            0,
            0,
            width,
            height,
            fill=APP_BG,
            outline="",
            width=0,
            tags="main_bg"
        )

        self.main_canvas.tag_lower("main_bg")

        content_margin = 24

        self.main_canvas.coords(
            self.content_window,
            content_margin,
            content_margin
        )

        self.main_canvas.itemconfigure(
            self.content_window,
            width=max(width - content_margin * 2, 400),
            height=max(height - content_margin * 2, 300)
        )

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_module(self, module_name):
        self.active_module = module_name
        self.clear_content()
        self.build_sidebar()

        if module_name == "Dashboard":
            DashboardPage(self.content, self.app).pack(fill="both", expand=True)
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

        if module_name == "Reports":
            ReportsPage(self.content, self.app).pack(fill="both", expand=True)
            return

        if module_name == "User Management":
            UserManagementPage(self.content, self.app).pack(fill="both", expand=True)
            return

        if module_name == "Settings":
            SettingsPage(self.content, self.app).pack(fill="both", expand=True)
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
        self.users_cache = []
        self.build_ui()
        self.load_users()

    def build_ui(self):
        # ── Header ──────────────────────────────────────────
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(header, text="User Management", style="Header.TLabel").pack(side="left")
        ttk.Button(header, text="＋ Add User", command=self.open_add_user_window).pack(side="right")
        ttk.Button(header, text="↺ Refresh", command=self.load_users).pack(side="right", padx=(0, 6))

        # ── Staff table ──────────────────────────────────────
        cols = ("id", "full_name", "username", "role", "status", "bypass_pin")
        self.table = ttk.Treeview(self, columns=cols, show="headings", height=13)
        headings = ("ID", "Full Name", "Username", "Role", "Status", "Bypass PIN")
        widths   = (50,   220,         160,        90,     80,       90)
        for col, hd, wd in zip(cols, headings, widths):
            self.table.heading(col, text=hd)
            self.table.column(col, width=wd, anchor="w")

        self.table.tag_configure("inactive", foreground="#999999")
        self.table.tag_configure("has_pin",  foreground="#5a7a2e")

        sb = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=sb.set)
        self.table.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

        # ── Action bar ───────────────────────────────────────
        action_col = tk.Frame(self, bg=APP_BG)
        action_col.pack(side="left", fill="y", padx=(14, 0))

        def act_btn(text, cmd, fg=TEXT_DARK):
            b = tk.Button(
                action_col, text=text, command=cmd,
                bg="#f1eadc", fg=fg, activebackground="#e4ddd0",
                bd=0, cursor="hand2", relief="flat",
                font=("Segoe UI", 9), width=22, pady=7
            )
            b.pack(fill="x", pady=3)
            return b

        tk.Label(action_col, text="Account", bg=APP_BG,
                 fg=TEXT_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(6, 2))
        act_btn("✏  Edit User Info",     self.open_edit_user_window)
        act_btn("👁  View Staff Details", self.open_staff_view_window)

        tk.Label(action_col, text="Access", bg=APP_BG,
                 fg=TEXT_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(12, 2))
        act_btn("🔑  Module Assignment",  self.open_privileges_window)
        act_btn("🔓  Bypass PIN Setup",   self.open_bypass_pin_window)

        tk.Label(action_col, text="Security", bg=APP_BG,
                 fg=TEXT_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(12, 2))
        act_btn("🔒  Reset Password",     self.open_password_recovery_window, fg=DANGER_RED)

    # ── Data ────────────────────────────────────────────────

    def load_users(self):
        for item in self.table.get_children():
            self.table.delete(item)
        self.users_cache = self.app.auth_service.list_users()
        for u in self.users_cache:
            status  = "Active"   if u.get("is_active", 1) else "Inactive"
            has_pin = "✔ Set"    if u.get("has_bypass_pin") else "— None"
            tag = "inactive" if not u.get("is_active", 1) else ("has_pin" if u.get("has_bypass_pin") else "normal")
            self.table.insert("", "end", tags=(tag,),
                values=(u["id"], u["full_name"], u["username"], u["role"], status, has_pin))

    def get_selected_user(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a user first.")
            return None
        uid = int(self.table.item(sel[0], "values")[0])
        for u in self.users_cache:
            if u["id"] == uid:
                return u
        return None

    # ── Openers ─────────────────────────────────────────────

    def open_add_user_window(self):
        UserFormWindow(self.app, self, mode="add")

    def open_edit_user_window(self):
        u = self.get_selected_user()
        if u:
            UserFormWindow(self.app, self, mode="edit", user=u)

    def open_staff_view_window(self):
        u = self.get_selected_user()
        if u:
            StaffViewWindow(self.app, u)

    def open_privileges_window(self):
        u = self.get_selected_user()
        if u:
            PrivilegesWindow(self.app, self, u)

    def open_bypass_pin_window(self):
        u = self.get_selected_user()
        if u:
            BypassPinWindow(self.app, self, u)

    def open_password_recovery_window(self):
        u = self.get_selected_user()
        if u:
            PasswordRecoveryWindow(self.app, self, u)


class UserFormWindow(tk.Toplevel):
    def __init__(self, app: PanaloApp, parent_page: UserManagementPage, mode: str, user=None):
        super().__init__()
        self.app = app
        self.parent_page = parent_page
        self.mode = mode
        self.user = user

        self.title("Add New User" if mode == "add" else "Edit User")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(bg=APP_BG)
        self.grab_set()

        self.full_name_var   = tk.StringVar(value=user["full_name"]    if user else "")
        self.username_var    = tk.StringVar(value=user["username"]     if user else "")
        self.email_var       = tk.StringVar(value=user.get("email","") if user else "")
        self.phone_var       = tk.StringVar(value=user.get("phone_number","") if user else "")
        self.role_var        = tk.StringVar(value=user["role"]         if user else "STAFF")
        self.is_active_var   = tk.IntVar(value=int(user.get("is_active",1)) if user else 1)
        self.password_var    = tk.StringVar()
        self.password_visible = False

        self.build_ui()

    def _field(self, parent, label, var, placeholder=""):
        tk.Label(parent, text=label, bg=APP_BG, fg=TEXT_DARK,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8,1))
        box = tk.Frame(parent, bg="white", highlightbackground=BORDER_SOFT, highlightthickness=1)
        box.pack(fill="x")
        e = tk.Entry(box, textvariable=var, bd=0, bg="white", fg=TEXT_DARK,
                     insertbackground=TEXT_DARK, font=("Segoe UI", 10))
        e.pack(fill="x", padx=8, pady=6)
        return e

    def build_ui(self):
        wrap = tk.Frame(self, bg=APP_BG, padx=24, pady=20)
        wrap.pack(fill="both", expand=True)

        tk.Label(wrap, text="Add New User" if self.mode=="add" else "Edit User",
                 bg=APP_BG, fg=TEXT_DARK, font=("Georgia", 16, "bold")).pack(anchor="w", pady=(0,12))

        self._field(wrap, "Full Name *", self.full_name_var)
        self._field(wrap, "Username *", self.username_var)
        self._field(wrap, "Email", self.email_var)
        self._field(wrap, "Phone Number", self.phone_var)

        tk.Label(wrap, text="Role *", bg=APP_BG, fg=TEXT_DARK,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8,1))
        ttk.Combobox(wrap, textvariable=self.role_var,
                     values=["ADMIN","STAFF"], state="readonly").pack(fill="x")

        pw_lbl = "Password *" if self.mode=="add" else "New Password  (leave blank to keep)"
        tk.Label(wrap, text=pw_lbl, bg=APP_BG, fg=TEXT_DARK,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8,1))
        pw_box = tk.Frame(wrap, bg="white", highlightbackground=BORDER_SOFT, highlightthickness=1)
        pw_box.pack(fill="x")
        self.pw_entry = tk.Entry(pw_box, textvariable=self.password_var, show="*",
                                  bd=0, bg="white", fg=TEXT_DARK,
                                  insertbackground=TEXT_DARK, font=("Segoe UI",10))
        self.pw_entry.pack(side="left", fill="x", expand=True, padx=8, pady=6)
        tk.Button(pw_box, text="👁", bd=0, bg="white", activebackground="white",
                  command=self._toggle_pw, cursor="hand2").pack(side="right", padx=6)

        if self.mode == "edit":
            tk.Checkbutton(wrap, text="Account is Active", variable=self.is_active_var,
                           bg=APP_BG, fg=TEXT_DARK, activebackground=APP_BG,
                           selectcolor=APP_BG, font=("Segoe UI",10)).pack(anchor="w", pady=(10,0))

        tk.Button(wrap, text="Save", command=self.save_user,
                  bg=ACCENT_OLIVE, fg="white", activebackground="#5a6435",
                  bd=0, cursor="hand2", font=("Segoe UI",11,"bold"),
                  height=2).pack(fill="x", pady=(16,0))

    def _toggle_pw(self):
        self.password_visible = not self.password_visible
        self.pw_entry.config(show="" if self.password_visible else "*")

    def save_user(self):
        try:
            actor_id = self.app.current_user.id
            if self.mode == "add":
                self.app.auth_service.create_user_by_admin(
                    actor_id=actor_id,
                    full_name=self.full_name_var.get(),
                    username=self.username_var.get(),
                    password=self.password_var.get(),
                    role=self.role_var.get(),
                    email=self.email_var.get(),
                    phone_number=self.phone_var.get(),
                )
                messagebox.showinfo("Success", "User account created successfully.")
            else:
                self.app.auth_service.update_user_by_admin(
                    actor_id=actor_id,
                    user_id=self.user["id"],
                    full_name=self.full_name_var.get(),
                    username=self.username_var.get(),
                    role=self.role_var.get(),
                    email=self.email_var.get(),
                    phone_number=self.phone_var.get(),
                    is_active=self.is_active_var.get(),
                    new_password=self.password_var.get().strip() or None,
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
        self.title(f"Module Assignment — {user['full_name']}")
        self.geometry("420x540")
        self.resizable(False, False)
        self.configure(bg=APP_BG)
        self.grab_set()
        self.permission_vars = {}
        self.build_ui()

    def build_ui(self):
        wrap = tk.Frame(self, bg=APP_BG, padx=24, pady=20)
        wrap.pack(fill="both", expand=True)

        tk.Label(wrap, text="Module Assignment", bg=APP_BG, fg=TEXT_DARK,
                 font=("Georgia", 16, "bold")).pack(anchor="w")
        tk.Label(wrap, text=f"User: {self.user['full_name']}  ({self.user['role']})",
                 bg=APP_BG, fg=TEXT_MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 14))

        tk.Label(wrap, text="Enable or disable access to each module:",
                 bg=APP_BG, fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 8))

        allowed = self.app.auth_service.get_user_permissions(self.user["id"], self.user["role"])

        box = tk.Frame(wrap, bg=APP_BG)
        box.pack(fill="x")

        for module in APP_MODULES:
            row = tk.Frame(box, bg=APP_BG)
            row.pack(fill="x", pady=3)
            var = tk.IntVar(value=1 if module in allowed else 0)
            self.permission_vars[module] = var
            tk.Checkbutton(
                row, text=module, variable=var,
                bg=APP_BG, fg=TEXT_DARK, activebackground=APP_BG,
                selectcolor=APP_BG, font=("Segoe UI", 10), anchor="w"
            ).pack(side="left")

        tk.Button(wrap, text="Save Module Assignment", command=self.save_privileges,
                  bg=ACCENT_OLIVE, fg="white", activebackground="#5a6435",
                  bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"),
                  height=2).pack(fill="x", pady=(20, 0))

    def save_privileges(self):
        try:
            permissions = {m: v.get() for m, v in self.permission_vars.items()}
            self.app.auth_service.set_user_permissions(
                actor_id=self.app.current_user.id,
                user_id=self.user["id"],
                permissions=permissions
            )
            messagebox.showinfo("Saved", "Module assignments updated.\nChanges apply on next login.")
            self.parent_page.load_users()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))


class StaffViewWindow(tk.Toplevel):
    """Read-only staff profile viewer."""
    def __init__(self, app: PanaloApp, user: dict):
        super().__init__()
        self.app = app
        self.user = user
        self.title(f"Staff Profile — {user['full_name']}")
        self.geometry("420x500")
        self.resizable(False, False)
        self.configure(bg=APP_BG)
        self.grab_set()
        self.build_ui()

    def build_ui(self):
        wrap = tk.Frame(self, bg=APP_BG, padx=28, pady=22)
        wrap.pack(fill="both", expand=True)

        # Avatar circle
        av = tk.Canvas(wrap, width=64, height=64, bg=APP_BG, highlightthickness=0)
        av.pack(anchor="w")
        av.create_oval(0, 0, 64, 64, fill=ACCENT_OLIVE, outline="")
        initials = "".join(p[0].upper() for p in self.user["full_name"].split()[:2])
        av.create_text(32, 32, text=initials, fill="white", font=("Georgia", 22, "bold"))

        tk.Label(wrap, text=self.user["full_name"], bg=APP_BG, fg=TEXT_DARK,
                 font=("Georgia", 15, "bold")).pack(anchor="w", pady=(8, 0))
        tk.Label(wrap, text=f"@{self.user['username']}  ·  {self.user['role']}",
                 bg=APP_BG, fg=TEXT_MUTED, font=("Segoe UI", 10)).pack(anchor="w")

        sep = tk.Frame(wrap, height=1, bg=BORDER_SOFT)
        sep.pack(fill="x", pady=14)

        def row(label, val):
            r = tk.Frame(wrap, bg=APP_BG)
            r.pack(fill="x", pady=3)
            tk.Label(r, text=label, bg=APP_BG, fg=TEXT_MUTED,
                     font=("Segoe UI", 9), width=16, anchor="w").pack(side="left")
            tk.Label(r, text=val or "—", bg=APP_BG, fg=TEXT_DARK,
                     font=("Segoe UI", 10)).pack(side="left")

        row("Email",        self.user.get("email") or "")
        row("Phone",        self.user.get("phone_number") or "")
        row("Status",       "Active" if self.user.get("is_active", 1) else "Inactive")
        row("Bypass PIN",   "Set ✔" if self.user.get("has_bypass_pin") else "Not set")
        row("Created",      str(self.user.get("created_at",""))[:10])

        sep2 = tk.Frame(wrap, height=1, bg=BORDER_SOFT)
        sep2.pack(fill="x", pady=14)

        tk.Label(wrap, text="Assigned Modules:", bg=APP_BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 6))

        allowed = self.app.auth_service.get_user_permissions(self.user["id"], self.user["role"])
        mods_text = "  ·  ".join(sorted(allowed)) if allowed else "No modules assigned"
        tk.Label(wrap, text=mods_text, bg=APP_BG, fg=TEXT_DARK,
                 font=("Segoe UI", 9), wraplength=350, justify="left").pack(anchor="w")

        tk.Button(wrap, text="Close", command=self.destroy,
                  bg=BORDER_SOFT, fg=TEXT_DARK, bd=0, cursor="hand2",
                  font=("Segoe UI", 10), height=2).pack(fill="x", pady=(18, 0))


class BypassPinWindow(tk.Toplevel):
    """Admin sets or removes a bypass PIN for a user."""
    def __init__(self, app: PanaloApp, parent_page: UserManagementPage, user: dict):
        super().__init__()
        self.app = app
        self.parent_page = parent_page
        self.user = user
        self.title(f"Bypass PIN — {user['full_name']}")
        self.geometry("400x360")
        self.resizable(False, False)
        self.configure(bg=APP_BG)
        self.grab_set()
        self.pin_var     = tk.StringVar()
        self.confirm_var = tk.StringVar()
        self.build_ui()

    def build_ui(self):
        wrap = tk.Frame(self, bg=APP_BG, padx=28, pady=22)
        wrap.pack(fill="both", expand=True)

        tk.Label(wrap, text="Bypass PIN Setup", bg=APP_BG, fg=TEXT_DARK,
                 font=("Georgia", 16, "bold")).pack(anchor="w")
        tk.Label(wrap, text=f"User: {self.user['full_name']}", bg=APP_BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 4))

        has_pin = self.user.get("has_bypass_pin", False)
        status_color = "#5a7a2e" if has_pin else TEXT_MUTED
        status_text  = "● Bypass PIN is currently SET" if has_pin else "○ No bypass PIN set"
        tk.Label(wrap, text=status_text, bg=APP_BG, fg=status_color,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 12))

        tk.Label(wrap,
                 text="A bypass PIN (4–6 digits) lets this authorized user\noverride system restrictions when required.",
                 bg=APP_BG, fg=TEXT_MUTED, font=("Segoe UI", 9),
                 justify="left").pack(anchor="w", pady=(0, 12))

        def pin_field(label, var):
            tk.Label(wrap, text=label, bg=APP_BG, fg=TEXT_DARK,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 1))
            box = tk.Frame(wrap, bg="white", highlightbackground=BORDER_SOFT, highlightthickness=1)
            box.pack(fill="x")
            tk.Entry(box, textvariable=var, show="●", bd=0, bg="white",
                     fg=TEXT_DARK, font=("Segoe UI", 13),
                     justify="center").pack(fill="x", padx=8, pady=7)

        pin_field("New PIN (4–6 digits)", self.pin_var)
        pin_field("Confirm PIN",          self.confirm_var)

        tk.Button(wrap, text="Set Bypass PIN", command=self.set_pin,
                  bg=ACCENT_OLIVE, fg="white", activebackground="#5a6435",
                  bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"),
                  height=2).pack(fill="x", pady=(14, 4))

        if has_pin:
            tk.Button(wrap, text="Remove Bypass PIN", command=self.remove_pin,
                      bg="#f3e4de", fg=DANGER_RED, activebackground="#edd8d2",
                      bd=0, cursor="hand2", font=("Segoe UI", 10),
                      height=2).pack(fill="x")

    def set_pin(self):
        pin     = self.pin_var.get().strip()
        confirm = self.confirm_var.get().strip()
        if pin != confirm:
            messagebox.showerror("Mismatch", "PINs do not match.")
            return
        try:
            self.app.auth_service.set_bypass_pin(
                actor_id=self.app.current_user.id,
                target_user_id=self.user["id"],
                pin=pin
            )
            messagebox.showinfo("Done", f"Bypass PIN set for {self.user['full_name']}.")
            self.parent_page.load_users()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def remove_pin(self):
        if not messagebox.askyesno("Confirm", f"Remove bypass PIN for {self.user['full_name']}?"):
            return
        try:
            self.app.auth_service.remove_bypass_pin(
                actor_id=self.app.current_user.id,
                target_user_id=self.user["id"]
            )
            messagebox.showinfo("Done", "Bypass PIN removed.")
            self.parent_page.load_users()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))


class PasswordRecoveryWindow(tk.Toplevel):
    """Admin resets a staff member's forgotten password."""
    def __init__(self, app: PanaloApp, parent_page: UserManagementPage, user: dict):
        super().__init__()
        self.app = app
        self.parent_page = parent_page
        self.user = user
        self.title(f"Reset Password — {user['full_name']}")
        self.geometry("420x380")
        self.resizable(False, False)
        self.configure(bg=APP_BG)
        self.grab_set()
        self.new_pw_var    = tk.StringVar()
        self.confirm_pw_var = tk.StringVar()
        self.build_ui()

    def build_ui(self):
        wrap = tk.Frame(self, bg=APP_BG, padx=28, pady=22)
        wrap.pack(fill="both", expand=True)

        tk.Label(wrap, text="🔒  Password Recovery", bg=APP_BG, fg=TEXT_DARK,
                 font=("Georgia", 16, "bold")).pack(anchor="w")
        tk.Label(wrap, text=f"Staff account: {self.user['full_name']}  (@{self.user['username']})",
                 bg=APP_BG, fg=TEXT_MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 14))

        tk.Label(wrap,
                 text="Set a new password for this staff account.\nThe staff member can change it after logging in.",
                 bg=APP_BG, fg=TEXT_MUTED, font=("Segoe UI", 9), justify="left").pack(anchor="w", pady=(0, 10))

        def pw_field(label, var):
            tk.Label(wrap, text=label, bg=APP_BG, fg=TEXT_DARK,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8, 1))
            box = tk.Frame(wrap, bg="white", highlightbackground=BORDER_SOFT, highlightthickness=1)
            box.pack(fill="x")
            e = tk.Entry(box, textvariable=var, show="*", bd=0, bg="white",
                         fg=TEXT_DARK, insertbackground=TEXT_DARK, font=("Segoe UI", 10))
            e.pack(fill="x", padx=8, pady=6)
            return e

        pw_field("New Password *", self.new_pw_var)
        pw_field("Confirm New Password *", self.confirm_pw_var)

        tk.Label(wrap,
                 text="Min 8 chars · uppercase · lowercase · number · special char",
                 bg=APP_BG, fg=TEXT_MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))

        tk.Button(wrap, text="Reset Password", command=self.reset_password,
                  bg=DANGER_RED, fg="white", activebackground="#7a1818",
                  bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"),
                  height=2).pack(fill="x", pady=(16, 0))

    def reset_password(self):
        new_pw  = self.new_pw_var.get()
        confirm = self.confirm_pw_var.get()
        if new_pw != confirm:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return
        try:
            self.app.auth_service.reset_password_by_admin(
                actor_id=self.app.current_user.id,
                target_user_id=self.user["id"],
                new_password=new_pw
            )
            messagebox.showinfo("Done",
                f"Password for {self.user['full_name']} has been reset successfully.\n"
                "Please inform the staff member of the new password.")
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
            style="Header.TLabel"
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

        self.table.column("id", width=50, anchor="center")
        self.table.column("full_name", width=220)
        self.table.column("contact_number", width=140)
        self.table.column("notes", width=350)
        self.table.column("created_at", width=150)

        self.table.tag_configure(
            "normal",
            background=APP_BG,
            foreground=TEXT_DARK
        )

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

        search_entry.bind("<Return>", lambda event: self.search_clients())

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
                ),
                tags=("normal",)
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
                ),
                tags=("normal",)
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
            style="Section.TLabel"
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
            style="Section.TLabel"
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(
            frame,
            text=f"Client: {self.schedule['client_name'] or ''}",
            style="Section.TLabel"
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
            style="Section.TLabel"
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
                ),
                tags=("normal",)
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


class ReportsPage(ttk.Frame):
    def __init__(self, parent, app: PanaloApp):
        super().__init__(parent)

        self.app = app
        self.reports_data = {}

        self.build_ui()
        self.load_reports()

    def build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            header,
            text="Reports",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Refresh Reports",
            command=self.load_reports
        ).pack(side="right")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.overview_tab = ttk.Frame(self.notebook, padding=15)
        self.bookings_tab = ttk.Frame(self.notebook, padding=15)
        self.payments_tab = ttk.Frame(self.notebook, padding=15)
        self.schedules_tab = ttk.Frame(self.notebook, padding=15)
        self.clients_tab = ttk.Frame(self.notebook, padding=15)
        self.packages_tab = ttk.Frame(self.notebook, padding=15)

        self.notebook.add(self.overview_tab, text="Overview")
        self.notebook.add(self.bookings_tab, text="Bookings")
        self.notebook.add(self.payments_tab, text="Payments")
        self.notebook.add(self.schedules_tab, text="Schedules")
        self.notebook.add(self.clients_tab, text="Clients")
        self.notebook.add(self.packages_tab, text="Packages")

    def clear_tab(self, tab):
        for widget in tab.winfo_children():
            widget.destroy()

    def format_price(self, value):
        try:
            return f"₱{float(value or 0):,.2f}"
        except Exception:
            return "₱0.00"

    def create_card(self, parent, title, value):
        card = tk.Frame(
            parent,
            bg="white",
            relief="solid",
            bd=1
        )
        card.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        tk.Label(
            card,
            text=title,
            bg="white",
            fg="#555555",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=12, pady=(10, 2))

        tk.Label(
            card,
            text=value,
            bg="white",
            fg="#111111",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=12, pady=(0, 10))

        return card

    def create_table(self, parent, columns, headings, widths=None, height=12):
        table = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            height=height
        )

        for index, column in enumerate(columns):
            table.heading(column, text=headings[index])
            width = widths[index] if widths else 120
            table.column(column, width=width)

        table.pack(fill="both", expand=True, pady=(8, 0))

        return table

    def load_reports(self):
        self.reports_data = self.app.reports_service.get_all_reports()

        self.render_overview_tab()
        self.render_bookings_tab()
        self.render_payments_tab()
        self.render_schedules_tab()
        self.render_clients_tab()
        self.render_packages_tab()

    def render_overview_tab(self):
        self.clear_tab(self.overview_tab)

        booking = self.reports_data["booking"]
        payment = self.reports_data["payment"]
        schedule = self.reports_data["schedule"]
        client = self.reports_data["client"]

        row1 = ttk.Frame(self.overview_tab)
        row1.pack(fill="x")

        self.create_card(row1, "Total Bookings", str(booking["total_bookings"]))
        self.create_card(row1, "Total Clients", str(client["total_clients"]))
        self.create_card(row1, "Upcoming Events", str(schedule["upcoming_count"]))
        self.create_card(row1, "This Month Schedules", str(schedule["this_month_count"]))

        row2 = ttk.Frame(self.overview_tab)
        row2.pack(fill="x", pady=(8, 0))

        self.create_card(row2, "Expected Revenue", self.format_price(payment["expected_revenue"]))
        self.create_card(row2, "Verified Payments", self.format_price(payment["verified_paid"]))
        self.create_card(row2, "Pending Payments", self.format_price(payment["pending_payment"]))
        self.create_card(row2, "Unpaid Balance", self.format_price(payment["total_balance"]))

        ttk.Label(
            self.overview_tab,
            text="Upcoming Events",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(20, 0))

        table = self.create_table(
            self.overview_tab,
            columns=("date", "time", "client", "event_type", "package", "status"),
            headings=("Date", "Time", "Client", "Event Type", "Package", "Status"),
            widths=(100, 90, 160, 140, 220, 110),
            height=8
        )

        for event in schedule["upcoming_events"]:
            table.insert(
                "",
                "end",
                values=(
                    event["event_date"] or "",
                    event["event_time"] or "",
                    event["client_name"] or "",
                    event["event_type"] or "",
                    event["package_name"] or "",
                    event["status"] or ""
                )
            )

    def render_bookings_tab(self):
        self.clear_tab(self.bookings_tab)

        booking = self.reports_data["booking"]

        row = ttk.Frame(self.bookings_tab)
        row.pack(fill="x")

        self.create_card(row, "Total Bookings", str(booking["total_bookings"]))

        ttk.Label(
            self.bookings_tab,
            text="Bookings by Status",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(20, 0))

        status_table = self.create_table(
            self.bookings_tab,
            columns=("status", "count"),
            headings=("Status", "Count"),
            widths=(240, 120),
            height=7
        )

        for item in booking["by_status"]:
            status_table.insert(
                "",
                "end",
                values=(
                    item["status"],
                    item["count"]
                )
            )

        ttk.Label(
            self.bookings_tab,
            text="Bookings by Event Type",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(20, 0))

        event_type_table = self.create_table(
            self.bookings_tab,
            columns=("event_type", "count"),
            headings=("Event Type", "Count"),
            widths=(240, 120),
            height=7
        )

        for item in booking["by_event_type"]:
            event_type_table.insert(
                "",
                "end",
                values=(
                    item["event_type"],
                    item["count"]
                )
            )

    def render_payments_tab(self):
        self.clear_tab(self.payments_tab)

        payment = self.reports_data["payment"]

        row1 = ttk.Frame(self.payments_tab)
        row1.pack(fill="x")

        self.create_card(row1, "Expected Revenue", self.format_price(payment["expected_revenue"]))
        self.create_card(row1, "Verified Payments", self.format_price(payment["verified_paid"]))
        self.create_card(row1, "Pending Payments", self.format_price(payment["pending_payment"]))
        self.create_card(row1, "Refunded Amount", self.format_price(payment["refunded_amount"]))

        row2 = ttk.Frame(self.payments_tab)
        row2.pack(fill="x", pady=(8, 0))

        self.create_card(row2, "Total Balance", self.format_price(payment["total_balance"]))
        self.create_card(row2, "Paid Bookings", str(payment["paid_count"]))
        self.create_card(row2, "Partial Bookings", str(payment["partial_count"]))
        self.create_card(row2, "Unpaid Bookings", str(payment["unpaid_count"]))

        ttk.Label(
            self.payments_tab,
            text="Booking Payment Status",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(20, 0))

        table = self.create_table(
            self.payments_tab,
            columns=("booking_id", "client", "total", "paid", "balance", "status"),
            headings=("Booking ID", "Client", "Total", "Paid", "Balance", "Payment Status"),
            widths=(90, 180, 120, 120, 120, 130),
            height=10
        )

        for item in payment["booking_payment_statuses"]:
            table.insert(
                "",
                "end",
                values=(
                    item["booking_id"],
                    item["client_name"] or "",
                    self.format_price(item["total_amount"]),
                    self.format_price(item["net_paid"]),
                    self.format_price(item["balance"]),
                    item["payment_status"]
                )
            )

    def render_schedules_tab(self):
        self.clear_tab(self.schedules_tab)

        schedule = self.reports_data["schedule"]

        row = ttk.Frame(self.schedules_tab)
        row.pack(fill="x")

        self.create_card(row, "Today", str(schedule["today_count"]))
        self.create_card(row, "Upcoming", str(schedule["upcoming_count"]))
        self.create_card(row, "This Month", str(schedule["this_month_count"]))
        self.create_card(row, "Cancelled", str(schedule["cancelled_count"]))

        ttk.Label(
            self.schedules_tab,
            text="Upcoming Schedules",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(20, 0))

        table = self.create_table(
            self.schedules_tab,
            columns=("date", "time", "client", "event_type", "package", "location", "status"),
            headings=("Date", "Time", "Client", "Event Type", "Package", "Location", "Status"),
            widths=(100, 90, 150, 130, 190, 190, 110),
            height=12
        )

        for event in schedule["upcoming_events"]:
            table.insert(
                "",
                "end",
                values=(
                    event["event_date"] or "",
                    event["event_time"] or "",
                    event["client_name"] or "",
                    event["event_type"] or "",
                    event["package_name"] or "",
                    event["event_location"] or "",
                    event["status"] or ""
                )
            )

    def render_clients_tab(self):
        self.clear_tab(self.clients_tab)

        client = self.reports_data["client"]

        row = ttk.Frame(self.clients_tab)
        row.pack(fill="x")

        self.create_card(row, "Total Clients", str(client["total_clients"]))
        self.create_card(row, "Clients With Bookings", str(client["clients_with_bookings"]))
        self.create_card(row, "Clients Without Bookings", str(client["clients_without_bookings"]))

        ttk.Label(
            self.clients_tab,
            text="Recent Clients",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(20, 0))

        table = self.create_table(
            self.clients_tab,
            columns=("id", "name", "contact", "notes", "created_at"),
            headings=("ID", "Client Name", "Contact", "Notes", "Created At"),
            widths=(60, 200, 140, 350, 160),
            height=12
        )

        for item in client["recent_clients"]:
            table.insert(
                "",
                "end",
                values=(
                    item["id"],
                    item["full_name"] or "",
                    item["contact_number"] or "",
                    item["notes"] or "",
                    item["created_at"] or ""
                )
            )

    def render_packages_tab(self):
        self.clear_tab(self.packages_tab)

        packages = self.reports_data["packages"]

        ttk.Label(
            self.packages_tab,
            text="Package Performance",
            style="Section.TLabel"
        ).pack(anchor="w", pady=(0, 10))

        table = self.create_table(
            self.packages_tab,
            columns=("id", "package_name", "booking_count", "revenue"),
            headings=("ID", "Package", "Booking Count", "Total Revenue"),
            widths=(60, 320, 130, 150),
            height=15
        )

        for item in packages:
            table.insert(
                "",
                "end",
                values=(
                    item["id"],
                    item["package_name"] or "",
                    item["booking_count"],
                    self.format_price(item["total_revenue"])
                )
            )


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
            style="Section.TLabel"
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