import bcrypt
import pytest
import uuid

from models.user import User


@pytest.mark.parametrize(
    "id, name, email, hashed",
    [
        (
            uuid.uuid4(),
            "abcd",
            "email@example.com",
            bcrypt.hashpw(f"password:passcode".encode(), bcrypt.gensalt()),
        ),
    ],
)
def test_user_valid(id, name, email, hashed):
    user = User(id, name, email, hashed)
    assert user.name == name
    assert user.email == email
    assert user.hashed == hashed
    assert isinstance(user.id, uuid.UUID)


@pytest.mark.parametrize(
    "id, name, email, hashed",
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
def test_user_invalid_id(id, name, email, hashed):
    with pytest.raises(ValueError) as e:
        User(id, name, email, hashed)
    assert "Invalid user id" in str(e.value)


@pytest.mark.parametrize(
    "id, name, email, hashed",
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
def test_user_invalid_name(id, name, email, hashed):
    with pytest.raises(ValueError) as e:
        User(id, name, email, hashed)
    assert "Invalid user name" in str(e.value)


@pytest.mark.parametrize(
    "id, name, email, hashed",
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
def test_user_invalid_email(id, name, email, hashed):
    with pytest.raises(ValueError) as e:
        User(id, name, email, hashed)
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
def test_hash_pass(password, passcode):
    hashed = User.hash_pass(password, passcode)
    assert isinstance(hashed, bytes)
    assert len(hashed) > 0
    assert bcrypt.checkpw(User.combine_pass(password, passcode), hashed)


@pytest.mark.parametrize(
    "password, passcode",
    [
        ("secure_password", "secure_passcode"),
        ("mypassword123", "mysecretcode"),
        ("pass", "code"),
    ],
)
def test_is_valid_password_true(password, passcode):
    hashed = User.hash_pass(password, passcode)
    assert User.is_valid_password(password, passcode, hashed) is True


@pytest.mark.parametrize(
    ("password", "passcode", "wrong_password", "wrong_passcode"),
    [
        ("secure_password", "secure_passcode", "wrong", "wrong"),
        ("mypassword123", "mysecretcode", "wrong", "wrong"),
        ("pass", "code", "wrong", "wrong"),
    ],
)
def test_is_valid_password_false(password, passcode, wrong_password, wrong_passcode):
    hashed = User.hash_pass(password, passcode)
    assert User.is_valid_password(wrong_password, passcode, hashed) is False
    assert User.is_valid_password(password, wrong_passcode, hashed) is False
    assert User.is_valid_password(wrong_password, wrong_passcode, hashed) is False
