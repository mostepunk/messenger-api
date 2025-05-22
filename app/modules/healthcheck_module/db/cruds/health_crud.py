from sqlalchemy import text


class HealthCRUD:
    def __init__(self, session):
        self.session = session

    async def check_connect(self):
        q = text("SELECT * FROM user")
        res = await self.session.execute(q)
        return res.scalar()
