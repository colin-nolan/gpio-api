from sqlalchemy import create_engine, Column, Integer, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from gpio_api import pins

Base = declarative_base()


class Output(Base):
    __tablename__ = "output"

    pin_id = Column(Integer, primary_key=True, nullable=False)
    state = Column(Boolean, nullable=False)


def initialise_output_pins(session: Session):
    outputs = session.query(Output).all()
    for output in outputs:
        pins.set_output_state(output.pin_id, output.state)


def record_output_state(session: Session, pin_id: int, state: bool):
    output = session.query(Output).get(pin_id)
    if output is None:
        output = Output(pin_id=pin_id, state=state)
        session.add(output)
    else:
        output.state = state
    session.commit()


def initialise_database(database_url: str) -> sessionmaker:
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
