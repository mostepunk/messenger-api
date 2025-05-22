import bcrypt
from passlib.context import CryptContext

# https://github.com/pyca/bcrypt/issues/684#issuecomment-2465572106
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("about", (object,), {"__version__": bcrypt.__version__})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
