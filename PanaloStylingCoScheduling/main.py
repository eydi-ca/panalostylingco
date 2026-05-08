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

MAX_ACTIVE_BOOKINGS_PER_DAY = 1

SCHEDULE_CARD_BG = "#fffaf1"
SCHEDULE_CELL_BG = "#fffaf1"
SCHEDULE_CELL_ALT_BG = "#fcf3e8"
SCHEDULE_BORDER = "#dccfbf"
SCHEDULE_BOOKED_BG = "#e8c0b6"
SCHEDULE_AVAILABLE_BG = "#d8dfbd"
SCHEDULE_LIMITED_BG = "#e9c98e"
SCHEDULE_TEXT = "#2f2b1f"

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

        self.scroll_canvas = tk.Canvas(
            self,
            bg=APP_BG,
            highlightthickness=0,
            bd=0
        )
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.scroll_canvas.yview
        )
        self.scrollbar.pack(side="right", fill="y")

        self.scroll_canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.content = ttk.Frame(self.scroll_canvas)

        self.content_window = self.scroll_canvas.create_window(
            0,
            0,
            window=self.content,
            anchor="nw"
        )

        self.content.bind(
            "<Configure>",
            lambda event: self.scroll_canvas.configure(
                scrollregion=self.scroll_canvas.bbox("all")
            )
        )

        self.scroll_canvas.bind(
            "<Configure>",
            self.resize_dashboard_content
        )

        self.scroll_canvas.bind_all(
            "<MouseWheel>",
            self.on_dashboard_mousewheel
        )

    def resize_dashboard_content(self, event=None):
        canvas_width = self.scroll_canvas.winfo_width()

        self.scroll_canvas.itemconfigure(
            self.content_window,
            width=canvas_width
        )

    def on_dashboard_mousewheel(self, event):
        self.scroll_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

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
        table_frame = tk.Frame(
            parent,
            bg=APP_BG,
            bd=0,
            highlightthickness=0
        )
        table_frame.pack(fill="both", expand=True)

        table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=height
        )

        for index, column in enumerate(columns):
            table.heading(column, text=headings[index])
            width = widths[index] if widths else 120
            table.column(column, width=width, anchor="w", stretch=True)

        table.tag_configure(
            "normal",
            background=APP_BG,
            foreground=TEXT_DARK
        )

        table.pack(fill="both", expand=True)

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
        graph_row.pack(fill="x", expand=False, pady=(6, 8))

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
        operational_row.pack(fill="x", expand=False, pady=(6, 8))

        today_box = ttk.LabelFrame(operational_row, text="Schedule in Selected Range", padding=10)
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

        for item in data["schedule_range"]:
            today_table.insert(
                "",
                "end",
                values=(
                    item["event_time"] or "",
                    item["client_name"] or "",
                    item["event_type"] or "",
                    item["status"] or ""
                ),
                tags = ("normal",)
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
                ),
                tags=("normal",)
            )

        queue_table = self.create_table(
            queue_box,
            columns=("client", "type", "amount", "method", "date"),
            headings=("Client", "Type", "Amount", "Method", "Date"),
            widths=(150, 120, 100, 100, 100),
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
                    item["payment_method"] or "",
                    item["payment_date"] or ""
                ),
                tags=("normal",)
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
                ),
                tags = ("normal",)
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
            style="Header.TLabel"
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

        self.today = date.today()
        self.current_date = self.today

        self.active_view = "month"
        self.events = []

        self.build_ui()
        self.refresh_page()

    # =========================
    # UI STRUCTURE
    # =========================

    def build_ui(self):
        self.configure(style="TFrame")

        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 12))

        title_group = ttk.Frame(header)
        title_group.pack(side="left", fill="x", expand=True)

        ttk.Label(
            title_group,
            text="Schedule",
            style="Header.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            title_group,
            text="View, manage, reschedule, and cancel event schedules.",
            style="Subheader.TLabel"
        ).pack(anchor="w", pady=(2, 0))

        ttk.Button(
            header,
            text="⟳ Refresh",
            command=self.refresh_page
        ).pack(side="right")

        # Navigation row
        nav_row = ttk.Frame(self)
        nav_row.pack(fill="x", pady=(0, 12))

        ttk.Button(
            nav_row,
            text="‹ Previous",
            command=self.go_previous
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            nav_row,
            text="Today",
            command=self.go_today
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            nav_row,
            text="Next ›",
            command=self.go_next
        ).pack(side="left")

        self.period_title_var = tk.StringVar()

        ttk.Label(
            nav_row,
            textvariable=self.period_title_var,
            font=("Georgia", 24, "bold"),
            foreground=ACCENT_OLIVE,
            background=APP_BG
        ).pack(side="left", expand=True)

        # View buttons
        view_row = ttk.Frame(self)
        view_row.pack(fill="x", pady=(0, 10))

        self.view_buttons = {}

        for view_key, label in [
            ("month", "Month"),
            ("week", "Week"),
            ("day", "Day"),
            ("list", "Schedule List")
        ]:
            btn = tk.Button(
                view_row,
                text=label,
                command=lambda key=view_key: self.switch_view(key),
                bg=SCHEDULE_CARD_BG,
                fg=TEXT_MUTED,
                activebackground="#f1eadc",
                activeforeground=ACCENT_OLIVE,
                relief="solid",
                bd=1,
                font=("Georgia", 11),
                padx=18,
                pady=7,
                cursor="hand2"
            )
            btn.pack(side="left", padx=(0, 6))
            self.view_buttons[view_key] = btn

        # Main content shell
        self.body = ttk.Frame(self)
        self.body.pack(fill="both", expand=True)

        self.main_panel = ttk.Frame(self.body)
        self.main_panel.pack(side="left", fill="both", expand=True, padx=(0, 14))

        self.side_panel = ttk.Frame(self.body, width=330)
        self.side_panel.pack(side="right", fill="y")
        self.side_panel.pack_propagate(False)

    def create_card(self, parent):
        card = tk.Frame(
            parent,
            bg=SCHEDULE_CARD_BG,
            highlightbackground=SCHEDULE_BORDER,
            highlightthickness=1,
            bd=0
        )
        return card

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def refresh_page(self):
        self.load_schedule_data()
        self.render_page()

    def render_page(self):
        self.clear_frame(self.main_panel)
        self.clear_frame(self.side_panel)

        self.update_period_title()
        self.update_view_buttons()

        if self.active_view == "month":
            self.render_month_view()
        elif self.active_view == "week":
            self.render_week_view()
        elif self.active_view == "day":
            self.render_day_view()
        else:
            self.render_schedule_list_view()

        self.render_side_panel()

    def update_view_buttons(self):
        for key, button in self.view_buttons.items():
            if key == self.active_view:
                button.configure(
                    fg=ACCENT_OLIVE,
                    bg=SIDEBAR_ACTIVE_BG,
                    font=("Georgia", 11, "bold")
                )
            else:
                button.configure(
                    fg=TEXT_MUTED,
                    bg=SCHEDULE_CARD_BG,
                    font=("Georgia", 11)
                )

    # =========================
    # NAVIGATION
    # =========================

    def switch_view(self, view_key):
        self.active_view = view_key
        self.refresh_page()

    def go_today(self):
        self.current_date = self.today
        self.refresh_page()

    def go_previous(self):
        if self.active_view == "month":
            year = self.current_date.year
            month = self.current_date.month

            if month == 1:
                self.current_date = date(year - 1, 12, 1)
            else:
                self.current_date = date(year, month - 1, 1)

        elif self.active_view == "week":
            self.current_date = self.current_date - timedelta(days=7)

        elif self.active_view == "day":
            self.current_date = self.current_date - timedelta(days=1)

        else:
            self.current_date = self.current_date - timedelta(days=30)

        self.refresh_page()

    def go_next(self):
        if self.active_view == "month":
            year = self.current_date.year
            month = self.current_date.month

            if month == 12:
                self.current_date = date(year + 1, 1, 1)
            else:
                self.current_date = date(year, month + 1, 1)

        elif self.active_view == "week":
            self.current_date = self.current_date + timedelta(days=7)

        elif self.active_view == "day":
            self.current_date = self.current_date + timedelta(days=1)

        else:
            self.current_date = self.current_date + timedelta(days=30)

        self.refresh_page()

    def update_period_title(self):
        if self.active_view == "month":
            title = self.current_date.strftime("%B %Y")

        elif self.active_view == "week":
            start, end = self.get_week_start_end()
            title = f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"

        elif self.active_view == "day":
            title = self.current_date.strftime("%B %d, %Y")

        else:
            start, end = self.get_month_start_end()
            title = f"Schedules: {start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"

        self.period_title_var.set(title)

    # =========================
    # DATE RANGE HELPERS
    # =========================

    def get_month_start_end(self):
        first_day = date(self.current_date.year, self.current_date.month, 1)
        last_day = date(
            self.current_date.year,
            self.current_date.month,
            calendar.monthrange(self.current_date.year, self.current_date.month)[1]
        )

        return first_day, last_day

    def get_week_start_end(self):
        # Monday start
        start = self.current_date - timedelta(days=self.current_date.weekday())
        end = start + timedelta(days=6)

        return start, end

    def get_current_range(self):
        if self.active_view == "month":
            return self.get_month_start_end()

        if self.active_view == "week":
            return self.get_week_start_end()

        if self.active_view == "day":
            return self.current_date, self.current_date

        return self.get_month_start_end()

    # =========================
    # DATABASE
    # =========================

    def load_schedule_data(self):
        start_date, end_date = self.get_current_range()

        start_text = start_date.strftime("%Y-%m-%d")
        end_text = end_date.strftime("%Y-%m-%d")

        try:
            with self.app.db.get_conn() as conn:
                rows = conn.execute(
                    """
                    SELECT
                        b.id,
                        b.event_date,
                        b.event_time,
                        b.event_location,
                        b.guest_count,
                        b.theme_motif,
                        b.total_amount,
                        c.full_name AS client_name,
                        et.name AS event_type,
                        p.package_name,
                        bs.name AS status
                    FROM bookings b
                    LEFT JOIN clients c ON b.client_id = c.id
                    LEFT JOIN event_types et ON b.event_type_id = et.id
                    LEFT JOIN packages p ON b.package_id = p.id
                    LEFT JOIN booking_statuses bs ON b.status_id = bs.id
                    WHERE b.event_date BETWEEN ? AND ?
                    ORDER BY b.event_date ASC, b.event_time ASC
                    """,
                    (start_text, end_text)
                ).fetchall()

            self.events = [dict(row) for row in rows]

        except Exception as e:
            self.events = []
            messagebox.showerror("Schedule Error", f"Unable to load schedules: {e}")

    def get_events_by_date(self):
        grouped = {}

        for event in self.events:
            event_date = event["event_date"]

            if event_date not in grouped:
                grouped[event_date] = []

            grouped[event_date].append(event)

        return grouped

    def get_cancelled_status_id(self):
        with self.app.db.get_conn() as conn:
            row = conn.execute(
                """
                SELECT id
                FROM booking_statuses
                WHERE LOWER(name) = 'cancelled'
                LIMIT 1
                """
            ).fetchone()

            if row:
                return row["id"]

            cursor = conn.execute(
                """
                INSERT INTO booking_statuses (name)
                VALUES ('Cancelled')
                """
            )
            conn.commit()

            return cursor.lastrowid

    def count_active_bookings_on_date(self, event_date, exclude_booking_id=None):
        query = """
            SELECT COUNT(*) AS count
            FROM bookings b
            LEFT JOIN booking_statuses bs ON b.status_id = bs.id
            WHERE b.event_date = ?
              AND LOWER(COALESCE(bs.name, '')) != 'cancelled'
        """

        params = [event_date]

        if exclude_booking_id:
            query += " AND b.id != ?"
            params.append(exclude_booking_id)

        with self.app.db.get_conn() as conn:
            row = conn.execute(query, params).fetchone()

        return int(row["count"] or 0)

    def get_booked_dates_for_month(self, year, month, exclude_booking_id=None):
        first_day = date(year, month, 1)
        last_day = date(
            year,
            month,
            calendar.monthrange(year, month)[1]
        )

        query = """
            SELECT
                b.id,
                b.event_date,
                bs.name AS status
            FROM bookings b
            LEFT JOIN booking_statuses bs ON b.status_id = bs.id
            WHERE b.event_date BETWEEN ? AND ?
              AND LOWER(COALESCE(bs.name, '')) != 'cancelled'
        """

        params = [
            first_day.strftime("%Y-%m-%d"),
            last_day.strftime("%Y-%m-%d")
        ]

        if exclude_booking_id:
            query += " AND b.id != ?"
            params.append(exclude_booking_id)

        with self.app.db.get_conn() as conn:
            rows = conn.execute(query, params).fetchall()

        booked_dates = {}

        for row in rows:
            event_date = row["event_date"]

            if event_date not in booked_dates:
                booked_dates[event_date] = 0

            booked_dates[event_date] += 1

        return booked_dates

    def update_booking_schedule(self, booking_id, new_date, new_time):
        with self.app.db.get_conn() as conn:
            conn.execute(
                """
                UPDATE bookings
                SET event_date = ?,
                    event_time = ?
                WHERE id = ?
                """,
                (new_date, new_time, booking_id)
            )
            conn.commit()

    def cancel_booking_schedule(self, booking_id):
        cancelled_status_id = self.get_cancelled_status_id()

        with self.app.db.get_conn() as conn:
            conn.execute(
                """
                UPDATE bookings
                SET status_id = ?
                WHERE id = ?
                """,
                (cancelled_status_id, booking_id)
            )
            conn.commit()

    # =========================
    # STATUS HELPERS
    # =========================

    def get_date_status(self, events):
        if not events:
            return "available"

        active_events = [
            event for event in events
            if str(event.get("status", "")).lower() != "cancelled"
        ]

        if len(active_events) == 0:
            return "available"

        if len(active_events) >= MAX_ACTIVE_BOOKINGS_PER_DAY:
            return "booked"

        return "limited"

    def get_status_colors(self, status):
        if status == "available":
            return SCHEDULE_AVAILABLE_BG, ACCENT_OLIVE

        if status == "limited":
            return SCHEDULE_LIMITED_BG, "#6a4a11"

        return SCHEDULE_BOOKED_BG, "#6c2c22"

    # =========================
    # MONTH VIEW
    # =========================

    def render_month_view(self):
        grouped_events = self.get_events_by_date()

        card = self.create_card(self.main_panel)
        card.pack(fill="both", expand=True)

        calendar_frame = tk.Frame(card, bg=SCHEDULE_CARD_BG)
        calendar_frame.pack(fill="both", expand=True, padx=14, pady=14)

        weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        for col, day_name in enumerate(weekdays):
            tk.Label(
                calendar_frame,
                text=day_name,
                bg=SCHEDULE_CARD_BG,
                fg=TEXT_DARK,
                font=("Georgia", 11, "bold")
            ).grid(row=0, column=col, sticky="nsew", pady=(0, 8))

        for col in range(7):
            calendar_frame.grid_columnconfigure(col, weight=1, uniform="calendar_col")

        for row in range(1, 7):
            calendar_frame.grid_rowconfigure(row, weight=1, uniform="calendar_row")

        first_weekday, days_in_month = calendar.monthrange(
            self.current_date.year,
            self.current_date.month
        )

        start_col = (first_weekday + 1) % 7
        day_number = 1

        for week in range(6):
            for col in range(7):
                cell = tk.Frame(
                    calendar_frame,
                    bg=SCHEDULE_CELL_BG,
                    highlightbackground=SCHEDULE_BORDER,
                    highlightthickness=1,
                    bd=0
                )
                cell.grid(
                    row=week + 1,
                    column=col,
                    sticky="nsew"
                )

                if week == 0 and col < start_col:
                    continue

                if day_number > days_in_month:
                    continue

                current_day = date(
                    self.current_date.year,
                    self.current_date.month,
                    day_number
                )
                date_text = current_day.strftime("%Y-%m-%d")
                events = grouped_events.get(date_text, [])
                status = self.get_date_status(events)

                self.populate_month_cell(
                    cell=cell,
                    current_day=current_day,
                    date_text=date_text,
                    events=events,
                    status=status
                )

                day_number += 1

        self.render_legend(card)

    def populate_month_cell(self, cell, current_day, date_text, events, status):
        tk.Label(
            cell,
            text=str(current_day.day),
            bg=SCHEDULE_CELL_BG,
            fg=TEXT_DARK,
            font=("Segoe UI", 10, "bold" if current_day == self.today else "normal"),
            anchor="nw"
        ).pack(anchor="nw", padx=8, pady=6)

        active_events = [
            event for event in events
            if str(event.get("status", "")).lower() != "cancelled"
        ]

        cancelled_events = [
            event for event in events
            if str(event.get("status", "")).lower() == "cancelled"
        ]

        if active_events:
            badge_bg, badge_fg = self.get_status_colors(status)
            label_text = "Booked" if len(active_events) == 1 else f"{len(active_events)} Bookings"

            badge = tk.Label(
                cell,
                text=label_text,
                bg=badge_bg,
                fg=badge_fg,
                font=("Segoe UI", 8),
                padx=7,
                pady=3,
                cursor="hand2"
            )
            badge.pack(anchor="center", pady=(8, 0))

            badge.bind(
                "<Button-1>",
                lambda event, date_value=date_text: self.open_day_details(date_value)
            )

        if cancelled_events:
            cancelled = tk.Label(
                cell,
                text=f"{len(cancelled_events)} Cancelled",
                bg="#efc0c0",
                fg="#7a1f1f",
                font=("Segoe UI", 8),
                padx=7,
                pady=3,
                cursor="hand2"
            )
            cancelled.pack(anchor="center", pady=(4, 0))

            cancelled.bind(
                "<Button-1>",
                lambda event, date_value=date_text: self.open_day_details(date_value)
            )

        cell.bind(
            "<Button-1>",
            lambda event, date_value=date_text: self.open_day_details(date_value)
        )

    def render_legend(self, parent):
        legend = tk.Frame(parent, bg=SCHEDULE_CARD_BG)
        legend.pack(fill="x", padx=18, pady=(0, 14))

        items = [
            ("Available", SCHEDULE_AVAILABLE_BG),
            ("Booked / Fully Booked", SCHEDULE_BOOKED_BG),
            ("Limited Availability", SCHEDULE_LIMITED_BG),
            ("Cancelled", "#efc0c0"),
        ]

        for label_text, color in items:
            item = tk.Frame(legend, bg=SCHEDULE_CARD_BG)
            item.pack(side="left", padx=(0, 24))

            tk.Label(
                item,
                text="●",
                bg=SCHEDULE_CARD_BG,
                fg=color,
                font=("Segoe UI", 13)
            ).pack(side="left")

            tk.Label(
                item,
                text=label_text,
                bg=SCHEDULE_CARD_BG,
                fg=TEXT_MUTED,
                font=("Segoe UI", 9)
            ).pack(side="left", padx=(5, 0))

    # =========================
    # WEEK VIEW
    # =========================

    def render_week_view(self):
        start, end = self.get_week_start_end()
        grouped_events = self.get_events_by_date()

        card = self.create_card(self.main_panel)
        card.pack(fill="both", expand=True)

        week_frame = tk.Frame(card, bg=SCHEDULE_CARD_BG)
        week_frame.pack(fill="both", expand=True, padx=14, pady=14)

        for col in range(7):
            week_frame.grid_columnconfigure(col, weight=1, uniform="week_col")

        for col in range(7):
            day_date = start + timedelta(days=col)
            date_text = day_date.strftime("%Y-%m-%d")
            events = grouped_events.get(date_text, [])

            day_card = tk.Frame(
                week_frame,
                bg=SCHEDULE_CELL_BG,
                highlightbackground=SCHEDULE_BORDER,
                highlightthickness=1,
                bd=0
            )
            day_card.grid(row=0, column=col, sticky="nsew", padx=3, pady=3)

            tk.Label(
                day_card,
                text=day_date.strftime("%a"),
                bg=SCHEDULE_CELL_BG,
                fg=ACCENT_OLIVE,
                font=("Georgia", 12, "bold")
            ).pack(anchor="w", padx=10, pady=(10, 0))

            tk.Label(
                day_card,
                text=day_date.strftime("%b %d"),
                bg=SCHEDULE_CELL_BG,
                fg=TEXT_DARK,
                font=("Segoe UI", 10)
            ).pack(anchor="w", padx=10, pady=(0, 10))

            if not events:
                tk.Label(
                    day_card,
                    text="Available",
                    bg=SCHEDULE_CELL_BG,
                    fg=TEXT_MUTED,
                    font=("Segoe UI", 9)
                ).pack(anchor="w", padx=10, pady=6)
            else:
                for event in events:
                    self.create_event_chip(day_card, event)

    # =========================
    # DAY VIEW
    # =========================

    def render_day_view(self):
        date_text = self.current_date.strftime("%Y-%m-%d")
        events = [
            event for event in self.events
            if event["event_date"] == date_text
        ]

        card = self.create_card(self.main_panel)
        card.pack(fill="both", expand=True)

        container = tk.Frame(card, bg=SCHEDULE_CARD_BG)
        container.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            container,
            text=self.current_date.strftime("%A, %B %d, %Y"),
            bg=SCHEDULE_CARD_BG,
            fg=ACCENT_OLIVE,
            font=("Georgia", 18, "bold")
        ).pack(anchor="w", pady=(0, 14))

        if not events:
            tk.Label(
                container,
                text="No bookings scheduled for this day.",
                bg=SCHEDULE_CARD_BG,
                fg=TEXT_MUTED,
                font=("Segoe UI", 11)
            ).pack(anchor="w")
            return

        for event in events:
            self.create_day_event_card(container, event)

    def create_day_event_card(self, parent, event):
        card = tk.Frame(
            parent,
            bg="#fffdf7",
            highlightbackground=SCHEDULE_BORDER,
            highlightthickness=1,
            bd=0
        )
        card.pack(fill="x", pady=(0, 10))

        top = tk.Frame(card, bg="#fffdf7")
        top.pack(fill="x", padx=14, pady=(12, 6))

        tk.Label(
            top,
            text=event["event_type"] or "Event",
            bg="#fffdf7",
            fg=TEXT_DARK,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        tk.Label(
            top,
            text=event["status"] or "",
            bg=SIDEBAR_ACTIVE_BG,
            fg=ACCENT_OLIVE,
            font=("Segoe UI", 9),
            padx=8,
            pady=3
        ).pack(side="right")

        details = (
            f"Client: {event['client_name'] or ''}\n"
            f"Package: {event['package_name'] or ''}\n"
            f"Time: {event['event_time'] or ''}\n"
            f"Location: {event['event_location'] or ''}"
        )

        tk.Label(
            card,
            text=details,
            bg="#fffdf7",
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
            justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 10))

        actions = tk.Frame(card, bg="#fffdf7")
        actions.pack(fill="x", padx=14, pady=(0, 12))

        ttk.Button(
            actions,
            text="View Details",
            command=lambda: self.open_booking_details(event)
        ).pack(side="left")

        ttk.Button(
            actions,
            text="Reschedule",
            command=lambda: self.open_reschedule_window(event)
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            actions,
            text="Cancel Schedule",
            command=lambda: self.confirm_cancel_schedule(event)
        ).pack(side="left", padx=(8, 0))

    # =========================
    # LIST VIEW
    # =========================

    def render_schedule_list_view(self):
        card = self.create_card(self.main_panel)
        card.pack(fill="both", expand=True)

        container = tk.Frame(card, bg=SCHEDULE_CARD_BG)
        container.pack(fill="both", expand=True, padx=14, pady=14)

        columns = (
            "date",
            "time",
            "client",
            "event",
            "package",
            "status"
        )

        table = ttk.Treeview(
            container,
            columns=columns,
            show="headings",
            height=18
        )

        headings = {
            "date": "Date",
            "time": "Time",
            "client": "Client",
            "event": "Event",
            "package": "Package",
            "status": "Status"
        }

        widths = {
            "date": 110,
            "time": 90,
            "client": 170,
            "event": 150,
            "package": 220,
            "status": 110
        }

        for column in columns:
            table.heading(column, text=headings[column])
            table.column(column, width=widths[column], anchor="w")

        table.tag_configure("normal", background=APP_BG, foreground=TEXT_DARK)
        table.pack(fill="both", expand=True)

        for event in self.events:
            table.insert(
                "",
                "end",
                iid=str(event["id"]),
                values=(
                    event["event_date"] or "",
                    event["event_time"] or "",
                    event["client_name"] or "",
                    event["event_type"] or "",
                    event["package_name"] or "",
                    event["status"] or ""
                ),
                tags=("normal",)
            )

        action_row = tk.Frame(container, bg=SCHEDULE_CARD_BG)
        action_row.pack(fill="x", pady=(12, 0))

        ttk.Button(
            action_row,
            text="View Details",
            command=lambda: self.handle_table_action(table, "view")
        ).pack(side="left")

        ttk.Button(
            action_row,
            text="Reschedule",
            command=lambda: self.handle_table_action(table, "reschedule")
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            action_row,
            text="Cancel Schedule",
            command=lambda: self.handle_table_action(table, "cancel")
        ).pack(side="left", padx=(8, 0))

    def handle_table_action(self, table, action):
        selected = table.selection()

        if not selected:
            messagebox.showwarning("No Selection", "Please select a schedule first.")
            return

        booking_id = int(selected[0])
        event = self.get_event_by_id(booking_id)

        if not event:
            messagebox.showerror("Error", "Schedule record not found.")
            return

        if action == "view":
            self.open_booking_details(event)
        elif action == "reschedule":
            self.open_reschedule_window(event)
        elif action == "cancel":
            self.confirm_cancel_schedule(event)

    # =========================
    # EVENT WIDGETS
    # =========================

    def create_event_chip(self, parent, event):
        status = str(event.get("status", "")).lower()

        if status == "cancelled":
            bg_color = "#efc0c0"
            fg_color = "#7a1f1f"
        else:
            bg_color = SIDEBAR_ACTIVE_BG
            fg_color = ACCENT_OLIVE

        chip = tk.Frame(
            parent,
            bg=bg_color,
            cursor="hand2"
        )
        chip.pack(fill="x", padx=8, pady=4)

        tk.Label(
            chip,
            text=event["event_time"] or "",
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=8, pady=(5, 0))

        tk.Label(
            chip,
            text=event["client_name"] or "Client",
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=8, pady=(0, 5))

        chip.bind(
            "<Button-1>",
            lambda e, event_data=event: self.open_booking_details(event_data)
        )

    def get_event_by_id(self, booking_id):
        for event in self.events:
            if int(event["id"]) == int(booking_id):
                return event

        return None

    # =========================
    # SIDE PANEL
    # =========================

    def render_side_panel(self):
        self.render_upcoming_bookings()
        self.render_mini_calendar()

    def render_upcoming_bookings(self):
        box = self.create_card(self.side_panel)
        box.pack(fill="x", pady=(0, 14))

        tk.Label(
            box,
            text="Upcoming Bookings",
            bg=SCHEDULE_CARD_BG,
            fg=ACCENT_OLIVE,
            font=("Georgia", 13, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 8))

        upcoming = [
            event for event in self.events
            if str(event.get("status", "")).lower() != "cancelled"
        ][:6]

        if not upcoming:
            tk.Label(
                box,
                text="No upcoming bookings in this view.",
                bg=SCHEDULE_CARD_BG,
                fg=TEXT_MUTED,
                font=("Segoe UI", 9)
            ).pack(anchor="w", padx=14, pady=(0, 14))
            return

        for event in upcoming:
            item = tk.Frame(box, bg=SCHEDULE_CARD_BG, cursor="hand2")
            item.pack(fill="x", padx=14, pady=6)

            tk.Label(
                item,
                text=f"{event['event_date']}  •  {event['event_time'] or ''}",
                bg=SCHEDULE_CARD_BG,
                fg=TEXT_MUTED,
                font=("Segoe UI", 8)
            ).pack(anchor="w")

            tk.Label(
                item,
                text=event["client_name"] or "",
                bg=SCHEDULE_CARD_BG,
                fg=TEXT_DARK,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")

            tk.Label(
                item,
                text=event["event_type"] or "",
                bg=SCHEDULE_CARD_BG,
                fg=TEXT_MUTED,
                font=("Segoe UI", 8)
            ).pack(anchor="w")

            item.bind(
                "<Button-1>",
                lambda e, event_data=event: self.open_booking_details(event_data)
            )

    def render_mini_calendar(self):
        box = self.create_card(self.side_panel)
        box.pack(fill="x")

        tk.Label(
            box,
            text="Mini Calendar",
            bg=SCHEDULE_CARD_BG,
            fg=ACCENT_OLIVE,
            font=("Georgia", 13, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 8))

        mini_title = self.current_date.strftime("%B %Y")

        tk.Label(
            box,
            text=mini_title,
            bg=SCHEDULE_CARD_BG,
            fg=TEXT_DARK,
            font=("Georgia", 12, "bold")
        ).pack(pady=(0, 8))

        grid = tk.Frame(box, bg=SCHEDULE_CARD_BG)
        grid.pack(padx=18, pady=(0, 16))

        weekdays = ["S", "M", "T", "W", "T", "F", "S"]

        for col, day_name in enumerate(weekdays):
            tk.Label(
                grid,
                text=day_name,
                bg=SCHEDULE_CARD_BG,
                fg=TEXT_MUTED,
                font=("Segoe UI", 8),
                width=4
            ).grid(row=0, column=col, pady=(0, 5))

        first_day, last_day = self.get_month_start_end()
        first_weekday, days_in_month = calendar.monthrange(first_day.year, first_day.month)
        start_col = (first_weekday + 1) % 7
        grouped = self.get_events_by_date()

        day_number = 1

        for week in range(6):
            for col in range(7):
                if week == 0 and col < start_col:
                    tk.Label(grid, text="", bg=SCHEDULE_CARD_BG, width=4).grid(row=week + 1, column=col)
                    continue

                if day_number > days_in_month:
                    tk.Label(grid, text="", bg=SCHEDULE_CARD_BG, width=4).grid(row=week + 1, column=col)
                    continue

                d = date(first_day.year, first_day.month, day_number)
                date_text = d.strftime("%Y-%m-%d")
                events = grouped.get(date_text, [])

                bg = SCHEDULE_CARD_BG
                fg = TEXT_DARK

                if events:
                    bg = SCHEDULE_BOOKED_BG
                    fg = "#6c2c22"

                if d == self.today:
                    bg = ACCENT_OLIVE
                    fg = "white"

                label = tk.Label(
                    grid,
                    text=str(day_number),
                    bg=bg,
                    fg=fg,
                    font=("Segoe UI", 8, "bold" if events or d == self.today else "normal"),
                    width=4,
                    cursor="hand2"
                )
                label.grid(row=week + 1, column=col, pady=3)

                label.bind(
                    "<Button-1>",
                    lambda e, date_value=date_text: self.open_day_details(date_value)
                )

                day_number += 1

    # =========================
    # ACTIONS
    # =========================

    def open_day_details(self, date_text):
        events = [
            event for event in self.events
            if event["event_date"] == date_text
        ]

        if not events:
            messagebox.showinfo("Schedule", f"No booking scheduled on {date_text}.")
            return

        ScheduleDetailsWindow(
            parent=self,
            schedule_page=self,
            events=events,
            date_text=date_text
        )

    def open_booking_details(self, event):
        ScheduleDetailsWindow(
            parent=self,
            schedule_page=self,
            events=[event],
            date_text=event["event_date"]
        )

    def open_reschedule_window(self, event):
        if str(event.get("status", "")).lower() == "cancelled":
            messagebox.showwarning(
                "Cancelled Schedule",
                "Cancelled schedules cannot be rescheduled."
            )
            return

        RescheduleScheduleWindow(
            parent=self,
            schedule_page=self,
            event=event
        )

    def confirm_cancel_schedule(self, event):
        if str(event.get("status", "")).lower() == "cancelled":
            messagebox.showinfo("Already Cancelled", "This schedule is already cancelled.")
            return

        confirm = messagebox.askyesno(
            "Cancel Schedule",
            "Are you sure you want to cancel this schedule?\n\n"
            f"Client: {event['client_name']}\n"
            f"Date: {event['event_date']}\n"
            f"Time: {event['event_time']}"
        )

        if not confirm:
            return

        try:
            self.cancel_booking_schedule(event["id"])
            messagebox.showinfo("Success", "Schedule cancelled successfully.")
            self.refresh_page()

        except Exception as e:
            messagebox.showerror("Error", f"Unable to cancel schedule: {e}")

class ScheduleDetailsWindow(tk.Toplevel):
    def __init__(self, parent, schedule_page: SchedulePage, events, date_text):
        super().__init__(parent)

        self.schedule_page = schedule_page
        self.events = events
        self.date_text = date_text

        self.title("Schedule Details")
        self.geometry("620x520")
        self.minsize(600, 480)
        self.configure(bg=APP_BG)

        self.build_ui()

    def build_ui(self):
        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text=f"Schedules on {self.date_text}",
            style="Header.TLabel"
        ).pack(anchor="w", pady=(0, 12))

        list_frame = ttk.Frame(container)
        list_frame.pack(fill="both", expand=True)

        for event in self.events:
            self.create_event_detail_card(list_frame, event)

        button_row = ttk.Frame(container)
        button_row.pack(fill="x", pady=(14, 0))

        ttk.Button(
            button_row,
            text="Close",
            command=self.destroy
        ).pack(side="right")

    def create_event_detail_card(self, parent, event):
        card = tk.Frame(
            parent,
            bg="#fffdf7",
            highlightbackground=SCHEDULE_BORDER,
            highlightthickness=1,
            bd=0
        )
        card.pack(fill="x", pady=(0, 12))

        header = tk.Frame(card, bg="#fffdf7")
        header.pack(fill="x", padx=14, pady=(12, 6))

        tk.Label(
            header,
            text=event["client_name"] or "Client",
            bg="#fffdf7",
            fg=TEXT_DARK,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        tk.Label(
            header,
            text=event["status"] or "",
            bg=SIDEBAR_ACTIVE_BG,
            fg=ACCENT_OLIVE,
            font=("Segoe UI", 9),
            padx=8,
            pady=3
        ).pack(side="right")

        details_text = (
            f"Event Type: {event['event_type'] or ''}\n"
            f"Package: {event['package_name'] or ''}\n"
            f"Date: {event['event_date'] or ''}\n"
            f"Time: {event['event_time'] or ''}\n"
            f"Location: {event['event_location'] or ''}\n"
            f"Guest Count: {event['guest_count'] or ''}\n"
            f"Theme / Motif: {event['theme_motif'] or ''}"
        )

        tk.Label(
            card,
            text=details_text,
            bg="#fffdf7",
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
            justify="left",
            anchor="w"
        ).pack(anchor="w", padx=14, pady=(0, 10))

        actions = tk.Frame(card, bg="#fffdf7")
        actions.pack(fill="x", padx=14, pady=(0, 12))

        ttk.Button(
            actions,
            text="Reschedule",
            command=lambda: self.reschedule_event(event)
        ).pack(side="left")

        ttk.Button(
            actions,
            text="Cancel Schedule",
            command=lambda: self.cancel_event(event)
        ).pack(side="left", padx=(8, 0))

    def reschedule_event(self, event):
        self.destroy()
        self.schedule_page.open_reschedule_window(event)

    def cancel_event(self, event):
        self.destroy()
        self.schedule_page.confirm_cancel_schedule(event)



class RescheduleScheduleWindow(tk.Toplevel):
    def __init__(self, parent, schedule_page: SchedulePage, event):
        super().__init__(parent)

        self.schedule_page = schedule_page
        self.event = event

        self.original_date = event["event_date"] or ""
        self.original_time = event["event_time"] or ""

        self.date_var = tk.StringVar(value=self.original_date)
        self.time_var = tk.StringVar(value=self.original_time)

        self.title("Reschedule")
        self.geometry("520x420")
        self.resizable(False, False)
        self.configure(bg=APP_BG)

        self.transient(parent)
        self.grab_set()

        self.build_ui()

    def build_ui(self):
        container = ttk.Frame(self, padding=22)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Reschedule Event",
            style="Header.TLabel"
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(
            container,
            text=f"Client: {self.event['client_name'] or ''}",
            style="Subheader.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            container,
            text=f"Current Schedule: {self.original_date} at {self.original_time}",
            style="Subheader.TLabel"
        ).pack(anchor="w", pady=(2, 18))

        form = ttk.Frame(container)
        form.pack(fill="x")

        ttk.Label(form, text="New Event Date").pack(anchor="w")

        date_row = ttk.Frame(form)
        date_row.pack(fill="x", pady=(4, 14))

        ttk.Entry(
            date_row,
            textvariable=self.date_var,
            state="readonly"
        ).pack(side="left", fill="x", expand=True)

        ttk.Button(
            date_row,
            text="Select Date",
            command=self.select_date
        ).pack(side="left", padx=(8, 0))

        ttk.Label(form, text="New Event Time").pack(anchor="w")

        time_options = [
            "08:00 AM",
            "09:00 AM",
            "10:00 AM",
            "11:00 AM",
            "12:00 PM",
            "01:00 PM",
            "02:00 PM",
            "03:00 PM",
            "04:00 PM",
            "05:00 PM",
            "06:00 PM",
            "07:00 PM"
        ]

        ttk.Combobox(
            form,
            textvariable=self.time_var,
            values=time_options,
            state="readonly"
        ).pack(fill="x", pady=(4, 18))

        #note = (
        #    "Available dates are selectable.\n"
        #    "Unavailable dates are already booked or too close to today.\n"
        #    "The current booked date is highlighted in the calendar."
        #)

        #ttk.Label(
        #   container,
        #    text=note,
        #    style="Subheader.TLabel",
        #    wraplength=460
        #).pack(anchor="w", pady=(0, 16))

        button_row = ttk.Frame(container)
        button_row.pack(fill="x", pady=(10, 0))

        ttk.Button(
            button_row,
            text="Cancel",
            command=self.destroy
        ).pack(side="right")

        ttk.Button(
            button_row,
            text="Confirm Reschedule",
            command=self.confirm_reschedule
        ).pack(side="right", padx=(0, 8))

    def select_date(self):
        RescheduleDatePickerWindow(
            parent=self,
            schedule_page=self.schedule_page,
            target_var=self.date_var,
            booking_id=self.event["id"],
            current_schedule_date=self.original_date,
            initial_date=self.date_var.get()
        )

    def validate_reschedule(self):
        new_date = self.date_var.get().strip()
        new_time = self.time_var.get().strip()

        if not new_date:
            raise ValueError("Please select a new event date.")

        if not new_time:
            raise ValueError("Please select a new event time.")

        try:
            selected_date = datetime.strptime(new_date, "%Y-%m-%d").date()
        except Exception:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

        minimum_date = date.today() + timedelta(days=3)

        if selected_date < minimum_date:
            raise ValueError(
                "You cannot reschedule to this date.\n\n"
                "Schedules must be at least 3 days from today."
            )

        active_count = self.schedule_page.count_active_bookings_on_date(
            new_date,
            exclude_booking_id=self.event["id"]
        )

        if active_count >= MAX_ACTIVE_BOOKINGS_PER_DAY:
            raise ValueError(
                "This date is already booked or unavailable.\n\n"
                "Only one active booking per day is allowed for now."
            )

        return new_date, new_time

    def confirm_reschedule(self):
        try:
            new_date, new_time = self.validate_reschedule()

            if new_date == self.original_date and new_time == self.original_time:
                messagebox.showinfo(
                    "No Changes",
                    "The selected schedule is the same as the current schedule."
                )
                return

            confirm = messagebox.askyesno(
                "Confirm Reschedule",
                "Are you sure you want to reschedule this event?\n\n"
                f"Client: {self.event['client_name'] or ''}\n"
                f"From: {self.original_date} at {self.original_time}\n"
                f"To: {new_date} at {new_time}"
            )

            if not confirm:
                return

            self.schedule_page.update_booking_schedule(
                booking_id=self.event["id"],
                new_date=new_date,
                new_time=new_time
            )

            messagebox.showinfo(
                "Success",
                "Schedule rescheduled successfully."
            )

            self.destroy()

            self.schedule_page.current_date = datetime.strptime(
                new_date,
                "%Y-%m-%d"
            ).date()

            self.schedule_page.refresh_page()

        except ValueError as e:
            messagebox.showerror("Invalid Reschedule", str(e))

        except Exception as e:
            messagebox.showerror("Error", f"Unable to reschedule: {e}")

class RescheduleDatePickerWindow(tk.Toplevel):
    def __init__(
        self,
        parent,
        schedule_page: SchedulePage,
        target_var,
        booking_id,
        current_schedule_date,
        initial_date=None
    ):
        super().__init__(parent)

        self.schedule_page = schedule_page
        self.target_var = target_var
        self.booking_id = booking_id
        self.current_schedule_date = current_schedule_date

        try:
            parsed_initial = datetime.strptime(initial_date, "%Y-%m-%d").date()
        except Exception:
            parsed_initial = date.today()

        self.current_year = parsed_initial.year
        self.current_month = parsed_initial.month
        self.selected_date = target_var.get().strip() or current_schedule_date

        self.title("Select Event Date")
        self.geometry("540x620")
        self.resizable(False, False)
        self.configure(bg=APP_BG)

        self.transient(parent)
        self.grab_set()

        self.month_title_var = tk.StringVar()

        self.build_ui()
        self.render_calendar()

    def build_ui(self):
        container = tk.Frame(
            self,
            bg=APP_BG,
            padx=18,
            pady=18
        )
        container.pack(fill="both", expand=True)

        nav = tk.Frame(container, bg=APP_BG)
        nav.pack(fill="x", pady=(0, 12))

        tk.Button(
            nav,
            text="‹",
            command=self.previous_month,
            bg="#f8f3e8",
            fg=TEXT_DARK,
            activebackground="#efe8d8",
            activeforeground=TEXT_DARK,
            relief="solid",
            bd=1,
            width=6,
            height=2,
            cursor="hand2",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        tk.Label(
            nav,
            textvariable=self.month_title_var,
            bg=APP_BG,
            fg=TEXT_DARK,
            font=("Segoe UI", 16, "bold")
        ).pack(side="left", expand=True)

        tk.Button(
            nav,
            text="›",
            command=self.next_month,
            bg="#f8f3e8",
            fg=TEXT_DARK,
            activebackground="#efe8d8",
            activeforeground=TEXT_DARK,
            relief="solid",
            bd=1,
            width=6,
            height=2,
            cursor="hand2",
            font=("Segoe UI", 10, "bold")
        ).pack(side="right")

        self.calendar_frame = tk.Frame(
            container,
            bg=APP_BG
        )
        self.calendar_frame.pack(fill="both", expand=True, pady=(0, 10))

        legend = tk.Frame(container, bg=APP_BG)
        legend.pack(fill="x", pady=(6, 12))

        self.create_legend_box(legend, "Available", "#fffdf7", TEXT_DARK)
        self.create_legend_box(legend, "Unavailable", "#f6d2d8", "#b13b49")
        self.create_legend_box(legend, "Current", "#d9c47f", "white")
        self.create_legend_box(legend, "Selected", ACCENT_OLIVE, "white")

        button_row = tk.Frame(container, bg=APP_BG)
        button_row.pack(fill="x")

        tk.Button(
            button_row,
            text="Cancel",
            command=self.destroy,
            bg="#f8f3e8",
            fg=TEXT_DARK,
            activebackground="#efe8d8",
            activeforeground=TEXT_DARK,
            relief="solid",
            bd=1,
            width=14,
            height=2,
            cursor="hand2",
            font=("Segoe UI", 10, "bold")
        ).pack(side="right")

        tk.Button(
            button_row,
            text="Confirm Date",
            command=self.confirm_date,
            bg=ACCENT_OLIVE,
            fg="white",
            activebackground="#555f34",
            activeforeground="white",
            relief="flat",
            bd=0,
            width=16,
            height=2,
            cursor="hand2",
            font=("Segoe UI", 10, "bold")
        ).pack(side="right", padx=(0, 10))

    def create_legend_box(self, parent, text, bg_color, fg_color):
        item = tk.Frame(parent, bg=APP_BG)
        item.pack(side="left", padx=(0, 10))

        sample = tk.Label(
            item,
            text="",
            bg=bg_color,
            relief="solid",
            bd=1,
            width=3,
            height=1
        )
        sample.pack(side="left")

        tk.Label(
            item,
            text=text,
            bg=APP_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 8)
        ).pack(side="left", padx=(4, 0))

    def previous_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1

        self.render_calendar()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1

        self.render_calendar()

    def clear_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

    def render_calendar(self):
        self.clear_calendar()

        self.month_title_var.set(
            f"{calendar.month_name[self.current_month]} {self.current_year}"
        )

        booked_dates = self.schedule_page.get_booked_dates_for_month(
            self.current_year,
            self.current_month,
            exclude_booking_id=self.booking_id
        )

        weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        for col, day_name in enumerate(weekdays):
            tk.Label(
                self.calendar_frame,
                text=day_name,
                bg=APP_BG,
                fg=TEXT_DARK,
                font=("Segoe UI", 10, "bold")
            ).grid(row=0, column=col, sticky="nsew", pady=(0, 8))

        for col in range(7):
            self.calendar_frame.grid_columnconfigure(col, weight=1, uniform="calendar_col")

        for row in range(1, 7):
            self.calendar_frame.grid_rowconfigure(row, weight=1, uniform="calendar_row")

        first_weekday, days_in_month = calendar.monthrange(
            self.current_year,
            self.current_month
        )

        start_col = (first_weekday + 1) % 7
        day_number = 1

        for week in range(6):
            for col in range(7):
                if week == 0 and col < start_col:
                    spacer = tk.Frame(self.calendar_frame, bg=APP_BG)
                    spacer.grid(row=week + 1, column=col, padx=3, pady=3, sticky="nsew")
                    continue

                if day_number > days_in_month:
                    spacer = tk.Frame(self.calendar_frame, bg=APP_BG)
                    spacer.grid(row=week + 1, column=col, padx=3, pady=3, sticky="nsew")
                    continue

                current_day = date(
                    self.current_year,
                    self.current_month,
                    day_number
                )

                date_text = current_day.strftime("%Y-%m-%d")

                self.create_date_button(
                    row=week + 1,
                    col=col,
                    current_day=current_day,
                    date_text=date_text,
                    booked_dates=booked_dates
                )

                day_number += 1

    def create_date_button(self, row, col, current_day, date_text, booked_dates):
        minimum_date = date.today() + timedelta(days=3)

        is_current_schedule = date_text == self.current_schedule_date
        is_selected = date_text == self.selected_date
        is_too_soon = current_day < minimum_date
        is_booked = booked_dates.get(date_text, 0) >= MAX_ACTIVE_BOOKINGS_PER_DAY

        is_unavailable = is_too_soon or is_booked

        bg_color = "#fffdf7"
        fg_color = TEXT_DARK
        border_color = "#2f2b1f"
        clickable = True

        if is_unavailable:
            bg_color = "#f6d2d8"
            fg_color = "#b13b49"
            border_color = "#2f2b1f"
            clickable = False

        if is_current_schedule:
            bg_color = "#d9c47f"
            fg_color = "white"
            border_color = ACCENT_OLIVE
            clickable = True

        if is_selected:
            bg_color = ACCENT_OLIVE
            fg_color = "white"
            border_color = ACCENT_OLIVE
            clickable = True

        button = tk.Button(
            self.calendar_frame,
            text=str(current_day.day),
            bg=bg_color,
            fg=fg_color,
            activebackground=bg_color,
            activeforeground=fg_color,
            relief="solid",
            bd=1,
            highlightbackground=border_color,
            highlightcolor=border_color,
            highlightthickness=1,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2" if clickable else "arrow",
            command=lambda value=date_text: self.select_date(value) if clickable else None
        )

        button.grid(
            row=row,
            column=col,
            padx=3,
            pady=3,
            sticky="nsew"
        )

    def select_date(self, date_text):
        self.selected_date = date_text
        self.render_calendar()

    def confirm_date(self):
        if not self.selected_date:
            messagebox.showwarning(
                "No Date Selected",
                "Please select an available date."
            )
            return

        try:
            selected = datetime.strptime(self.selected_date, "%Y-%m-%d").date()
        except Exception:
            messagebox.showerror("Invalid Date", "Invalid selected date.")
            return

        minimum_date = date.today() + timedelta(days=3)

        if selected < minimum_date:
            messagebox.showerror(
                "Unavailable Date",
                "This date is unavailable.\n\n"
                "Schedules must be at least 3 days from today."
            )
            return

        active_count = self.schedule_page.count_active_bookings_on_date(
            self.selected_date,
            exclude_booking_id=self.booking_id
        )

        if active_count >= MAX_ACTIVE_BOOKINGS_PER_DAY:
            messagebox.showerror(
                "Unavailable Date",
                "This date is already booked.\n\n"
                "Please select another available date."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Date Selection",
            f"Use this date for rescheduling?\n\nSelected Date: {self.selected_date}"
        )

        if not confirm:
            return

        self.target_var.set(self.selected_date)
        self.destroy()


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