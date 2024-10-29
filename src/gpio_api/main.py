import logging
from fastapi import FastAPI
from gpiozero import InputDevice, PinInvalidPin, OutputDevice, PinFixedPull
from fastapi import HTTPException
from http import HTTPStatus

import uvicorn

logger = logging.getLogger(__name__)

app = FastAPI()



@app.get("/pin/{pin_number}")
def read_pin(pin_number: int, pull_up: bool | None = False) -> bool:
    try:
        device = InputDevice(pin_number, pull_up=pull_up)
    except PinInvalidPin:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pin not found")
    except PinFixedPull:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Pin has physical pull-up resistor so can only be read with pull_up set to true",
        )
    active = device.is_active
    logger.info(f"Read pin {pin_number} with pull-up {pull_up}: {active}")
    return active


@app.put("/pin/{pin_number}")
def write_pin(pin_number: int, state: bool):
    try:
        device = OutputDevice(pin_number, initial_value=None)
    except PinInvalidPin:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pin not found")
    if state:
        device.off()
    elif state:
        device.on()

    # gpiozero offers no good way of stopping the state from being reset:
    # https://github.com/gpiozero/gpiozero/issues/707
    # This solution stops the close cleanup from running. Resource cleanup will be handled as part of the Python GC.
    device.close = lambda: None
