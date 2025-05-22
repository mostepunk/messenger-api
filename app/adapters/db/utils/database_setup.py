import glob
import os

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, drop_database
from sqlalchemyseeder import ResolvingSeeder

from app.adapters.db import SYNC_SESSION
from app.adapters.db.utils.file_search import find_file_in_upfolders
from app.modules.auth_module.db.factories.account import accounts
from app.modules.catalogues_module.db.factories.catalogues import CATALOGUES_DATA
from app.modules.catalogues_module.utils.generate_sql_for_catalogues import (
    generate_insert_sql,
)
from app.modules.chat_module.db.factories.profile import profile_personal_data, profiles
from app.modules.notify_module.db.factories.factory import (
    notification_attachments,
    notification_templates,
)
from app.settings import config

engine = create_engine(config.db.alembic_db_uri)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def manual_drop_database():
    drop_database(config.db.dsn_no_driver)
    print(f"Database {config.db.db} dropped")


def drop_tables():
    engine = create_engine(config.db.dsn_no_driver)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)
    print(f"All Tables in {config.db.db} dropped")


def manual_create_database():
    create_database(config.db.dsn_no_driver)
    print(f"Database {config.db.db} created")


def run_migrations():
    alembic_path = find_file_in_upfolders(os.path.dirname(__file__), "alembic.ini")
    alembic_cfg = Config(alembic_path)
    command.upgrade(alembic_cfg, "head")
    print("Migrations applied.")


def clean_old_migration_files():
    directory = "app/modules/database_module/db/migrations/versions"
    pattern = os.path.join(directory, "202*")
    files = glob.glob(pattern)

    for file in files:
        if os.path.isfile(file):
            os.remove(file)
            print(f"Removed: {file}")


def fill_tables_with_fake_data():
    full_data = [
        accounts,
        notification_templates,
        notification_attachments,
        profiles,
        profile_personal_data,
    ]
    with SYNC_SESSION() as session:
        for sql in generate_insert_sql(CATALOGUES_DATA):
            session.execute(text(sql))
            session.commit()

    seeder = ResolvingSeeder(SYNC_SESSION())
    seeder.load_entities_from_data_dict(
        full_data,
        separate_by_class=True,
        commit=True,
    )
    print("Tables filled with fake data.")
