import random

from faker import Faker
from faker.providers import BaseProvider, DynamicProvider, file, misc

from app.modules.auth_module.db.factories.account import accounts
from app.modules.catalogues_module.db.factories.catalogues import CATALOGUES_DATA

fake = Faker("ru_RU")


class ClearPhoneProvider(BaseProvider):
    """Встроенный провайдер телефонов генерит номера со скобочками и прочей ересью."""

    def phone(self):
        code = random.choice(
            [
                900,
                901,
                902,
                903,
                904,
                905,
                906,
                908,
                909,
                910,
                911,
                912,
                913,
                914,
                915,
                916,
                917,
                918,
                919,
                920,
                921,
                922,
                923,
                924,
                925,
                926,
                927,
            ]
        )
        numbers = "".join([str(random.choice(range(9))) for i in range(7)])
        return f"7{code}{numbers}"


class AccountIdProvider(BaseProvider):
    """Вставка одного из созданных клиентов."""

    def account_id(self):
        ids = [acc["id"] for acc in accounts["data"]]
        return random.choice(ids)


# TODO: Решить, что делать с этими каталогами
for provider in CATALOGUES_DATA:
    fake.add_provider(
        DynamicProvider(
            provider_name=provider,
            elements=[catalogue.get("key") for catalogue in CATALOGUES_DATA[provider]],
        )
    )

fake.add_provider(ClearPhoneProvider)
fake.add_provider(AccountIdProvider)
fake.add_provider(file)
fake.add_provider(misc)
