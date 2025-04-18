import logging

class InvalidPasswordError(Exception):
    def __init__(self, email):
        message = f"Invalid password/passcode for e-mail: {email}."
        logging.warning(message)
        super().__init__(message)

class UserNotFoundError(Exception):
    def __init__(self, identifier):
        message = f"User not found: {identifier}."
        logging.warning(message)
        super().__init__(message)

class UserAlreadyExistsError(Exception):
    def __init__(self, email):
        message = f"User e-mail already exists: {email}."
        logging.warning(message)
        super().__init__(message)
