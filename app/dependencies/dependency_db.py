from __future__ import unicode_literals

import logging

from app.adapters.db import ASYNC_SESSION, SYNC_SESSION


async def get_async_db():
    session = ASYNC_SESSION()
    try:
        yield session
    except Exception as err:
        logging.error(f"[DATABASE ERROR]: {err}")
        session.rollback()
        raise
    finally:
        await session.close()


def get_sync_db():
    session = SYNC_SESSION()
    try:
        yield session
    except Exception as err:
        logging.error(f"[DATABASE ERROR]: {err}")
        session.rollback()
        raise
    finally:
        session.close()


async def get_session() -> ASYNC_SESSION:
    async with ASYNC_SESSION() as session:
        try:
            logging.debug("[DATABASE]: Session opened")
            yield session
        except Exception as err:
            # logging.exception(f"[DATABASE].Exception: {err}. Do rollback")
            logging.warning(f"[DATABASE].Exception: {err}. Do rollback")
            await session.rollback()
            raise
        finally:
            logging.debug("[DATABASE]: Session closed")
            await session.close()
