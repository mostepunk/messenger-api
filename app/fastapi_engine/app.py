from app.fastapi_engine.constructor import get_fastapi_app
from app.utils.setup_modules import attach_modules_to_app

fastapi_app = get_fastapi_app()
attach_modules_to_app(fastapi_app)
