import logging
import pathlib
from typing import NoReturn


class BaseModuleCreator:
    """BaseModuleCreator."""

    def __init__(self, name: str, root_dir: str) -> None:
        self.root_dir = root_dir
        self.name = name
        self.module_path = f"{self.root_dir}/{self.name}"

    def create_modules(self) -> NoReturn:
        """Создание всех основных модулей."""
        raise NotImplementedError()

    def create_module(self, module_name: str) -> None:
        """Создание папки и внутри файл `__init__.py`

        Args:
            module_name (str): имя модуля
        """
        self.create_folder(module_name)
        self.create_file(f"{module_name}/__init__.py")

    def create_folder(self, folderpath: str) -> None:
        """Создание папки.

        Args:
            folderpath (str): относительный путь к папке
        """
        dir_path = pathlib.Path(folderpath)
        try:
            dir_path.mkdir(exist_ok=True)
            logging.debug(f"Directory '{dir_path}' created successfully.")
        except OSError as err:
            logging.exception(f"Error creating directory: {err}")

    def create_file(self, filepath: str) -> None:
        """Создание файла.

        Args:
            filepath (str): относительный путь к файлу
        """
        file_path = pathlib.Path(filepath)

        try:
            file_path.touch()
            logging.debug(f"File '{file_path}' created successfully.")
        except OSError as e:
            logging.exception(f"Error creating file: {e}")

    def write_file(self, filepath: str, filetext: str) -> None:
        """Запись текста в файл.

        Args:
            filepath (str): относительный путь к файлу
            filetext (str): содержимое файла в виде строки
        """
        file_path = pathlib.Path(filepath)

        try:
            with file_path.open("w") as file:
                file.write(filetext)

            logging.debug(f"File '{file_path}' written successfully.")
        except OSError as e:
            logging.exception(f"Error writing file: {e}")
