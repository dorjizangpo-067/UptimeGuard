from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def generate_password_hash(password: str) -> str:
    hash = password_hash.hash(password)
    return hash


def verify_password(password: str, hash_password: str) -> bool:
    return password_hash.verify(password, hash_password)
