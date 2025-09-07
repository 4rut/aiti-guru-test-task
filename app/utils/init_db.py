from core.db import Base, engine
import models  # noqa: F401


def create_schema():
    Base.metadata.create_all(bind=engine)
