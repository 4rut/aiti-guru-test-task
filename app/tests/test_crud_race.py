import threading
from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from crud.order_items import add_item_to_order
from models.product import Product


def test_race_two_orders_one_product(db: Session, seed):
    order1 = seed["o1_id"]
    order2 = seed["o2_id"]
    product = seed["p1_id"]

    p = db.get(Product, product)
    p.stock_qty = 5
    db.commit()

    engine = db.get_bind()
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

    start_barrier = threading.Barrier(2)

    out1, out2 = {}, {}

    def worker(order_id, qty, out_dict):
        with SessionLocal() as s:
            try:
                start_barrier.wait()
                new_qty, stock_left = add_item_to_order(
                    db=s, order_id=order_id, product_id=product, qty=qty
                )
                out_dict["ok"] = True
                out_dict["new_qty"] = new_qty
                out_dict["stock_left"] = stock_left
            except HTTPException as e:
                out_dict["ok"] = False
                out_dict["status"] = e.status_code
                out_dict["exc"] = str(e)

    t1 = threading.Thread(target=worker, args=(order1, 3, out1))
    t2 = threading.Thread(target=worker, args=(order2, 3, out2))
    t1.start(); t2.start()
    t1.join(); t2.join()

    oks = [out1.get("ok"), out2.get("ok")]
    assert oks.count(True) == 1 and oks.count(False) == 1

    loser = out1 if not out1["ok"] else out2
    assert loser["status"] == 409  # Not enough stock

    winner = out1 if out1["ok"] else out2
    assert winner["new_qty"] == 3
    assert winner["stock_left"] == 2  # 5 - 3
