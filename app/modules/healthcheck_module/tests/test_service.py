import pytest
from sqlalchemy.exc import OperationalError


class TestCheckhealtchService:

    async def test_health_ok(self, health_service):
        await health_service.check_health()

    async def test_health_raises_db_error(self, incorrect_health_service):
        with pytest.raises(OperationalError) as err:
            await incorrect_health_service.check_health()
        assert 'database "database_not_exist__testing" does not exist' in str(err.value)
