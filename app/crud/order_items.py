from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from models.order import Order
from models.product import Product
from models.order_item import OrderItem


def add_item_to_order(db: Session, order_id: int, product_id: int, qty: int) -> tuple[int, int]:
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    prod = db.execute(
        select(Product).where(Product.id == product_id).with_for_update()
    ).scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    if prod.stock_qty < qty:
        raise HTTPException(status_code=409, detail="Not enough stock")

    stmt = (
        pg_insert(OrderItem)
        .values(order_id=order_id, product_id=product_id, quantity=qty, unit_price=prod.price)
        .on_conflict_do_update(
            index_elements=[OrderItem.order_id, OrderItem.product_id],
            set_={"quantity": OrderItem.quantity + qty}
        )
        .returning(OrderItem.quantity)
    )
    new_qty = db.execute(stmt).scalar_one()

    prod.stock_qty = prod.stock_qty - qty

    db.commit()
    db.refresh(prod)
    return new_qty, prod.stock_qty
