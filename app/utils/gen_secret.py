import secrets


def get_confirmation_token() -> str:
    return secrets.token_urlsafe(32)
