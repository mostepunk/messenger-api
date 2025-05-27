from uuid import uuid4

from app.modules.auth_module.utils.password import get_password_hash

accounts = {
    "target_class": "app.modules.auth_module.db.models.account:AccountModel",
    "data": [
        {
            "id": uuid4(),
            "email": "admin@admin.ru",
            "password": get_password_hash("admin"),
            "is_confirmed": True,
        },
        {
            "id": uuid4(),
            "email": "api-test@example.com",
            "password": get_password_hash("ooKyjmocCdom5qDobvYiEYtMxEtFhFM5Znez"),
            "is_confirmed": True,
        },
        {
            "id": uuid4(),
            "email": "user1@example.com",
            "password": get_password_hash("admin"),
            "is_confirmed": True,
        },
        {
            "id": uuid4(),
            "email": "user2@example.com",
            "password": get_password_hash("admin"),
            "is_confirmed": True,
        },
        {
            "id": uuid4(),
            "email": "user3@example.com",
            "password": get_password_hash("admin"),
            "is_confirmed": True,
        },
    ],
}
