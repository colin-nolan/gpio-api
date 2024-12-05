import logging
from threading import Lock
from typing import Callable, Type, TypeVar
from gpiozero import InputDevice, OutputDevice

from gpio_api.pins.abstract import PinController
from gpio_api.common import PinNumber

logger = logging.getLogger(__name__)

DeviceType = TypeVar("DeviceType", OutputDevice, InputDevice)

_OUTPUT_DEVICE_REGISTER: dict[PinNumber, OutputDevice] = {}
_INPUT_DEVICES_REGISTER: dict[PinNumber, InputDevice] = {}
_DEVICES_REGISTER_LOCK = Lock()


def _get_output_device(callable: Callable) -> Callable:
    def wrapper(self, pin_number: int, *args, **kwargs) -> OutputDevice:
        device = _get_device(pin_number, _OUTPUT_DEVICE_REGISTER, OutputDevice)
        return callable(self, device, *args, **kwargs)

    return wrapper


def _get_input_device(callable: Callable) -> Callable:
    def wrapper(self, pin_number: int, *args, **kwargs) -> InputDevice:
        device = _get_device(pin_number, _INPUT_DEVICES_REGISTER, InputDevice)
        return callable(self, device, *args, **kwargs)

    return wrapper


class LocalPinController(PinController):
    @_get_output_device
    def read_output_state(self, device: OutputDevice) -> bool:
        return device.is_active

    @_get_output_device
    def set_output_state(self, device: OutputDevice, state: bool):
        if state:
            device.on()
        else:
            device.off()

    @_get_input_device
    def read_input_state(self, device: InputDevice) -> bool:
        return device.is_active


class PinRegisterError(RuntimeError):
    def __init__(self, pin_number: PinNumber, pin_device_type: Type[DeviceType]):
        super().__init__(
            f"Pin {pin_number} is already registered as a {pin_device_type.__name__}"
        )
        self.pin_number = pin_number
        self.pin_device_type = pin_device_type


def _get_device(
    pin_number: PinNumber,
    device_register: dict[PinNumber, DeviceType],
    device_factory: Callable[[PinNumber], DeviceType],
) -> DeviceType:
    if pin_number in device_register:
        return device_register[pin_number]

    with _DEVICES_REGISTER_LOCK:
        # XXX: It would be better if the purpose of a pin could be converted, or they were treated more agnostically
        if (
            device_register == _OUTPUT_DEVICE_REGISTER
            and pin_number in _INPUT_DEVICES_REGISTER
        ):
            raise PinRegisterError(pin_number, InputDevice)
        elif (
            device_register == _INPUT_DEVICES_REGISTER
            and pin_number in _OUTPUT_DEVICE_REGISTER
        ):
            raise PinRegisterError(pin_number, OutputDevice)

        device = device_factory(pin_number)
        if isinstance(device, OutputDevice):
            # gpiozero offers no good way of stopping the state from being reset:
            # https://github.com/gpiozero/gpiozero/issues/707
            # This solution stops the close cleanup from running.
            device.close = lambda: None

        device_register[pin_number] = device

    return device
