import logging
from threading import Lock
from typing import Callable, Type, TypeAlias, TypeVar

from gpiozero import InputDevice, OutputDevice

logger = logging.getLogger(__name__)

PinNumber: TypeAlias = int
DeviceType = TypeVar("DeviceType", OutputDevice, InputDevice)

output_device_register: dict[PinNumber, OutputDevice] = {}
input_devices_register: dict[PinNumber, InputDevice] = {}
devices_register_lock = Lock()


class PinRegisterError(RuntimeError):
    def __init__(self, pin: PinNumber, pin_device_type: Type[DeviceType]):
        super().__init__(f"Pin {pin} is already registered as a {pin_device_type.__name__}")
        self.pin = pin
        self.pin_device_type = pin_device_type


def get_device(
    pin_number: PinNumber,
    device_register: dict[PinNumber, DeviceType],
    device_factory: Callable[[PinNumber], DeviceType],
) -> DeviceType:
    if pin_number in device_register:
        return device_register[pin_number]

    with devices_register_lock:
        if device_register == output_device_register and pin_number in input_devices_register:
            raise PinRegisterError(f"Pin {pin_number} is already registered as an input device")
        elif device_register == input_devices_register and pin_number in output_device_register:
            raise PinRegisterError(f"Pin {pin_number} is already registered as an output device")

        device = device_factory(pin_number)
        if isinstance(device, OutputDevice):
            # gpiozero offers no good way of stopping the state from being reset:
            # https://github.com/gpiozero/gpiozero/issues/707
            # This solution stops the close cleanup from running.
            device.close = lambda: None

        device_register[pin_number] = device

    return device


def get_output_device(callable: Callable) -> Callable:
    def wrapper(pin_number: int, *args, **kwargs) -> OutputDevice:
        device = get_device(pin_number, output_device_register, OutputDevice)
        return callable(device, *args, **kwargs)

    return wrapper


def get_input_device(callable: Callable) -> Callable:
    def wrapper(pin_number: int, *args, **kwargs) -> InputDevice:
        device = get_device(pin_number, input_devices_register, InputDevice)
        return callable(device, *args, **kwargs)

    return wrapper


@get_output_device
def read_output_state(device: OutputDevice) -> bool:
    return device.is_active


@get_output_device
def set_output_state(device: OutputDevice, state: bool):
    if state:
        device.on()
    else:
        device.off()


@get_input_device
def read_input_state(device: InputDevice) -> bool:
    return device.is_active
