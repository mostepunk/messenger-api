import re


def extract_key_info(error_message: str) -> dict:
    """
    Извлекает имя колонки и её значение из текста ошибки PostgreSQL формата:
    'Key (column_name)=(value) is not present in table "table_name".'

    Args:
        error_message: Текст ошибки PostgreSQL

    Returns:
        Словарь с ключами 'column', 'value', 'table' или пустой dict, если не найдено
        Пример: {'column': 'gender_id', 'value': 'ef50eb92-...', 'table': 'catalogue_gender'}
    """
    pattern = r'Key \((.*?)\)=\((.*?)\) is not present in table "(.*?)"'
    match = re.search(pattern, error_message)

    if match:
        return {
            "column": match.group(1),
            "value": match.group(2),
            "table": match.group(3),
        }
    return {}
