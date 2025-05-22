import logging
import re
from typing import Any

import phonenumbers as ph
from phonenumbers import format_number
from phonenumbers.phonenumberutil import NumberParseException
from pydantic import (
    GetCoreSchemaHandler,
)
from pydantic_core import CoreSchema, core_schema

from app.modules.auth_module.utils.errors import (
    AuthIncorrectPasswordError,
)
from app.settings import config


class BaseValidator:
    @classmethod
    def _validate(cls, value: str, /) -> str:
        raise NotImplementedError

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate, core_schema.str_schema()
        )


class EmailStr(BaseValidator):
    @classmethod
    def _validate(cls, email: str, /) -> str:
        email_pattern = config.auth.email_pattern

        if re.fullmatch(email_pattern, email):
            return email
        raise ValueError("Email incorrect")


class PasswordStr(BaseValidator):
    @classmethod
    def _validate(cls, password: str, /) -> str:
        err = AuthIncorrectPasswordError()
        err.fields = [
            {
                "field": ["body", "password"],
                "code": "PASSWORD_INCORRECT",
                "text": "Does not match password rules",
                "input": password,
            }
        ]

        if password:
            if config.auth.password_strip_enabled:
                password = password.strip()
            pattern = re.compile(config.auth.password_pattern)
            if re.match(pattern, password):
                return password
            else:
                raise err
        else:
            err.fields[0]["text"] = "Password shouldn't be empty"
            raise err


class PhoneStr(BaseValidator):
    @classmethod
    def _validate(cls, phone: str, /) -> str:
        err = ValueError("Phone number incorrect")
        if not isinstance(phone, str):
            raise err
        try:
            phone = ph.parse(phone, region="RU")
        except NumberParseException as e:
            logging.warning(f"Phone Validator. Number parser error: {e}")
            raise err

        if not ph.is_possible_number(phone):
            logging.warning(f"Phone Validator. Number is impossible: {phone}")
            raise err

        if not ph.is_valid_number(phone):
            logging.warning(f"Phone Validator. Number is invalid: {phone}")
            raise err

        # возвращает в 7XXXXXXXXXX
        # return f"{phone.country_code}{phone.national_number}"

        # возвращает в +7XXXXXXXXXX
        return format_number(phone, ph.PhoneNumberFormat.E164)
