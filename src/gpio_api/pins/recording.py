from gpio_api.persistence.abstract import PinRecorder
from gpio_api.pins.abstract import PinController
from gpio_api.common import PinNumber


class RecordingPinController(PinController):
    def __init__(
        self,
        pin_controller: PinController,
        pin_recorder: PinRecorder,
    ):
        self._pin_controller = pin_controller
        self._pin_recorder = pin_recorder

    def read_input_state(self, pin_number: PinNumber) -> bool:
        return self._pin_controller.read_input_state(pin_number)

    def read_output_state(self, pin_number: PinNumber) -> bool:
        return self._pin_controller.read_output_state(pin_number)

    def set_output_state(self, pin_number: PinNumber, state: bool):
        self._pin_controller.set_output_state(pin_number, state)
        self._pin_recorder.record_pin_state(pin_number, state)
