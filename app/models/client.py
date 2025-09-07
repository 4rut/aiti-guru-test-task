from sqlalchemy import BigInteger, Column, DateTime, String, func, Text
from core.db import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
