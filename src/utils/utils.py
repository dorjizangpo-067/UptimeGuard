from fastapi import HTTPException
from itsdangerous import BadSignature, SignatureExpired, URLSafeSerializer
from pwdlib import PasswordHash

from src.config import config

serializer = URLSafeSerializer(
    secret_key=config.JWT_SECRET_KEY.get_secret_value(), salt="email-configuration"
)

password_hash = PasswordHash.recommended()


def generate_password_hash(password: str) -> str:
    hash = password_hash.hash(password)
    return hash


def verify_password(password: str, hash_password: str) -> bool:
    return password_hash.verify(password, hash_password)


def create_url_save_token(data: dict) -> str:
    """Serialize a dict into a URLSafe token"""

    token = serializer.dumps(data)
    return token


def decode_url_safe_token(token: str):
    """Deserialize a URLSafe token to get data"""

    try:
        token_data = serializer.loads(token)

        return token_data

    except SignatureExpired:
        raise HTTPException(status_code=400, detail="Token has expired")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid token")
