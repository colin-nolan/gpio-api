import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from gpiozero import PinInvalidPin

from gpio_api import pins
from gpio_api.pins import PinNumber

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/output/{pin_number}")
async def read_output_state(pin_number: int) -> bool:
    try:
        return pins.read_output_state(pin_number)
    except PinInvalidPin:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pin not found")


@app.put("/output/{pin_number}")
async def set_output_state(pin_number: PinNumber, state: bool):
    try:
        return pins.set_output_state(pin_number, state)
    except PinInvalidPin:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pin not found")


@app.put("/outputs/")
async def set_multiple_output_states(
    on_pins: Annotated[list[PinNumber], Query()] = [], off_pins: Annotated[list[PinNumber], Query()] = []
):
    # Turn on after turning off to avoid potential overvoltages on combined outputs
    pin_state_pairs = [(pin, False) for pin in off_pins] + [(pin, True) for pin in on_pins]

    for pin, state in pin_state_pairs:
        try:
            pins.set_output_state(pin, state)
        except PinInvalidPin:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Pin not found: {pin}")
