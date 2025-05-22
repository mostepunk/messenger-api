import os


def find_file_in_upfolders(start_path: str, filename: str):
    """Поиск файла по папкам выше, пока не найдет указанный файл."""
    current_path = os.path.abspath(start_path)

    while current_path != os.path.dirname(current_path):
        if os.path.isfile(os.path.join(current_path, filename)):
            return os.path.join(current_path, filename)

        current_path = os.path.dirname(current_path)

    raise FileNotFoundError(f"File: {filename} not found")
