from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, func, text
from core.db import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True)
    client_id = Column(BigInteger, ForeignKey("clients.id"), nullable=False)
    order_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String(30), server_default=text("'created'"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
