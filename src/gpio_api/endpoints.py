from collections.abc import Callable
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Depends

from gpio_api.config import AppConfiguration, app_configuration
from gpio_api.pins.local import PinRegisterError
from gpio_api.pins.remote_thread import PinNumber
from gpiozero import PinInvalidPin

router = APIRouter()


def _handle_common_exceptions(callable: Callable):
    def wrapper(*args, **kwargs):
        try:
            return callable(*args, **kwargs)
        except PinInvalidPin as e:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="Pin not found"
            ) from e
        except PinRegisterError as e:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=f"Pin {e.pin_number} is already registered as a {e.pin_device_type.__name__}",
            )

    return wrapper


@_handle_common_exceptions
@router.get("/input/{pin_number}")
async def read_input_state(
    configuration: Annotated[AppConfiguration, Depends(app_configuration)],
    pin_number: int,
) -> bool:
    return configuration.pin_controller.read_input_state(pin_number)


@_handle_common_exceptions
@router.get("/output/{pin_number}")
async def read_output_state(
    configuration: Annotated[AppConfiguration, Depends(app_configuration)],
    pin_number: int,
) -> bool:
    return configuration.pin_controller.read_output_state(pin_number)


@_handle_common_exceptions
@router.put("/output/{pin_number}")
async def set_output_state(
    configuration: Annotated[AppConfiguration, Depends(app_configuration)],
    pin_number: PinNumber,
    state: bool,
):
    configuration.pin_controller.set_output_state(pin_number, state)


@_handle_common_exceptions
@router.put("/outputs/")
async def set_multiple_output_states(
    configuration: Annotated[AppConfiguration, Depends(app_configuration)],
    on_pins: Annotated[list[PinNumber], Query()] = [],
    off_pins: Annotated[list[PinNumber], Query()] = [],
):
    # Turn on after turning off to avoid potential overvoltages on combined outputs
    pin_state_pairs = [(pin, False) for pin in off_pins] + [
        (pin, True) for pin in on_pins
    ]

    for pin_number, state in pin_state_pairs:
        configuration.pin_controller.set_output_state(pin_number, state)
