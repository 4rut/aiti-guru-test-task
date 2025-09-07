from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from core.db import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(BigInteger, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    parent = relationship("Category", remote_side=[id], backref="children")


class CategoryClosure(Base):
    __tablename__ = "category_closure"

    ancestor_id = Column(BigInteger, ForeignKey("categories.id"), primary_key=True, nullable=False)
    descendant_id = Column(BigInteger, ForeignKey("categories.id"), primary_key=True, nullable=False)
    depth = Column(Integer, nullable=False)
