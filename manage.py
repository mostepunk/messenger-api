import argparse
from argparse import RawDescriptionHelpFormatter
from random import SystemRandom

import pyfiglet

from app.adapters.db.utils.database_setup import (
    drop_tables,
    fill_tables_with_fake_data,
    manual_create_database,
    run_migrations,
)
from app.utils import create_new_module

TEXT_LOGO = "Messenger"
DB = "db"
MODULE = "module"
COMMANDS = {
    DB: {
        "help": "Операции над базой данных",
        "arguments": [
            {
                "args": ["-c", "--create"],
                "help": "Создать новую базу данных",
                "action": "store_true",
            },
            {
                "args": ["-d", "--drop"],
                "help": "Удалить базу данных",
                "action": "store_true",
            },
            {
                "args": ["-m", "--migrate"],
                "help": "Создать таблицы",
                "action": "store_true",
            },
            {
                "args": ["-f", "--fill"],
                "help": "Заполнить таблицы фейковыми данными",
                "action": "store_true",
            },
            {
                "args": ["-r", "--recreate"],
                "help": "Выполнить все вышеперечисленное",
                "action": "store_true",
            },
        ],
    },
    MODULE: {
        "help": "Создание нового модуля",
        "arguments": [
            {
                "args": ["-n", "--name"],
                "help": "передайте имя модуля на латинице",
                "type": str,
            }
        ],
    },
}


def logo():
    """Создание логотипа в меню --help.

    Returns:
        str: фиглет
    """
    fonts = [
        "larry3d",
        # "isometric2",
        "invita",
        "graffiti",
        "gothic",
        "fuzzy",
        "drpepper",
        # "doh",
        "cybermedium",
        "chunky",
        # "banner3-D",
        # "starwars",
        "stampatello",
        "speed",
        "smshadow",
        "shadow",
    ]
    label = pyfiglet.figlet_format(TEXT_LOGO, font=SystemRandom().choice(fonts))
    return f"""\n\033[33m{label}\033[0m"""


def init_parser():
    parser = argparse.ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=(f"{logo()}\nScript to manage with Messenger-cli.\n-----------\n"),
    )
    subparsers = parser.add_subparsers(dest="command")

    for command in COMMANDS:
        some_parser = subparsers.add_parser(
            command,
            help=COMMANDS[command]["help"],
        )
        for argument in COMMANDS[command]["arguments"]:
            if argument.get("action"):
                some_parser.add_argument(
                    *argument["args"],
                    action=argument.get("action"),
                    help=argument.get("help"),
                )
            elif argument.get("type"):
                some_parser.add_argument(
                    *argument["args"],
                    help=argument.get("help"),
                    type=argument.get("type"),
                )
    return parser


def main():
    parser = init_parser()

    args = parser.parse_args()

    if args.command == DB:
        if args.drop:
            drop_tables()

        elif args.create:
            manual_create_database()

        elif args.migrate:
            run_migrations()

        elif args.fill:
            fill_tables_with_fake_data()

        elif args.recreate:
            drop_tables()
            run_migrations()
            fill_tables_with_fake_data()

    elif args.command == MODULE:
        module_name = args.name

        if not module_name.endswith("_module"):
            module_name += "_module"

        print(f"Create new module with name: {module_name}")
        create_new_module(module_name)


if __name__ == "__main__":
    main()
