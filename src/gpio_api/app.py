import logging
from http import HTTPStatus
from typing import Annotated, Callable

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from gpiozero import PinInvalidPin
from pydantic_settings import BaseSettings, SettingsConfigDict

from gpio_api import pins
from gpio_api.pins import PinNumber, PinRegisterError

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='GPIO_API_')
    username: str
    password: str


settings = Settings()
security = HTTPBasic()


def basic_auth(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    print(settings.username, settings.password)

app = FastAPI(dependencies=[Depends(security), Depends(basic_auth)])



def handle_common_exceptions(callable: Callable):
    def wrapper(*args, **kwargs):
        try:
            return callable(*args, **kwargs)
        except PinInvalidPin as e:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pin not found") from e
        except PinRegisterError as e:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=f"Pin {e.pin} is already registered as a {e.pin_device_type.__name__}",
            )

    return wrapper


@handle_common_exceptions
@app.get("/input/{pin_number}")
async def read_input_state(pin_number: int) -> bool:
    return pins.read_input_state(pin_number)


@handle_common_exceptions
@app.get("/output/{pin_number}")
async def read_output_state(pin_number: int) -> bool:
    return pins.read_output_state(pin_number)


@handle_common_exceptions
@app.put("/output/{pin_number}")
async def set_output_state(pin_number: PinNumber, state: bool):
    return pins.set_output_state(pin_number, state)


@handle_common_exceptions
@app.put("/outputs/")
async def set_multiple_output_states(
    on_pins: Annotated[list[PinNumber], Query()] = [], off_pins: Annotated[list[PinNumber], Query()] = []
):
    # Turn on after turning off to avoid potential overvoltages on combined outputs
    pin_state_pairs = [(pin, False) for pin in off_pins] + [(pin, True) for pin in on_pins]

    for pin, state in pin_state_pairs:
        pins.set_output_state(pin, state)
