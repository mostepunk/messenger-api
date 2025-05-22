import logging
from uuid import UUID

from fastapi import BackgroundTasks
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth_module.db.cruds import AccountCRUD
from app.modules.auth_module.db.cruds.account_session_crud import AccountSessionCRUD
from app.modules.auth_module.dependencies.errors import (
    InvalidTokenError,
    InvalidTokenTypeError,
)
from app.modules.auth_module.dependencies.jwt_decode import (
    decode_token_and_check_exp,
)
from app.modules.auth_module.schemas.account import (
    AccountDBSchema,
    AccountRegisterSchema,
)
from app.modules.auth_module.schemas.account_session import AccountSessionBaseSchema
from app.modules.auth_module.schemas.token import Token, TokenTypeEnum
from app.modules.auth_module.utils.const import EMPTY_FINGER_PRINT
from app.modules.auth_module.utils.errors import (
    AccountAlreadyExists,
    AccountAlreadyVerified,
    AccountNotExists,
    CredentialsError,
)
from app.modules.auth_module.utils.password import get_password_hash, verify_password
from app.modules.base_module.db.errors import (
    ItemNotFoundError,
)
from app.modules.base_module.services.base_service import BaseService
from app.modules.notify_module.schemas.notify_schemas import NotificationTypeEnum
from app.modules.notify_module.services.notification_service import NotificationService
from app.settings import config


class AuthService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.crud = AccountCRUD(session)
        self.s_crud = AccountSessionCRUD(session)
        self.notification_service = NotificationService()

    async def authenticate_user(
        self, email: str, plain_password: str, fingerprint: str
    ) -> AccountDBSchema:
        if fingerprint is None:
            # FP может быть пустым.
            fingerprint = EMPTY_FINGER_PRINT

        db_account = await self.crud.find_by_email(email)
        if not db_account.is_confirmed:
            logging.warning(f"Account.ID: {db_account.id}. Email not confirmed.")
            raise CredentialsError
        if not verify_password(plain_password, db_account.password):
            logging.warning(f"Account.ID: {db_account.id}. Password invalid.")
            raise CredentialsError

        logging.debug(
            f"Account.ID {db_account.id}. Has {len(db_account.sessions)} active sessions"
        )
        if not db_account.can_account_create_session:
            pass
        new_session = await self.create_or_update_session(db_account, fingerprint)
        await self.session.commit()
        return new_session

    async def register_user(
        self,
        account: AccountRegisterSchema,
        background_tasks: BackgroundTasks,
    ) -> AccountDBSchema:
        """Запись пользователя в БД и послать письмо.

        Первый раз отправляет email, password:
        - вводит логин и пароль
        - сохраняю в БД как неподтвержденного
        - создаю confirmation_token
        - отправка ссылки на почту

        Пользователь повторно вводит почту и пароль:
        - если запись уже существует:
          - если email подтвержден: ошибка AccountAlreadyExists
          - иначе обновить данные
            > если аккаунт не подтвержден, значит ему не пришло письмо,
            > и надо выслать его еще раз
        - иначе создать нового неподтвержденного пользователя
        """
        account_dict = account.dict()
        account_dict["password"] = get_password_hash(account.password)

        db_account: AccountDBSchema | None = await self.crud.find_by_email(
            account.email, raise_err=False
        )
        if db_account is not None:
            if db_account.is_confirmed:
                raise AccountAlreadyExists
            else:
                await self.crud.update(db_account.id, account_dict)

        elif db_account is None:
            db_account: AccountDBSchema = await self.crud.add(account_dict)

        confirmation_token = db_account.confirm_token
        await self.crud.update(
            db_account.id, {"confirmation_token": confirmation_token}
        )
        await self.session.commit()

        template_url = "{domain}{endpoint}?token={confirmation_token}"
        notify_kwargs = {
            "type": NotificationTypeEnum.email,
            "code": "confirm_email",
            "recipients": [
                {
                    "emails": [db_account.email],
                    "params": {
                        "url": template_url.format(
                            domain=config.app.domain,
                            endpoint=config.app.route_confirm_password,
                            confirmation_token=confirmation_token,
                        )
                    },
                }
            ],
        }

        background_tasks.add_task(self.notification_service.notify, notify_kwargs)
        return db_account

    async def confirm_email(self, token: str, fingerprint: str) -> bool:
        """Подтверждение почты:

        После регистрации выслана ссылка на почту:
        - Ссылка ведет на фронтовую страницу
        - Фронт подставляет данные, присылает token и fingerprint

        Пользователь первый раз переходит на ссылку:
        - проверяю токен. Возможные ошибки:
          - TokenExpiredError: токен протух
          - InvalidTokenTypeError: должен быть прислан токен с типом confirmation_token
          - InvalidTokenError: токен не соответствует сохраненному в БД
        - Создаю сессию, сохраняю в БД
        - Записываю куки и отдаю access_token

        Пользователь повторно переходит по ссылке:
        - аккаунт уже подтвержден - ошибка AccountAlreadyVerified
        """
        if fingerprint is None:
            # FP может быть пустым.
            fingerprint = EMPTY_FINGER_PRINT
        token_schema: Token = await decode_token_and_check_exp(token)
        try:
            account: AccountDBSchema = await self.crud.get_by_id(token_schema.user_id)
        except ItemNotFoundError as err:
            logging.warning(f"{err}")
            raise CredentialsError

        if token_schema.token_type != TokenTypeEnum.confirmation_type:
            raise InvalidTokenTypeError

        if account.confirmation_token != token:
            raise InvalidTokenError

        if account.is_confirmed:
            raise AccountAlreadyVerified(
                f"Account.ID: {account.id}. Already confirmed email"
            )

        new_session = await self.create_or_update_session(account, fingerprint)
        await self.crud.update(
            account.id, {"is_confirmed": True, "confirmation_token": None}
        )
        await self.session.commit()
        logging.debug(
            f"Account.ID: {account.id}. Email confirmed. Account session created"
        )
        return new_session

    async def account_email_exists(self, email: EmailStr):
        if email is None:
            return False
        db_account = await self.crud.find_by_email(email, raise_err=False)
        if db_account and db_account.is_confirmed:
            return True
        return False

    async def reset_account_password(
        self, email: EmailStr, background_tasks: BackgroundTasks
    ):
        """Восстановление пароля:

        - Создать confirmation_token
        - На почту отправить ссылку для восстановления пароля с токеном
        - Новый пароль присылает запросом:
          - POST /accounts/password/set/ {password: new_password}
        """
        account: AccountDBSchema = await self.crud.find_by_email(email, raise_err=False)
        if not account:
            raise AccountNotExists

        confirmation_token = account.confirm_token
        await self.crud.update(account.id, {"confirmation_token": confirmation_token})
        await self.session.commit()

        template_url = "{domain}{endpoint}?token={token}"
        notify_kwargs = {
            "type": NotificationTypeEnum.email,
            "code": "reset_password",
            "recipients": [
                {
                    "emails": [account.email],
                    "params": {
                        "url": template_url.format(
                            domain=config.app.domain,
                            endpoint=config.app.route_setup_new_password,
                            token=confirmation_token,
                            account_id=account.id,
                        )
                    },
                }
            ],
        }

        background_tasks.add_task(self.notification_service.notify, notify_kwargs)

    async def update_password(self, account_id: UUID, new_password: str):
        """Заменить старый пароль новым.

        - Только обновление пароля. Больше ничего.
        """
        db_account: AccountDBSchema = await self.crud.get_by_id(account_id)
        await self.crud.update(
            db_account.id, {"password": get_password_hash(new_password)}
        )
        await self.session.commit()
        logging.debug(f"Account.ID {account_id} password updated successfully")

    async def refresh_account_token(
        self, account_id: UUID, refresh_token: str, fingerprint: str
    ) -> AccountSessionBaseSchema:
        """Обновить access_token и refresh_token.

        - Через куку получаю refresh_token, провераю на валидность.
        - Поиск среди активных сессий по refresh_token
        - Если не найдено - ошибка
        - Если не совпадает fingerprint с найденной - ошибка
          - стереть из БД запись с этим refresh_token
        - Обновить в БД refresh_token и access_token
        - Вернуть новые access_token и refresh_token.
        - refresh_token записать в куку
        """
        fingerprint = fingerprint or EMPTY_FINGER_PRINT
        db_account: AccountDBSchema = await self.crud.get_by_id(account_id)
        account_session: AccountSessionBaseSchema = db_account.get_session(
            refresh_token, "refresh_token"
        )
        if not account_session:
            logging.warning(f"Account.ID: {db_account.id}. Session Not Found")
            raise InvalidTokenError

        if account_session.fingerprint != fingerprint:
            logging.warning(f"Account.ID: {db_account.id}. Incorrect fingerprint")
            await self.s_crud.delete_session(account_session.refresh_token)
            await self.session.commit()
            raise InvalidTokenError

        new_session = db_account.create_session(fingerprint)
        await self.s_crud.update_refresh_token(
            refresh_token, account_id, new_session.dict()
        )
        logging.debug(f"Account.ID: {db_account.id} Session updated.")
        await self.session.commit()
        return new_session

    async def check_token_and_create_session(
        self, confirmation_token: str, fingerprint: str
    ):
        """Проверка confirmation_token, перед тем как пользователь задаст новый пароль.
        Проверить токен:
          - если валиден: {status: success} и токены
          - иначе: {status: error} и причина ошибки
          - создать новую сессию
          - изничтожить confirmation_token в таблице.
          - сохранить сессию в БД.
          - отдать токены
        """
        token_schema: Token = await decode_token_and_check_exp(confirmation_token)
        if token_schema.token_type != TokenTypeEnum.confirmation_type:
            raise InvalidTokenTypeError

        db_account: AccountDBSchema = await self.crud.get_by_id(token_schema.user_id)
        if db_account.confirmation_token != confirmation_token:
            raise InvalidTokenError

        new_session = await self.create_or_update_session(db_account, fingerprint)

        db_account_values = {"confirmation_token": None}
        if not db_account.is_confirmed:
            db_account_values["is_confirmed"] = True
        await self.crud.update(db_account.id, db_account_values)

        await self.session.commit()
        logging.debug(f"Account.ID: {db_account.id}. Token Verified. Session created")
        return new_session

    async def create_or_update_session(
        self, db_account: AccountDBSchema, fingerprint: str
    ):
        fingerprint = fingerprint or EMPTY_FINGER_PRINT
        new_session: AccountSessionBaseSchema = db_account.create_session(
            fingerprint=fingerprint
        )
        account_session: AccountSessionBaseSchema | None = db_account.get_session(
            fingerprint, "fingerprint"
        )
        if not account_session:
            await self.s_crud.add(new_session)
            logging.debug(f"Account.ID: {db_account.id} session created")
        else:
            await self.s_crud.update_refresh_token(
                account_session.refresh_token, db_account.id, new_session.dict()
            )
            logging.debug(f"Account.ID: {db_account.id} session updated")
        await self.session.flush()
        return new_session

    async def logout_account(self, refresh_token: str):
        await self.s_crud.delete_session(refresh_token)
        await self.session.commit()
        logging.debug("Refresh token destroyed")
