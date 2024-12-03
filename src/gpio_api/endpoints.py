from typing import Annotated

from fastapi import APIRouter, Query, Depends

from gpio_api import pins
from gpio_api.common import handle_common_exceptions
from gpio_api.config import AppConfiguration, app_configuration
from gpio_api.persistence import record_output_state
from gpio_api.pins import PinNumber


router = APIRouter()


@handle_common_exceptions
@router.get("/input/{pin_number}")
async def read_input_state(pin_number: int) -> bool:
    return pins.read_input_state(pin_number)


@handle_common_exceptions
@router.get("/output/{pin_number}")
async def read_output_state(pin_number: int) -> bool:
    return pins.read_output_state(pin_number)


@handle_common_exceptions
@router.put("/output/{pin_number}")
async def set_output_state(
    pin_number: PinNumber, state: bool, configuration: Annotated[AppConfiguration, Depends(app_configuration)]
):
    pins.set_output_state(pin_number, state)
    record_output_state(configuration.create_database_session(), pin_number, state)


@handle_common_exceptions
@router.put("/outputs/")
async def set_multiple_output_states(
    configuration: Annotated[AppConfiguration, Depends(app_configuration)],
    on_pins: Annotated[list[PinNumber], Query()] = [],
    off_pins: Annotated[list[PinNumber], Query()] = [],
):
    # Turn on after turning off to avoid potential overvoltages on combined outputs
    pin_state_pairs = [(pin, False) for pin in off_pins] + [(pin, True) for pin in on_pins]

    for pin_number, state in pin_state_pairs:
        pins.set_output_state(pin_number, state)
        record_output_state(configuration.create_database_session(), pin_number, state)
