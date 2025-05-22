import random
from uuid import uuid4

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
        }
        for _ in range(5)
    ],
}


IDS = [profile["id"] for profile in profiles["data"]]


def profile_id():
    id = random.choice(IDS)
    return IDS.pop(IDS.index(id))


profile_personal_data = {
    "target_class": "app.modules.chat_module.db.models.profile:ProfilePersonalDataModel",
    "data": [
        {
            "id": uuid4(),
            "phone": fake.phone(),
            "!refs": {
                "profile_id": {
                    "target_class": "app.modules.chat_module.db.models.profile:ProfileModel",
                    "criteria": {"id": profile_id()},
                    "field": "id",
                },
            },
        }
        for _ in range(5)
    ],
}
