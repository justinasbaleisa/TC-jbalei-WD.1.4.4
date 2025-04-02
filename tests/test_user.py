import bcrypt
import pytest
import uuid

from models.user import User


@pytest.mark.parametrize(
    "id, name, email, hashed_password",
    [
        (
            uuid.uuid4(),
            "abcd",
            "email@example.com",
            bcrypt.hashpw(f"password:passcode".encode(), bcrypt.gensalt()),
        ),
    ],
)
def test_user_valid(id, name, email, hashed_password):
    user = User(id, name, email, hashed_password)
    assert user.name == name
    assert user.email == email
    assert user.hashed_password == hashed_password
    assert isinstance(user.id, uuid.UUID)


@pytest.mark.parametrize(
    "id, name, email, hashed_password",
    [
        (
            1,
            "abcd",
            "email@example.com",
            bcrypt.hashpw(f"password:passcode".encode(), bcrypt.gensalt()),
        ),
        (
            "",
            "abcd",
            "email@example.com",
            bcrypt.hashpw(f"password:passcode".encode(), bcrypt.gensalt()),
        ),
        (
            None,
            "abcd",
            "email@example.com",
            bcrypt.hashpw(f"password:passcode".encode(), bcrypt.gensalt()),
        ),
    ],
)
def test_user_invalid_id(id, name, email, hashed_password):
    with pytest.raises(ValueError) as e:
        User(id, name, email, hashed_password)
    assert "Invalid user id" in str(e.value)


@pytest.mark.parametrize(
    "id, name, email, hashed_password",
    [
        (
            uuid.uuid4(),
            "",
            "email@example.com",
            bcrypt.hashpw(f"password:passcode".encode(), bcrypt.gensalt()),
        ),
        (
            uuid.uuid4(),
            None,
            "email@example.com",
            bcrypt.hashpw(f"password:passcode".encode(), bcrypt.gensalt()),
        ),
        (
            uuid.uuid4(),
            True,
            "email@example.com",
            bcrypt.hashpw(f"password:passcode".encode(), bcrypt.gensalt()),
        ),
    ],
)
def test_user_invalid_name(id, name, email, hashed_password):
    with pytest.raises(ValueError) as e:
        User(id, name, email, hashed_password)
    assert "Invalid user name" in str(e.value)


@pytest.mark.parametrize(
    "id, name, email, hashed_password",
    [
        (
            uuid.uuid4(),
            "abcd",
            "",
            bcrypt.hashpw(f"password:passcode".encode(), bcrypt.gensalt()),
        ),
        (
            uuid.uuid4(),
            "abcd",
            None,
            bcrypt.hashpw(f"password:passcode".encode(), bcrypt.gensalt()),
        ),
        (
            uuid.uuid4(),
            "abcd",
            True,
            bcrypt.hashpw(f"password:passcode".encode(), bcrypt.gensalt()),
        ),
        (
            uuid.uuid4(),
            "abcd",
            ".user@example.com",
            bcrypt.hashpw(f"password:passcode".encode(), bcrypt.gensalt()),
        ),
    ],
)
def test_user_invalid_email(id, name, email, hashed_password):
    with pytest.raises(ValueError) as e:
        User(id, name, email, hashed_password)
    assert "Invalid email" in str(e.value)


@pytest.mark.parametrize(
    "email",
    [
        "user@example.com",
        "user.name+tag@domain.co",
        "user.name@sub.domain.com",
        "name.lastname@example.co.uk",
        "12345@example.com",
        "valid.email@domain.com",
        "user@subdomain.domain.com",
        "12@domain.com",
        "123456789012345678901234567890@domain.com",
    ],
)
def test_is_valid_email_true(email):
    assert User.is_valid_email(email) == True


@pytest.mark.parametrize(
    "email",
    [
        ".user@example.com",
        "user.@example.com",
        "user@.example.com",
        "user@domain",
        "user@domain..com",
        "user@domain.c",
        "user@domain@domain.com",
        "@example.com",
        "user@com",
        "1@domain.com",
        "1234567890123456789012345678901@domain.com",
    ],
)
def test_is_valid_email_false(email):
    assert User.is_valid_email(email) == False


@pytest.mark.parametrize(
    "password, passcode",
    [
        ("secure_password", "secure_passcode"),
        ("mypassword123", "mysecretcode"),
        ("pass", "code"),
    ],
)
def test_hash_password(password, passcode):
    hashed_password = User.hash_password(password, passcode)
    assert isinstance(hashed_password, bytes)
    assert len(hashed_password) > 0
    assert bcrypt.checkpw(User.combine_pass(password, passcode), hashed_password)


@pytest.mark.parametrize(
    "password, passcode",
    [
        ("secure_password", "secure_passcode"),
        ("mypassword123", "mysecretcode"),
        ("pass", "code"),
    ],
)
def test_is_valid_password_true(password, passcode):
    hashed_password = User.hash_password(password, passcode)
    assert User.is_valid_password(password, passcode, hashed_password) is True


@pytest.mark.parametrize(
    ("password", "passcode", "wrong"),
    [
        ("secure_password", "secure_passcode", "wrong"),
        ("mypassword123", "mysecretcode", "wrong"),
        ("pass", "code", "wrong"),
    ],
)
def test_is_valid_password_false(password, passcode, wrong):
    hashed_password = User.hash_password(password, passcode)
    assert User.is_valid_password(wrong, passcode, hashed_password) is False
    assert User.is_valid_password(password, wrong, hashed_password) is False
    assert User.is_valid_password(wrong, wrong, hashed_password) is False
