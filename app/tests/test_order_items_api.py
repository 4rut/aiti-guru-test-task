from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import status

from models.order_item import OrderItem
from models.product import Product


def test_add_item_success(client, db: Session, seed):
    order_id = seed["o1_id"]
    product_id = seed["p1_id"]

    resp = client.post(f"/orders/{order_id}/items", json={"product_id": product_id, "quantity": 3})
    assert resp.status_code == status.HTTP_200_OK, resp.text
    body = resp.json()
    assert body["order_id"] == order_id
    assert body["product_id"] == product_id
    assert body["new_quantity_in_order"] == 3
    assert body["stock_left"] == 97

    line = db.execute(
        select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.product_id == product_id)
    ).scalar_one()
    assert line.quantity == 3

    prod = db.get(Product, product_id)
    assert prod.stock_qty == 97


def test_add_item_upsert_increments(client, db: Session, seed):
    order_id = seed["o1_id"]
    product_id = seed["p1_id"]

    resp1 = client.post(f"/orders/{order_id}/items", json={"product_id": product_id, "quantity": 2})
    assert resp1.status_code == 200
    assert resp1.json()["new_quantity_in_order"] == 2

    resp2 = client.post(f"/orders/{order_id}/items", json={"product_id": product_id, "quantity": 5})
    assert resp2.status_code == 200
    assert resp2.json()["new_quantity_in_order"] == 7
    assert resp2.json()["stock_left"] == 93


def test_add_item_not_enough_stock(client, db: Session, seed):
    order_id = seed["o1_id"]
    product_id = seed["p2_id"]

    resp = client.post(f"/orders/{order_id}/items", json={"product_id": product_id, "quantity": 10_000})
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Not enough stock"


def test_add_item_404_order(client, db: Session, seed):
    product_id = seed["p1_id"]
    resp = client.post(f"/orders/999999/items", json={"product_id": product_id, "quantity": 1})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Order not found"


def test_add_item_404_product(client, db: Session, seed):
    order_id = seed["o1_id"]
    resp = client.post(f"/orders/{order_id}/items", json={"product_id": 999999, "quantity": 1})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Product not found"
