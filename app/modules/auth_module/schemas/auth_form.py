from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, ValidationError


class OAuth2EmailRequestForm(OAuth2PasswordRequestForm):
    def __init__(
        self,
        email: EmailStr | None = Form(None, description="User email"),
        username: EmailStr | None = Form(None),
        password: str = Form(...),
        fingerprint: str | None = Form(None),
    ):
        if not email and not username:
            raise ValidationError(
                "Either 'email' or 'username' must be provided.", OAuth2EmailRequestForm
            )
        super().__init__(
            username=email or username,
            password=password,
        )
        self.email = email
        self.fingerprint = fingerprint
