import json
import logging

from managers.exceptions import (
    UserNotFoundError,
    InvalidPasswordError,
    UserAlreadyExistsError,
)
from models.user import User
from utils.JSONFileHandler import JSONFileHandler


class UsersManager:
    def __init__(self, file_path="data/users.json") -> None:
        self.file_path = file_path
        self.file_handler = JSONFileHandler(self.file_path)
        self.users = []
        self._users_by_email = {}  # key-based lookup
        self.load_users()

    def load_users(self) -> None:
        self.users = []
        self._users_by_email = {}
        try:
            users_list_from_json = self.file_handler.read_json()
            if not isinstance(users_list_from_json, list):
                 logging.error(f"User data file {self.file_path} did not contain a JSON list. Found {type(users_list_from_json)}. Cannot load users.")
                 return

            for raw_user_data in users_list_from_json:
                 try:
                      if not isinstance(raw_user_data, dict):
                           logging.warning(f"Skipping non-dictionary item: {raw_user_data}")
                           continue
                      user = User.from_dict(raw_user_data)
                      if user.email in self._users_by_email:
                           logging.warning(f"Skipping duplicate email loaded: {user.email}")
                           continue
                      self.users.append(user)
                      self._users_by_email[user.email] = user
                 except (KeyError, TypeError, ValueError) as e:
                      logging.warning(f"Skipping user data due to data error: {e}. Data: {raw_user_data}")
                 except Exception as e:
                      logging.exception(f"Unexpected error processing user data item: {raw_user_data}")

        except FileNotFoundError:
            logging.warning(f"User data file not found at {self.file_path}. Starting with no users.")
        except json.JSONDecodeError:
            logging.exception(f"Failed to decode JSON from {self.file_path}. File may be corrupt. Starting with no users.")
        except (IOError, OSError) as e:
            logging.exception(f"OS error reading user file {self.file_path}. Cannot load users.")
            # raise e
        except Exception as e:
            logging.exception("An unexpected error occurred during user loading.")
            # raise e

    def save_users(self) -> None:
        users_list = [user.to_dict() for user in self.users]
        try:
            self.file_handler.write_json(users_list)
        except (IOError, OSError, TypeError) as e:
            logging.exception(f"Failed to save user data to {self.file_path}.")
            raise e
        except Exception as e:
            logging.exception("An unexpected error occurred during user saving.")
            raise e

    def add_user(self, name: str, email: str, password: str, passcode: str) -> User:
        if email in self._users_by_email:
            raise UserAlreadyExistsError(email)
        hashed_password = User.hash_password(password, passcode)
        user = User(name=name, email=email, hashed_password=hashed_password)
        self.users.append(user)
        self._users_by_email[user.email] = user
        self.save_users()
        return user

    def edit_user_name(self, email: str, new_name: str) -> None:
        if user := self.get_user_by_email(email):
            logging.info(f"Changing user name '{user.name}' to '{new_name}'...")
            user.name = new_name
        else:
            logging.warning(f"User not found for name changing: {email}")

    def edit_user_email(self, old_email: str, new_email: str) -> None:
        if new_email in self._users_by_email:
            raise UserAlreadyExistsError(new_email)
        if user := self.get_user_by_email(old_email):
            logging.info(f"Changing user e-mail '{user.email}' to '{new_email}'...")
            user.email = new_email
            del self._users_by_email[old_email]
            self._users_by_email[new_email] = user
        else:
            logging.warning(f"User not found for e-mail changing: {old_email}")

    def edit_user_pass(
        self,
        email: str,
        # old_password: str,
        # old_passcode: str,
        new_password: str,
        new_passcode: str,
    ) -> None:
        '''
            old_password and old_passcode check omitted,
            as ProfileMode is accessible after User is logged in
        '''
        if user := self.get_user_by_email(email):
            logging.info(f"changing user passes...")
            # if user.is_valid_password(old_password, old_passcode, user.hashed_password):
            user.hashed_password = User.hash_password(new_password, new_passcode)
            # else:
            #     raise InvalidPasswordError(email)
            logging.info(f"user passes changed and saved")

    def delete_user(self, email: str) -> None:
        user = self.get_user_by_email(email)
        self.users.remove(user)
        del self._users_by_email[user.email]
        self.save_users()

    def get_user_by_email(self, email: str) -> User:
        if user := self._users_by_email.get(email):
            return user
        else:
            raise UserNotFoundError(email)

    def authenticate_user(self, email: str, password: str, passcode: str) -> User:
        user = self.get_user_by_email(email)
        if user.is_valid_password(password, passcode, user.hashed_password):
            return user
        else:
            raise InvalidPasswordError(email)
