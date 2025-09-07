from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.db import get_db
from crud import add_item_to_order
from schemas import AddItemIn, AddItemOut

router = APIRouter()


@router.post("/{order_id}/items", response_model=AddItemOut)
def add_item(order_id: int, payload: AddItemIn, db: Session = Depends(get_db)):
    new_qty, stock_left = add_item_to_order(
        db=db,
        order_id=order_id,
        product_id=payload.product_id,
        qty=payload.quantity,
    )
    return AddItemOut(
        order_id=order_id,
        product_id=payload.product_id,
        new_quantity_in_order=new_qty,
        stock_left=stock_left,
    )
