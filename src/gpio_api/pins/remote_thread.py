from enum import Enum, auto, unique
import logging
from multiprocessing import Lock
from multiprocessing.connection import Connection

from gpio_api.pins.abstract import PinController
from gpio_api.common import PinNumber

logger = logging.getLogger(__name__)


class RemotePinController(PinController):
    def __init__(self, connection: Connection, lock: Lock):
        self._connection = connection
        self._lock = lock

    def read_output_state(self, pin_number: PinNumber) -> bool:
        with self._lock:
            self._connection.send((pin_number, Operation.READ_INPUT, None))
            return self._connection.recv()

    def set_output_state(self, pin_number: PinNumber, state: bool):
        with self._lock:
            self._connection.send((pin_number, Operation.SET_OUTPUT, state))
            self._connection.recv()

    def read_input_state(self, pin_number: PinNumber) -> bool:
        with self._lock:
            self._connection.send((pin_number, Operation.READ_INPUT, None))
            return self._connection.recv()


@unique
class Operation(Enum):
    READ_OUTPUT = auto()
    SET_OUTPUT = auto()
    READ_INPUT = auto()


def pin_setter(connection: Connection, pin_controller: PinController):
    while True:
        pin_number, operation, value = connection.recv()
        logger.info(f"Received {operation} for {pin_number} with value {value}")

        match operation:
            case Operation.READ_INPUT:
                rv = pin_controller.read_input_state(pin_number)
            case Operation.READ_OUTPUT:
                rv = pin_controller.read_output_state(pin_number)
            case Operation.SET_OUTPUT:
                rv = pin_controller.set_output_state(pin_number, value)
            case _:
                raise NotImplementedError(f"Operation not implemented: {operation}")

        connection.send(rv)
