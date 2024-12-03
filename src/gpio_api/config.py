from dataclasses import dataclass
from sqlalchemy.orm import sessionmaker

# FastAPI does not have a good mechanism for passing configuration to the application so resorting to a global...
_APP_CONFIGURATION: "AppConfiguration"


@dataclass
class AppConfiguration:
    database_session_maker: sessionmaker | None = None

    def create_database_session(self):
        return self.database_session_maker()


def app_configuration() -> AppConfiguration | None:
    return _APP_CONFIGURATION


def set_app_configuration(configuration: AppConfiguration):
    global _APP_CONFIGURATION
    _APP_CONFIGURATION = configuration
