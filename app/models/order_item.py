from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Numeric, PrimaryKeyConstraint, func
from core.db import Base


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        PrimaryKeyConstraint("order_id", "product_id", name="pk_order_items"),
    )

    order_id = Column(BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
