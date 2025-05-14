from tkinter import messagebox
from password_system import *
import smtplib
import re

def is_valid_email(email):

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6)), datetime.now()

def send_verification_email(user_email, verification_code, purpose):

    try:

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("cm7943@engr.ship.edu", "bbca hmlj xxnc mjyx")

        subject = f"{purpose.capitalize()} Game HUB Verification Code"
        body = (f"Your {purpose} verification code is: {verification_code}.\n\nDo not share your verification code. "
                f"\nWe will not call or ask for this code outside of the application.")
        message = f"Subject: {subject}\n\n{body}"

        server.sendmail("your_email@gmail.com", user_email, message)
        server.quit()
        return True
    except Exception as e:
        messagebox.showerror("Email Error", f"Failed to send email: {e}")
        return False

def send_lockout_email(user_email, lockout_end):

    try:

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("cm7943@engr.ship.edu", "bbca hmlj xxnc mjyx")

        subject = f"Game HUB Account Lockout"
        body = (f"Your account has been locked due to too many sign-in attempts."
                f"\nIf this was not you, please open the application and reset your password."
                f"\nYour account will unlock at {lockout_end}")
        message = f"Subject: {subject}\n\n{body}"

        server.sendmail("your_email@gmail.com", user_email, message)
        server.quit()
        return True

    except Exception as e:
        messagebox.showerror("Email Error", f"Failed to send email: {e}")
        return False

def error(message):
    messagebox.showerror("Error!", message)

def success(message):
    messagebox.showinfo("Success!", message)

def password_requirements():
    messagebox.showinfo("Password Requirements", "Must be a minimum of 10 characters"
                                                 "\nMust include at least 1 upper case letter"
                                                 "\nMust include at least 1 lower case letter"
                                                 "\nMust include at least 1 number"
                                                 "\nMust include at least 1 special character\n")


def login_attempt(username, failed, login_attempts):
    attempts, lockout, lockout_until = track_lockout(username, failed, login_attempts)

    if lockout and attempts >= LOCKOUT_THRESHOLD:
        error(f"Too many login attempts. User locked out until {lockout_until}.")
    if attempts == LOCKOUT_THRESHOLD:
        send_lockout_email(get_user_email(username, "", 1), lockout_until)
        error(f"Too many login attempts. User locked out until {lockout_until}.")

def display_password_strength(root, tk):

    strength_frame = tk.Frame(root)
    strength_frame.pack(pady=5)
    canvas = tk.Canvas(strength_frame, width=20, height=20, highlightthickness=0)
    canvas.grid(row=0, column=0, padx=5)
    dot = canvas.create_oval(5, 5, 15, 15, fill="red")  # Default color
    strength_label = tk.Label(strength_frame, text="Strength: Very Weak", font=("Arial", 10))
    strength_label.grid(row=0, column=1)

    feedback_label = tk.Label(root, text="", font=("Arial", 10), justify="left", wraplength=350)
    feedback_label.pack(pady=5)

    return strength_label, feedback_label, canvas, dot

def update_strength(password_entry, strength_label, feedback_label, canvas, dot):
    password = password_entry.get()
    feedback, score = check_password_strength(password)

    strength_label.config(
    text=f"Strength: {'Very Strong' if score == 4 else 'Strong' if score == 3 else 'Ok' if score == 2 else 'Weak' if score == 1 else 'Very Weak'}")

    feedback_label.config(text=feedback)

    color = "green" if score >= 3 else "yellow" if score == 2 else "red"
    canvas.itemconfig(dot, fill=color)

def enter_id(root, tk):
    id_entry = tk.Entry(root, width=50, justify="center", show="")
    id_entry.pack(pady=10)
    id_entry.insert(0, "Enter your username here")
    return id_entry

def enter_password(root, tk, message):
    password_entry = tk.Entry(root, width=50, justify="center", show="*")
    password_entry.insert(0, message)
    password_entry.pack(pady=10)
    return password_entry

def toggle_password_visibility(password_entry, button):

    current_visibility = password_entry.cget('show') == ''
    password_entry.config(show='' if not current_visibility else '*')

    button.config(text="Hide Password" if not current_visibility else "Show Password")


def toggle_button(root, password_entry, tk):
    button = tk.Button(root, text="Show Password", command=lambda: toggle_password_visibility(password_entry, button), width=20)
    button.pack(pady=10)
    return button

def password_visibility(root, show):
    if show:
        root.config(show="")
    else:
        root.config(show="*")


def center_window(window, width=400, height=300):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def icon(root, tk):
    ico = tk.PhotoImage(file='game_hub_icon.png')
    root.wm_iconphoto(False, ico)
    pass


def window_size(root):
    root.geometry("720x480")