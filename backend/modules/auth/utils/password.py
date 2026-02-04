import bcrypt
from pydantic import SecretStr, SecretBytes


def password_hashed(password: SecretStr) -> SecretBytes:
    return SecretBytes(
        bcrypt.hashpw(
            password=password.get_secret_value().encode("utf-8"), 
            salt=bcrypt.gensalt()
        )
    )

def password_verify(password: SecretStr, password_hash: SecretBytes) -> bool:
    return bcrypt.checkpw(
        password=password.get_secret_value().encode("utf-8"),
        hashed_password=password_hash.get_secret_value()
    )