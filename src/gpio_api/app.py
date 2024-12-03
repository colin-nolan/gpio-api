import logging
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from pydantic_settings import BaseSettings, SettingsConfigDict

from gpio_api import endpoints
from gpio_api.auth import basic_auth
from gpio_api.config import AppConfiguration, set_app_configuration
from gpio_api.persistence import initialise_database, initialise_output_pins

logger = logging.getLogger(__name__)
app: FastAPI


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GPIO_API_")
    username: str
    password: str
    database_url: str | None = None


def main():
    settings = Settings()
    security = HTTPBasic()
    app_configuration = AppConfiguration()
    set_app_configuration(app_configuration)

    logging.basicConfig(level=logging.DEBUG, force=True)

    def basic_auth_dependency(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> str:
        return basic_auth(credentials, settings.username.encode("utf8"), settings.password.encode("utf8"))

    if settings.database_url:
        logger.info(f"Initialising database: {settings.database_url}")
        Session = initialise_database(settings.database_url)
        logger.info("Initialising output pins")
        initialise_output_pins(Session())
        app_configuration.database_session_maker = Session

    global app
    app = FastAPI(dependencies=[Depends(security), Depends(basic_auth_dependency)])
    app.include_router(endpoints.router)


# fastapi CLI does not excute the entrypoint if guarded with `if __name__ == "__main__"`
main()
