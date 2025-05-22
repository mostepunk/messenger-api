import uvicorn

from app.settings import config


def start_server():
    uvicorn.run("app.fastapi_engine.app:fastapi_app", **config.app.server_settings)


if __name__ == "__main__":
    start_server()
