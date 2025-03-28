import bcrypt
from dataclasses import dataclass, field
import re
import uuid


@dataclass
class User:
    id: uuid.UUID = field(default_factory=lambda: uuid.uuid4())
    name: str = None
    email: str = None
    hashed: bytes = None

    def __post_init__(self):
        self.validate()

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

        if not isinstance(self.hashed, bytes):
            raise ValueError(
                f"Invalid hashed '{self.hashed}' "
                f"({type(self.hashed).__name__}) - "
                f"must be bytes"
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
    def is_valid_password(
        password: str, passcode: str, hashed: bytes
    ) -> bool:

        combined = User.combine_pass(password, passcode)
        return bcrypt.checkpw(combined, hashed)

    @staticmethod
    def hash_pass(password: str, passcode: str) -> bytes:
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
