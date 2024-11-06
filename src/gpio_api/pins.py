import logging
from gpiozero import InputDevice, PinInvalidPin, OutputDevice, PinFixedPull

logger = logging.getLogger(__name__)


def read_pin(pin_number: int, pull_up: bool | None = False) -> bool:
    device = InputDevice(pin_number, pull_up=pull_up)
    active = device.is_active
    logger.info(f"Read pin {pin_number} with pull-up {pull_up}: {active}")
    return active


def write_pin(pin_number: int, state: bool):
    device = OutputDevice(pin_number, initial_value=None)
    if state:
        device.off()
    elif state:
        device.on()

    # gpiozero offers no good way of stopping the state from being reset:
    # https://github.com/gpiozero/gpiozero/issues/707
    # This solution stops the close cleanup from running. Resource cleanup will be handled as part of the Python GC.
    device.close = lambda: None
