import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Request,
    Response,
)

from app.dependencies.services_dependency import get_service
from app.modules.auth_module.dependencies.jwt_decode import (
    check_refresh_token,
    get_account_from_token,
)
from app.modules.auth_module.schemas.account import (
    AccountConfirmEmailSchema,
    AccountPasswordResetSchema,
    AccountRefreshTokenSchema,
    AccountRegisterSchema,
    AccountSchema,
    AccountSignInSchema,
    EmailExistsSchema,
    NewPasswordsSchema,
)
from app.modules.auth_module.schemas.account_session import AccountSessionBaseSchema
from app.modules.auth_module.schemas.auth_form import OAuth2EmailRequestForm
from app.modules.auth_module.schemas.token import AuthTokens
from app.modules.auth_module.services import AuthService
from app.modules.auth_module.utils.errors import (
    CredentialsError,
)
from app.modules.base_module.db.errors import ItemNotFoundError
from app.modules.base_module.schemas.customs import EmailStr

router = APIRouter()


router = APIRouter()


@router.post("/sign-in/swagger/", include_in_schema=False)
async def login_swager(
    response: Response,
    form_data: Annotated[OAuth2EmailRequestForm, Depends()],
    service: Annotated[get_service(AuthService), Depends()],
):
    """Ендпоинт для логина через свагер."""
    try:
        session: AccountSessionBaseSchema = await service.authenticate_user(
            form_data.email or form_data.username,
            form_data.password,
            form_data.fingerprint or "SWAGGER",
        )
    except ItemNotFoundError:
        raise CredentialsError

    response.set_cookie(
        key="refresh_token",
        value=session.refresh_token,
        httponly=True,
        # domain=config.app.frontend_domain,
        path="/accounts/",
        # secure=True,
        samesite="Lax",
    )
    return {"access_token": session.access_token, "token_type": "bearer"}


@router.post(
    "/sign-in/",
    summary="логин",
    response_model=AuthTokens,
)
async def login_user(
    response: Response,
    data: AccountSignInSchema,
    service: Annotated[get_service(AuthService), Depends()],
):
    try:
        session: AccountSessionBaseSchema = await service.authenticate_user(
            data.email, data.password, data.fingerprint
        )
    except ItemNotFoundError:
        raise CredentialsError

    response.set_cookie(
        key="refresh_token",
        value=session.refresh_token,
        httponly=True,
        path="/accounts/",
        samesite="Lax",
    )
    return {"access_token": session.access_token}


@router.post(
    "/sign-up/",
    summary="регистрация пользователя",
    response_model=AccountSchema,
)
async def register(
    request: Request,
    account: AccountRegisterSchema,
    background_tasks: BackgroundTasks,
    service: Annotated[get_service(AuthService), Depends()],
):
    return await service.register_user(account, background_tasks)


@router.post("/sign-out/", summary="логаут")
async def logout(
    request: Request,
    response: Response,
    service: Annotated[get_service(AuthService), Depends()],
):
    refresh_token = request.cookies.get("refresh_token")
    # TODO: продумать очистку мертвых рефрешей.
    if refresh_token:
        try:
            await check_refresh_token(refresh_token)
            await service.logout_account(refresh_token)
        except Exception as err:
            logging.warning(f"Error while sign-out: {err}")
    response.delete_cookie("refresh_token")


@router.get(
    "/me/",
    summary="Информация об авторизованном пользователе",
    response_model=AccountSchema,
)
async def about_me(account: Annotated[get_account_from_token, Depends()]):
    return account


@router.get(
    "/email/status/",
    summary="Проверка не занята ли такая почта",
    response_model=EmailExistsSchema,
)
async def email_check(
    service: Annotated[get_service(AuthService), Depends()],
    email: EmailStr | None = None,
):
    is_exists: bool = await service.account_email_exists(email)
    return {"exists": is_exists}


@router.post(
    "/email/confirm/", summary="Подтверждение почты", response_model=AuthTokens
)
async def confirm(
    response: Response,
    data: AccountConfirmEmailSchema,
    service: Annotated[get_service(AuthService), Depends()],
):
    session = await service.confirm_email(data.confirmation_token, data.fingerprint)
    response.set_cookie(
        key="refresh_token",
        value=session.refresh_token,
        httponly=True,
        path="/accounts/",
        samesite="Lax",
    )
    return {"access_token": session.access_token}


@router.post("/token/refresh/", summary="Обновить токен", response_model=AuthTokens)
async def refresh_token(
    response: Response,
    request: Request,
    service: Annotated[get_service(AuthService), Depends()],
    data: AccountRefreshTokenSchema,
):
    refresh_token = request.cookies.get("refresh_token")
    account = await check_refresh_token(refresh_token)
    account_session = await service.refresh_account_token(
        account.user_id, refresh_token, data.fingerprint if data else None
    )
    response.set_cookie(
        key="refresh_token",
        value=account_session.refresh_token,
        httponly=True,
        path="/accounts/",
        samesite="Lax",
    )
    return {
        "access_token": account_session.access_token,
        "token_type": "bearer",
    }


@router.post(
    "/token/redeem/",
    summary="Подтверждение confirmation_token",
    response_model=AuthTokens,
)
async def token_confirm(
    response: Response,
    data: AccountConfirmEmailSchema,
    service: Annotated[get_service(AuthService), Depends()],
):
    session = await service.check_token_and_create_session(
        data.confirmation_token, data.fingerprint
    )
    response.set_cookie(
        key="refresh_token",
        value=session.refresh_token,
        httponly=True,
        path="/accounts/",
        samesite="Lax",
    )
    return {"access_token": session.access_token}


@router.post("/password/reset/", summary="Запрос на сброс пароля")
async def reset_password(
    data: AccountPasswordResetSchema,
    service: Annotated[get_service(AuthService), Depends()],
    background_tasks: BackgroundTasks,
):
    """
    ## Сброс пароля:

    ### Пользователь не может аутентифицироваться:

    - жмет забыл пароль.
    - приходит письмо с токеном
    - переходит по ссылке
    - фронт делает запрос на /accounts/token/confirm/
      - присылает confirmation_token и fingerprint
      - в ответе получает access_token и refresh_token в куке
    - вводит новый пароль.
      - запрос на /accounts/password/set/
    """
    await service.reset_account_password(data.email, background_tasks)


@router.post(
    "/password/set/",
    summary="Установка нового пароля",
)
async def update_password(
    password: NewPasswordsSchema,
    account: Annotated[get_account_from_token, Depends()],
    service: Annotated[get_service(AuthService), Depends()],
):
    await service.update_password(account.id, password.password)
