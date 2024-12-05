from abc import ABC, abstractmethod
from collections.abc import Iterable

from gpio_api.common import PinNumber


class PinRecorder(ABC):
    @abstractmethod
    def record_pin_state(self, pin_number: PinNumber, state: bool): ...

    @abstractmethod
    def get_pin_state(self, pin_number: PinNumber) -> bool: ...

    @abstractmethod
    def get_all_pin_states(self) -> Iterable[tuple[PinNumber, bool]]: ...
