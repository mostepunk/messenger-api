import random

from app.settings import config

from .creator import ModuleCreator
from .figlet import figlets


def create_new_module(
    module_name: str,
    module_path: str = config.modules.root_base_dir,
):
    """Функция для создания нового модуля и всей иерархии подмодулей.

    Данный функционал необходим, чтобы не возникало ошибок при внедрении новых модулей.
    """
    mc = ModuleCreator(module_name, module_path)
    mc.create_modules()


def show_figlet():
    figlet = random.choice(figlets)
    print(figlet)
    print("Developed with love ❤️ \n")
