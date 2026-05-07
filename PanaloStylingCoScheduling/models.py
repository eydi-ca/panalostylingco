from dataclasses import dataclass


APP_NAME = "PanaloStylingCo Scheduling System"

APP_MODULES = [
    "Dashboard",
    "Clients",
    "Bookings",
    "Packages",
    "Schedule",
    "Payment",
    "Reports",
    "User Management",
    "Settings",
]


ROLE_PERMISSIONS = {
    "ADMIN": set(APP_MODULES),
    "STAFF": {
        "Dashboard",
        "Clients",
        "Bookings",
        "Packages",
        "Schedule",
    },
}


@dataclass
class SessionUser:
    id: int
    full_name: str
    username: str
    role: str