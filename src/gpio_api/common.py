from http import HTTPStatus
from typing import Callable

from fastapi import HTTPException
from gpiozero import PinInvalidPin

from gpio_api.pins import PinRegisterError


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
