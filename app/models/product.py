from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Numeric, String, func
from core.db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    stock_qty = Column(Integer, nullable=False, server_default="0")
    category_id = Column(BigInteger, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
