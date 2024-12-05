from collections.abc import Iterable
from sqlalchemy import Column, Integer, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import logging

from gpio_api.common import PinNumber
from gpio_api.persistence.abstract import PinRecorder

Base = declarative_base()

logger = logging.getLogger(__name__)


class Output(Base):
    __tablename__ = "output"

    pin_id = Column(Integer, primary_key=True, nullable=False)
    state = Column(Boolean, nullable=False)


class DbPinRecorder(PinRecorder):
    def __init__(self, session: Session):
        self._session = session

    def record_pin_state(self, pin_number: PinNumber, state: bool):
        output = self._session.query(Output).get(pin_number)
        if output is None:
            output = Output(pin_id=pin_number, state=state)
            self._session.add(output)
        else:
            output.state = state
        self._session.commit()

    def get_pin_state(self, pin_number: PinNumber) -> bool:
        return self._session.query(Output).get(pin_number).state

    def get_all_pin_states(self) -> Iterable[tuple[PinNumber, bool]]:
        outputs = self._session.query(Output).all()
        return {output.pin_id: output.state for output in outputs}


def initialise_database(database_url: str) -> sessionmaker:
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
