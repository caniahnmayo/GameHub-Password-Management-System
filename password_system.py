from datetime import datetime, timedelta
import os
import hashlib
import random
import string
import logging

MAX_ID_LENGTH = 1000
MAX_PASSWORD_LENGTH = 256
MIN_PASSWORD_LENGTH = 8
MIN_ID_LENGTH = 6

FILE_NAME = "psswrd.txt"
USER_FILE_NAME = "users.txt"
LOGIN_LOG_FILE_NAME = "login.log"
LOCKOUT_FILE = "lockout.txt"

LOCKOUT_THRESHOLD = 5
LOCKOUT_TIME = 300
COOLDOWN_TIME = 120

CODE_EXPIRATION = 60

logging.basicConfig(filename= LOGIN_LOG_FILE_NAME, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def record_attempts(username, lockout_until, last_failed_time, attempts):
    with open(LOCKOUT_FILE, 'r') as lockout:
        lines = lockout.readlines()

    with open(LOCKOUT_FILE, 'w') as lockout:
        for line in lines:
            parts = line.strip().split(' | ')
            if len(parts) == 4 and parts[0] == username:
                lockout.write(line)

    with open("lockout.txt", "a") as lockout:
        if lockout_until is None:
            lockout.write(f"\n {username}  |  {attempts}  |  {last_failed_time.timestamp()} |  None")
        else:
            lockout.write(f"\n {username}  |  {attempts}  |  {last_failed_time.timestamp()}  |  {lockout_until.timestamp()}")

def track_lockout(username, failed, login_attempts):
    current_time = datetime.now()

    if username not in login_attempts:
        login_attempts[username] = {"attempts": 0, "last_failed_time": None, "lockout_until": None}

    user_data = login_attempts[username]

    if user_data["lockout_until"] and current_time < user_data["lockout_until"]:
        time_remaining = (user_data["lockout_until"] - current_time).total_seconds()
        logging.warning(f"Account locked for {username}. Time remaining: {time_remaining:.0f} seconds.")
        return user_data["attempts"], True, user_data["lockout_until"]

    if user_data["last_failed_time"] and (current_time - user_data["last_failed_time"]).total_seconds() > COOLDOWN_TIME:
        user_data["attempts"] = 0
        logging.info(f"Login attempts for {username} reset.")

    if failed:
        user_data["attempts"] += 1
        user_data["last_failed_time"] = datetime.now()
        logging.warning(f"Failed {user_data["attempts"]} login attempt(s) for {username}")
        record_attempts(username, user_data["lockout_until"], user_data["last_failed_time"], user_data["attempts"])

    if user_data["attempts"] >= LOCKOUT_THRESHOLD:
        user_data["lockout_until"] = datetime.now() + timedelta(seconds=LOCKOUT_THRESHOLD)
        logging.error(f"Account locked for {username} due to too many failed login attempts.")
        return user_data["attempts"], True, user_data["lockout_until"]

    if not failed:
        return  user_data["attempts"], False, user_data["lockout_until"]
    elif user_data["attempts"] > 0:
        return user_data["attempts"], True, user_data["lockout_until"]


def check_password_strength(password):

    if len(password) < 8:
        score = 0
        feedback = "Password is too short, must be at least 8 characters."
    elif len(password) < 12:
        score = 2
        feedback = "Password needs to be longer and include a mix of characters."
    elif not any(c.isdigit() for c in password):
        score = 2
        feedback = "Password should include at least one number."
    elif not any(c.islower() for c in password):
        score = 2
        feedback = "Password should include at least one lowercase letter."
    elif not any(c.isupper() for c in password):
        score = 2
        feedback = "Password should include at least one uppercase letter."
    elif not any(c in '!@#$%^&*()_+=-[]{}|;:,.<>?/~`' for c in password):
        score = 2
        feedback = "Password should include at least one special character."
    else:
        score = 3
        feedback = "Great password!"

    return feedback, score

def check_password_characters(password):
    special_char_count = sum(1 for c in password if c in string.punctuation)
    number_count = sum(1 for c in password if c.isdigit())
    upper_count = sum(1 for c in password if c.isupper())
    lower_count = sum(1 for c in password if c.islower())
    return special_char_count > 0 and number_count > 0 and upper_count > 0 and lower_count > 0

def get_hash(password, salt):
    combined = password + salt
    return hashlib.sha256(combined.encode()).hexdigest()

def get_salt_val():
    current_time = datetime.now().strftime("%H%M%S")
    random_digits = ''.join(random.choices(string.digits, k=34))
    return current_time + random_digits

def get_file_str(username, salt, password_hash):
    return f"{username} | {salt} | {password_hash}\n"

def append_to_file(line):
    with open(FILE_NAME, "a") as file:
        file.write(line)

def get_user_info(username):
    if not os.path.exists(FILE_NAME):
        return None
    with open(FILE_NAME, "r") as file:
        for line in file:
            parts = line.strip().split(" | ")
            if len(parts) == 3 and parts[0] == username:
                return parts
    return None

def get_username(user_email):

    with open(USER_FILE_NAME, "r") as file:
        for line in file:
            parts = line.strip().split(" | ")
            if len(parts) == 2 and parts[1] == user_email:
                return parts[0]

def get_user_email(username, user_email, authentication_type):
    if not os.path.exists(USER_FILE_NAME):
        return None

    with open(USER_FILE_NAME, "r") as file:

        if authentication_type == 1:
            for line in file:
                parts = line.strip().split(" | ")
                if len(parts) == 2 and parts[0] == username:
                    return parts[1]

        elif authentication_type == 2:
            for line in file:
                parts = line.strip().split(" | ")
                if len(parts) == 2 and parts[1] == user_email:
                    return parts[1]

    return None

def check_user_exists(username):
    return get_user_info(username) is not None

def store_user_email(username, email):
    with open(USER_FILE_NAME, "a") as file:
        file.write(f"{username} | {email}\n")

def create_user(username, password):
    salt = get_salt_val()
    password_hash = get_hash(password, salt)
    file_str = get_file_str(username, salt, password_hash)
    append_to_file(file_str)

def verify_user(username, password):
    user_info = get_user_info(username)
    if user_info:
        stored_salt = user_info[1]
        stored_hash = user_info[2]
        password_hash = get_hash(password, stored_salt)
        return password_hash == stored_hash
    return False

def remove_user(username):

    with open(USER_FILE_NAME, "r") as file:
        lines = file.readlines()

    with open(USER_FILE_NAME, "w") as file:
        for line in lines:
            parts = line.strip().split(" | ")
            if len(parts) == 2 and parts[0] != username:
                file.write(line)

    with open(FILE_NAME, "r") as file:
        lines = file.readlines()

    with open(FILE_NAME, "w") as file:
        for line in lines:
            parts = line.strip().split(" | ")
            if len(parts) == 3 and parts[0] != username:
                file.write(line)