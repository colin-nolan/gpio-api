from abc import ABC, abstractmethod
from gpio_api.common import PinNumber


class PinController(ABC):
    @abstractmethod
    def read_input_state(self, pin_number: PinNumber) -> bool: ...

    @abstractmethod
    def read_output_state(self, pin_number: PinNumber) -> bool: ...

    @abstractmethod
    def set_output_state(self, pin_number: PinNumber, state: bool): ...
