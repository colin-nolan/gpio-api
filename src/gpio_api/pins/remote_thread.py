from dataclasses import dataclass
from enum import Enum, auto, unique
import logging
from multiprocessing import Lock
from multiprocessing.connection import Connection

from gpio_api.pins.abstract import PinController
from gpio_api.common import PinNumber

logger = logging.getLogger(__name__)


@unique
class Operation(Enum):
    READ_OUTPUT = auto()
    SET_OUTPUT = auto()
    READ_INPUT = auto()


@dataclass
class Request:
    pin_number: PinNumber
    operation: Operation
    value: bool | None


@dataclass
class Response:
    value: bool | None = None
    error: bytes | None = None

    @property
    def is_error(self) -> bool:
        return self.error is not None


def _unpack_response(response: Response) -> bool:
    if response.is_error:
        raise response.error
    return response.value


class RemotePinController(PinController):
    def __init__(self, connection: Connection, lock: Lock):
        self._connection = connection
        self._lock = lock

    def read_input_state(self, pin_number: PinNumber) -> bool:
        with self._lock:
            self._connection.send(Request(pin_number, Operation.READ_INPUT, None))
            response = self._connection.recv()
            return _unpack_response(response)

    def read_output_state(self, pin_number: PinNumber) -> bool:
        with self._lock:
            self._connection.send(Request(pin_number, Operation.READ_OUTPUT, None))
            response = self._connection.recv()
            return _unpack_response(response)

    def set_output_state(self, pin_number: PinNumber, state: bool):
        with self._lock:
            self._connection.send(Request(pin_number, Operation.SET_OUTPUT, state))
            response = self._connection.recv()
            return _unpack_response(response)


def pin_setter(connection: Connection, pin_controller: PinController):
    while True:
        request: Request = connection.recv()
        logger.debug(
            f"Received {request.operation} for {request.pin_number} with value {request.value}"
        )

        try:
            match request.operation:
                case Operation.READ_INPUT:
                    response = Response(
                        value=pin_controller.read_input_state(request.pin_number)
                    )
                case Operation.READ_OUTPUT:
                    response = Response(
                        value=pin_controller.read_output_state(request.pin_number)
                    )
                case Operation.SET_OUTPUT:
                    response = Response(
                        value=pin_controller.set_output_state(
                            request.pin_number, request.value
                        )
                    )
                case _:
                    response = Response(
                        error=NotImplementedError,
                        error_args=(f"Operation not implemented: {request.operation}",),
                    )
        except Exception as e:
            response = Response(error=e)

        logger.debug(f"Responding: {response}")
        connection.send(response)
