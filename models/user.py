import base64
import bcrypt
from dataclasses import dataclass, field
import logging
import re
import uuid


@dataclass
class User:
    id: uuid.UUID = field(default_factory=lambda: uuid.uuid4())
    name: str = None
    email: str = None
    hashed_password: bytes = None
    chat_history: list[tuple[str, str]] = field(default_factory=list)

    def __post_init__(self):
        self.validate()

    def __str__(self):
        return (
            f"User is:\n"
            f"- id: {self.id}\n"
            f"- name: {self.name}\n"
            f"- email: {self.email}\n"
            f"- hashed password: {self.hashed_password}"
        )

    def validate(self) -> bool:
        if not isinstance(self.id, uuid.UUID):
            raise ValueError(
                f"Invalid user id '{self.id}' "
                f"({type(self.id).__name__}) - "
                f"must be UUID"
            )

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError(
                f"Invalid user name '{self.name}' "
                f"({type(self.name).__name__}) - "
                f"must be non-empty string"
            )

        if not isinstance(self.email, str) or not User.is_valid_email(self.email):
            raise ValueError(
                f"Invalid email '{self.email}' "
                f"({type(self.email).__name__}) - "
                f"does not match RegEx"
            )

        if not isinstance(self.hashed_password, bytes):
            raise ValueError(
                f"Invalid hashed '{self.hashed_password}' "
                f"({type(self.hashed_password).__name__}) - "
                f"must be bytes"
            )

        if not isinstance(self.chat_history, list):
            raise ValueError(
                f"Invalid history '{self.chat_history}' "
                f"({type(self.chat_history).__name__}) - "
                f"must be list"
            )
        for item in self.chat_history:
            if not (isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str) and isinstance(item[1], str)):
                raise ValueError(
                f"Invalid history item '{item}' "
                f"({type(item).__name__}) - "
                f"must be (str, str) tuples"
            )

        return True

    @staticmethod
    def is_valid_email(email: str) -> bool:
        if not email:
            return False
        pattern = (
            r"^[a-zA-Z0-9](?!.*\.\.)[a-zA-Z0-9._%+-]{0,28}[a-zA-Z0-9]"
            r"@"
            r"[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$"
        )
        return bool(re.fullmatch(pattern, email))

    @staticmethod
    def is_valid_password(password: str, passcode: str, hashed: bytes) -> bool:

        combined = User.combine_pass(password, passcode)
        return bcrypt.checkpw(combined, hashed)

    @staticmethod
    def hash_password(password: str, passcode: str) -> bytes:
        combined = User.combine_pass(password, passcode)
        return bcrypt.hashpw(combined, bcrypt.gensalt())

    @staticmethod
    def combine_pass(password: str, passcode: str) -> bytes:
        if (
            password
            and isinstance(password, str)
            and passcode
            and isinstance(passcode, str)
        ):
            return f"{password}:{passcode}".encode()
        else:
            raise ValueError(
                f"Invalid password '{password}' "
                f"({type(password).__name__}) or "
                f"passcode '{passcode}' "
                f"({type(passcode).__name__}) - "
                f"must be non empty strings"
            )

    @staticmethod
    def from_dict(data: dict) -> "User":
        hashed_bytes = None
        hashed_str = data.get("hashed_password")
        if hashed_str:
            try:
                base64_bytes = hashed_str.encode("ascii")
                hashed_bytes = base64.b64decode(base64_bytes)
            except (TypeError, base64.binascii.Error, ValueError) as e:
                logging.warning(
                    f"Could not decode hashed password for data id {data.get('id', 'N/A')}. Error: {e}"
                )
                raise

        user_id_str = data.get("id")
        user_id = None
        if user_id_str:
            try:
                user_id = uuid.UUID(user_id_str)
            except ValueError:
                logging.error(f"Invalid UUID format in stored data: {user_id_str}")
                raise ValueError(f"Invalid UUID format in stored data: {user_id_str}") from None

        loaded_history = data.get("chat_history", "MISSING") # Use default marker

        if loaded_history == "MISSING" or not isinstance(loaded_history, list):
            logging.warning(f"Invalid/missing chat_history format for user {data.get('id')}, resetting.")
            loaded_history = []  # Optionaly exit
        else:
            loaded_history = [tuple(item) if isinstance(item, list) and len(item) == 2 else item for item in loaded_history]
            if not all(isinstance(item, tuple) and len(item) == 2 for item in loaded_history):
                logging.warning(f"Invalid item structure in chat_history for user {data.get('id')}, resetting.")
                loaded_history = []  # Optionaly exit

        name = data.get("name")
        email = data.get("email")
        try:
            user_instance = User(
                id=user_id,
                name=name,
                email=email,
                hashed_password=hashed_bytes,
                chat_history=loaded_history,
            )
            return user_instance
        
        except ValueError as e:
            logging.warning(f"Error creating User object from dict (validation failed) - Data: {data}. Error: {e}")
            raise

    def to_dict(self) -> dict:
        hashed_str = None
        if self.hashed_password:
            base64_bytes = base64.b64encode(self.hashed_password)
            hashed_str = base64_bytes.decode("ascii")
        data = {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "hashed_password": hashed_str,
            "chat_history": self.chat_history,
        }
        return data
