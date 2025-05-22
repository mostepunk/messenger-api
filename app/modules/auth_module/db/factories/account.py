import random
from uuid import uuid4

from app.modules.auth_module.utils.password import get_password_hash
from app.modules.chat_module.db.factories.profile import profiles

IDS = [profile["id"] for profile in profiles["data"]]


def profile_id():
    id = random.choice(IDS)
    return IDS.pop(IDS.index(id))


accounts = {
    "target_class": "app.modules.auth_module.db.models.account:AccountModel",
    "data": [
        {
            "id": uuid4(),
            "email": "admin@admin.ru",
            "password": get_password_hash("admin"),
            "is_confirmed": True,
            "!refs": {
                "profile_id": {
                    "target_class": "app.modules.chat_module.db.models.profile:ProfileModel",
                    "criteria": {"id": profile_id()},
                    "field": "id",
                },
            },
        },
        {
            "id": uuid4(),
            "email": "api-test@example.com",
            "password": get_password_hash("ooKyjmocCdom5qDobvYiEYtMxEtFhFM5Znez"),
            "is_confirmed": True,
            "!refs": {
                "profile_id": {
                    "target_class": "app.modules.chat_module.db.models.profile:ProfileModel",
                    "criteria": {"id": profile_id()},
                    "field": "id",
                },
            },
        },
        {
            "id": uuid4(),
            "email": "user1@example.com",
            "password": get_password_hash("admin"),
            "is_confirmed": True,
            "!refs": {
                "profile_id": {
                    "target_class": "app.modules.chat_module.db.models.profile:ProfileModel",
                    "criteria": {"id": profile_id()},
                    "field": "id",
                },
            },
        },
        {
            "id": uuid4(),
            "email": "user2@example.com",
            "password": get_password_hash("admin"),
            "is_confirmed": True,
            "!refs": {
                "profile_id": {
                    "target_class": "app.modules.chat_module.db.models.profile:ProfileModel",
                    "criteria": {"id": profile_id()},
                    "field": "id",
                },
            },
        },
        {
            "id": uuid4(),
            "email": "user3@example.com",
            "password": get_password_hash("admin"),
            "is_confirmed": True,
            "!refs": {
                "profile_id": {
                    "target_class": "app.modules.chat_module.db.models.profile:ProfileModel",
                    "criteria": {"id": profile_id()},
                    "field": "id",
                },
            },
        },
    ],
}
