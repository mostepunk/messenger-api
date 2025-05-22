from app.modules.base_module.schemas.base import StrEnum


class ClientStatus(StrEnum):
    not_started: str = "notStarted", "Не начата"
    pre_investigation_check: str = "preInvestigationCheck", "Доследственная проверка"
    investigation: str = "investigation", "Предварительное следствие"
    first_instance: str = "firstInstance", "Суд первой инстанции"
    second_instance: str = "secondInstance", "Суд апеляционноц инстанции"
    third_instance: str = "thirdInstance", "Суд кассационной инстанции"
