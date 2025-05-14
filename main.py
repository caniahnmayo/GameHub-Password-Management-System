import tkinter as tk
from tkinter.simpledialog import askstring
from snake_game import snake_game
from gui_utilities import *

def after_login_menu(root):

    def logout():

        messagebox.showinfo("Logout", "Logged out successfully.")
        root.deiconify()
        after_login.destroy()

    def play_viper():

        root.withdraw()
        snake_game()

    root.withdraw()
    after_login = tk.Toplevel(root)
    icon(after_login, tk)
    window_size(after_login)
    after_login.title("Game HUB Menu")
    tk.Label(after_login, text="Menu", font=("Arial", 50)).pack(pady = 10)
    tk.Button(after_login, text="Play VIPER", command=play_viper, width = 50).pack(pady = 10)
    tk.Button(after_login, text="Logout", command=logout, width = 50).pack(pady = 10)

def login_menu(root, login_attempts):
    root.withdraw()
    login_window = tk.Toplevel(root)
    icon(login_window, tk)
    window_size(login_window)
    login_window.title("Login Menu")
    tk.Label(login_window, text="Login Menu", font=("Arial", 50)).pack(pady = 10)

    id_entry = enter_id(login_window, tk)
    password_entry = enter_password(login_window, tk, "Enter password here")

    toggle_button(login_window, password_entry, tk)

    def back():
        root.deiconify()
        login_window.destroy()

    def handle_login():

        username = id_entry.get()
        if not username or len(username) < MIN_ID_LENGTH or len(username) > MAX_ID_LENGTH or not check_user_exists(username):
            error("Invalid User ID")
            return

        password = password_entry.get()
        if not password:
            error("Invalid password")
            return

        if verify_user(username, password):
            current_time = datetime.now()
            verification_code, verification_code_time = generate_verification_code()
            email = get_user_email(username,"", 1)
            email_sent = send_verification_email(email, verification_code, "login")
            if email_sent:
                user_input_code = askstring("Forgot Password", f"Enter the verification code sent to your email. Code expires at {verification_code_time+timedelta(seconds=CODE_EXPIRATION)}.")
                if not user_input_code or user_input_code != verification_code:
                    error("Invalid verification code")
                    return
                if (current_time - verification_code_time).total_seconds() > CODE_EXPIRATION:
                    error("Verification Code expired")
                    return
            else:
                error("Unable to send verification code at this time.")
                return

            login_attempt(username, False, login_attempts)
            after_login_menu(root)
            login_window.destroy()
            return
        else:
            error("Invalid login, please try again.")
            login_attempt(username, True, login_attempts)

    def handle_forgot_password():
        email = askstring("Forgot Password", "Enter the email associated with your account:")
        messagebox.showinfo("Forgot Password", f"If the account associated with that email exists, a verification code will be sent to you.")

        if get_user_email("", email, 2) == email:
            current_time = datetime.now()
            verification_code, verification_code_time = generate_verification_code()
            email_sent = send_verification_email(email, verification_code, "forgot password")
            if email_sent:
                user_input_code = askstring("Forgot Password", f"Enter the verification code sent to your email. Code expires at {verification_code_time+timedelta(seconds=CODE_EXPIRATION)}.")
                if not user_input_code or user_input_code != verification_code:
                    error("Invalid verification code")
                    return
                if (current_time - verification_code_time).total_seconds() > CODE_EXPIRATION:
                    error("Verification Code expired")
                    return

                password_requirements()

                password_reset_menu = tk.Toplevel(login_window)
                password_reset_menu.title("Reset Password")
                icon(password_reset_menu, tk)
                tk.Label(password_reset_menu, text="Reset Password", font=("Arial", 30)).pack(pady=10)

                reset_password_entry = enter_password(password_reset_menu, tk, "Enter password here")
                password_verify = enter_password(password_reset_menu, tk, "Re-enter your password")

                toggle_button(password_reset_menu, reset_password_entry, tk)
                strength_label, feedback_label, canvas, dot = display_password_strength(password_reset_menu, tk)

                password_entry.bind("<KeyRelease>",
                                    lambda event: update_strength(reset_password_entry, strength_label, feedback_label, canvas,
                                                                  dot))

                def handle_reset_password():

                    password = reset_password_entry.get()

                    if not password or len(password) < MIN_PASSWORD_LENGTH or not check_password_characters(
                            password) or password != password_verify.get() or verify_user(get_username(email), password) == True:
                        error("Invalid password."
                               "\nMust be a minimum of 10 characters"
                               "\nMust include at least 1 upper case letter"
                               "\nMust include at least 1 lower case letter"
                               "\nMust include at least 1 number"
                               "\nMust include at least 1 special character"
                               "\nPassword cannot be the same as previous password\n")
                        return

                    username = get_username(email)
                    password = password_entry.get()
                    remove_user(username)
                    create_user(username, password)
                    store_user_email(username, email)

                    messagebox.showinfo("Success", "Password updated successfully!")
                    password_reset_menu.destroy()

                tk.Button(password_reset_menu, text="Reset Password", command=handle_reset_password, width=50).pack(pady=10)

            else:
                error("Unable to send verification code at this time.")
                return

    tk.Button(login_window, text="Login", command=handle_login, width = 50).pack(pady = 10)
    tk.Button(login_window, text="Forgot Password", command=handle_forgot_password, width = 50).pack(pady = 10)
    tk.Button(login_window, text="Back", command=back, width = 50).pack(pady = 10)

def create_account_menu(root):

    root.withdraw()
    create_window = tk.Toplevel(root)
    icon(create_window, tk)
    window_size(create_window)
    create_window.title("Create Account Menu")
    tk.Label(create_window, text="Create Account", font=("Arial", 40)).pack(pady = 10)

    password_requirements()

    email_entry = tk.Entry(create_window, width=50, justify="center", show="")
    email_entry.pack(pady=10)
    email_entry.insert(0, "Enter your email here")

    id_entry = enter_id(create_window, tk)
    password_entry = enter_password(create_window, tk, "Enter your password here")
    password_verify = enter_password(create_window, tk, "Re-enter your password here")

    toggle_button(create_window, password_entry, tk)
    strength_label, feedback_label, canvas, dot = display_password_strength(create_window, tk)

    password_entry.bind("<KeyRelease>", lambda event: update_strength(password_entry, strength_label, feedback_label, canvas, dot))

    def handle_create_account():

        email = email_entry.get()
        if not email or not is_valid_email(email):
            error("Invalid email")
            return

        username = id_entry.get()
        if not username or len(username) < MIN_ID_LENGTH or len(username) > MAX_ID_LENGTH or check_user_exists(username):
            error("Invalid or already existing User ID.")
            return

        valid = False

        current_time = datetime.now()
        verification_code, verification_code_time = generate_verification_code()
        email_sent = send_verification_email(email, verification_code, "sign-up")
        if email_sent:
            user_input_code = askstring("Forgot Password",
                                        f"Enter the verification code sent to your email. Code expires at {verification_code_time + timedelta(seconds=CODE_EXPIRATION)}.")
            if not user_input_code or user_input_code != verification_code:
                error("Invalid verification code")
                return
            if (current_time - verification_code_time).total_seconds() > CODE_EXPIRATION:
                error("Verification Code expired")
                return
            else:
                valid = True
        else:
            error("Unable to send verification code at this time.")
            return

        password = password_entry.get()
        if not password or len(password) < MIN_PASSWORD_LENGTH or not check_password_characters(password) or password != password_verify.get():
            error("Invalid password."
                    "\nMust be a minimum of 10 characters"
                    "\nMust include at least 1 upper case letter"
                    "\nMust include at least 1 lower case letter"
                    "\nMust include at least 1 number"
                    "\nMust include at least 1 special character\n")

        if valid:

            username = id_entry.get()
            email = email_entry.get()
            password = password_entry.get()
            create_user(username, password)
            store_user_email(username, email)  # Store email with user details
            success("Account created successfully!")
            create_window.destroy()
            root.deiconify()

    def back():
        root.deiconify()
        create_window.destroy()

    tk.Button(create_window, text="Create Account", command=handle_create_account, width = 50).pack(pady = 10)
    tk.Button(create_window, text="Back", command = back, width = 50).pack(pady = 10)


def main_menu():
    root = tk.Tk()
    icon(root, tk)
    window_size(root)
    root.title("Game HUB")
    tk.Label(root, text="Game HUB", font=("Arial", 50)).pack(pady=10)
    login_attempts = {}

    tk.Button(root, text="Login", command=lambda: login_menu(root, login_attempts), width = 50).pack(pady = 10)
    tk.Button(root, text="Create Account", command=lambda: create_account_menu(root), width = 50).pack(pady = 10)
    tk.Button(root, text="Exit", command=root.quit, width = 50).pack(pady = 10)

    root.mainloop()

main_menu()
