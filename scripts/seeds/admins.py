from apps.users.models import User
from apps.users.storages.users_storage import get_random_string, hash_password
from core import logger

from scripts.db_session import db_session

ADMINS = [
    {
        "username": "admin",
        "password": "password",
        "role": "admin",
        "email": "admin@example.com",
        "full_name": "admin",
    },
]


def perform(*args, **kwargs):
    for data in ADMINS:
        is_admin_exists = (
            db_session.query(User).filter_by(username=data["username"]).all()
        )
        salt = get_random_string()

        if not is_admin_exists:
            admin = {
                "username": data["username"],
                "email": data["email"],
                "role": data["role"],
                "hashed_password": f"{salt}${hash_password(data['password'], salt)}",
                "full_name": data["full_name"],
            }
            db_session.add(User(**admin))
        else:
            logger.warning(f"Admin {data['username']} already exists")

    db_session.commit()
    db_session.close()
