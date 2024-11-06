import logging
from fastapi import FastAPI
from gpiozero import InputDevice, PinInvalidPin, OutputDevice, PinFixedPull
from fastapi import HTTPException
from http import HTTPStatus

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/pin/{pin_number}")
def read_pin(pin_number: int, pull_up: bool | None = False) -> bool:
    try:
        return read_pin(pin_number, pull_up)
    except PinInvalidPin:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pin not found")
    except PinFixedPull:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Pin has physical pull-up resistor so can only be read with pull_up set to true",
        )


@app.put("/pin/{pin_number}")
def write_pin(pin_number: int, state: bool):
    try:
        return write_pin(pin_number, state)
    except PinInvalidPin:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pin not found")


@app.get("/pins")
def write_one_pin(on_pin: int, off_pins: list[int]):
    try:
        for pin in off_pins:
            write_pin(pin, False)
        write_pin(on_pin, True)
    except PinInvalidPin:
        # TODO: which one!?
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pin not found")
