from collections.abc import Iterable
import logging
from multiprocessing import Lock, Pipe, Process
from multiprocessing.connection import Connection
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from pydantic_settings import BaseSettings, SettingsConfigDict

from gpio_api import endpoints
from gpio_api.auth import basic_auth
from gpio_api.config import AppConfiguration, set_app_configuration
from gpio_api.pins.abstract import PinController
from gpio_api.pins.local import LocalPinController
from gpio_api.pins.recording import RecordingPinController
from gpio_api.pins.remote_thread import RemotePinController, pin_setter
from gpio_api.persistence.database import DbPinRecorder, initialise_database
from gpio_api.common import PinNumber

logger = logging.getLogger(__name__)
app: FastAPI


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GPIO_API_")
    username: str
    password: str
    database_url: str


def initialise_output_pins(
    pin_controller: PinController, pin_to_state_map: Iterable[tuple[PinNumber, bool]]
):
    for pin_number, state in pin_to_state_map.items():
        logger.info(f"Initialising output pin {pin_number} to {state}")
        pin_controller.set_output_state(pin_number, state)


def create_pin_recorder(database_url: str):
    session_maker = initialise_database(database_url)
    return DbPinRecorder(session_maker())


def start_remote_pin_controller(
    database_url: str,
) -> tuple[RemotePinController, Process]:
    pin_change_lock = Lock()
    consumer_connection, producer_connection = Pipe()

    remote_pin_setter_process = Process(
        target=start_pin_controller_process,
        args=(consumer_connection, database_url),
    )
    remote_pin_setter_process.start()

    return RemotePinController(
        producer_connection, pin_change_lock
    ), remote_pin_setter_process


def start_pin_controller_process(
    consumer_connection: Connection, database_url: str
) -> PinController:
    pin_recorder = create_pin_recorder(database_url)
    pin_controller = RecordingPinController(LocalPinController(), pin_recorder)

    while True:
        try:
            pin_setter(consumer_connection, pin_controller)
        except Exception as e:
            logger.exception(e)
            consumer_connection.send(e)


def start_app(settings: Settings, app_configuration: AppConfiguration):
    set_app_configuration(app_configuration)

    security = HTTPBasic()

    def basic_auth_dependency(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    ) -> str:
        return basic_auth(
            credentials,
            settings.username.encode("utf8"),
            settings.password.encode("utf8"),
        )

    global app
    app = FastAPI(dependencies=[Depends(security), Depends(basic_auth_dependency)])
    app.include_router(endpoints.router)


def main():
    logging.basicConfig(level=logging.DEBUG, force=True)

    settings = Settings()

    logger.info("Initialising database")
    initialise_database(settings.database_url)

    remote_pin_controller, process = start_remote_pin_controller(settings.database_url)

    logger.info("Initialising output pins")
    pin_recorder = create_pin_recorder(settings.database_url)
    initialise_output_pins(remote_pin_controller, pin_recorder.get_all_pin_states())

    app_configuration = AppConfiguration(remote_pin_controller)
    start_app(settings, app_configuration)

    # process.terminate()
    # process.join()
    # from time import sleep


# fastapi CLI does not excute the entrypoint if guarded with `if __name__ == "__main__"`
main()
