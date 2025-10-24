import re
from tkinter import messagebox
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")  # simples e suficiente para exercício

def is_valid_email(email: str) -> bool:
    if not email:
        return True  # opcional
    return bool(EMAIL_RE.match(email))

def is_valid_phone(phone: str) -> bool:
    if not phone:
        return True  # opcional
    digits = re.sub(r"\D", "", phone)
    return 8 <= len(digits) <= 15

def show_info(title, msg):
    messagebox.showinfo(title, msg)

def show_error(title, msg):
    messagebox.showerror(title, msg)

def show_confirm(title, msg) -> bool:
    return messagebox.askyesno(title, msg)
