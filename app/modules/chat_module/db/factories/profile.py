from uuid import uuid4

from app.modules.auth_module.db.factories.account import accounts
from app.utils.fake_client import fake

profiles = {
    "target_class": "app.modules.chat_module.db.models.profile:ProfileModel",
    "data": [
        {
            "id": uuid4(),
            "last_name": fake.last_name_male(),
            "first_name": fake.first_name_male(),
            "middle_name": fake.middle_name_male(),
            "username": fake.word(),
            "!refs": {
                "account_id": {
                    "target_class": "app.modules.auth_module.db.models.account:AccountModel",
                    "criteria": {"id": acc["id"]},
                    "field": "id",
                },
            },
        }
        for acc in accounts["data"]
    ],
}


profile_personal_data = {
    "target_class": "app.modules.chat_module.db.models.profile:ProfilePersonalDataModel",
    "data": [
        {
            "id": uuid4(),
            "phone": fake.phone(),
            "!refs": {
                "profile_id": {
                    "target_class": "app.modules.chat_module.db.models.profile:ProfileModel",
                    "criteria": {"id": profile["id"]},
                    "field": "id",
                },
            },
        }
        for profile in profiles["data"]
    ],
}
