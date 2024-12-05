from dataclasses import dataclass

from gpio_api.pins.abstract import PinController

# FastAPI does not have a good mechanism for passing configuration to the application so resorting to a global...
_APP_CONFIGURATION: "AppConfiguration"


@dataclass
class AppConfiguration:
    pin_controller: PinController


def app_configuration() -> AppConfiguration:
    return _APP_CONFIGURATION


def set_app_configuration(configuration: AppConfiguration):
    global _APP_CONFIGURATION
    _APP_CONFIGURATION = configuration
