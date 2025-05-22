CATALOGUE_DICT = dict[str, list[dict[str, str]]]


def generate_insert_sql(data: CATALOGUE_DICT) -> str:
    """Генерирует INSERT для каталогов.
    На вход принимает словарь следующего вида:

    ```
    {
        "catalogue_table_name": [
            {"key": "someKey", "value": "Значение ключа"},
            # ...
        ],
    }
    ```
    На выходе отдает SQL запрос для инсерта

    ```
    INSERT INTO catalogue_table_name ("key", value) VALUES ('someKey', 'Значение ключа');
    ```
    """
    insert_template = 'INSERT INTO {table_name} ("key", value) VALUES '
    values_row = "\n('{key}', '{value}'),"

    for table_name in data:
        full_query = insert_template.format(table_name=table_name)

        for table_data in data[table_name]:
            full_query += values_row.format(
                key=table_data["key"],
                value=table_data["value"],
            )

        yield full_query.rstrip(",") + ";"


def generate_truncate_sql(data: CATALOGUE_DICT) -> str:
    """Генерирует TRUNCATE CASCADE для таблиц в каталоге.

    !WARNING!ACHTUNG!ALARM!
    Применять с осторожностью, может каскадно удалить данные.

    На вход принимает словарь следующего вида:

    ```
    {
        "catalogue_table_name": [
            {"key": "someKey", "value": "Значение ключа"},
            # ...
        ],
    }
    ```
    На выходе отдает SQL запрос для инсерта

    ```
    TRUNCATE table "catalogue_table_name" CASCADE
    ```
    """
    query_template = 'TRUNCATE table "{table_name}" CASCADE'

    for table_name in data:
        yield query_template.format(table_name=table_name)
