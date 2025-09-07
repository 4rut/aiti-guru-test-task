from pydantic import BaseModel, Field, conint


class AddItemIn(BaseModel):
    product_id: conint(gt=0) = Field(..., description="Product ID")
    quantity: conint(gt=0) = Field(..., description="Quantity to add")


class AddItemOut(BaseModel):
    order_id: int
    product_id: int
    new_quantity_in_order: int
    stock_left: int
