from sqlalchemy import text
from sqlalchemy.orm import Session

from models.order_item import OrderItem
from models.product import Product


def _create_top5_view(db: Session):
    sql = """
    create or replace view v_top5_products_last_month as
    with root_cat as (
      select
        cc.descendant_id as category_id,
        (array_agg(a.id order by cc.depth desc))[1] as root_id
      from category_closure cc
      join categories a on a.id = cc.ancestor_id
      where a.parent_id is null
      group by cc.descendant_id
    )
    select
      p.name as product_name,
      rc_root.name as category_lvl1,
      sum(oi.quantity) as total_qty
    from order_items oi
    join orders   o  on o.id = oi.order_id
    join products p  on p.id = oi.product_id
    left join root_cat rc     on rc.category_id = p.category_id
    left join categories rc_root on rc_root.id = rc.root_id
    where o.order_date >= (now() - interval '30 days')
    group by p.name, rc_root.name
    order by total_qty desc
    limit 5;
    """
    db.execute(text(sql))
    db.commit()


def test_reports(db: Session, seed):
    p1 = db.get(Product, seed["p1_id"])
    p2 = db.get(Product, seed["p2_id"])

    db.add_all([
        OrderItem(order_id=seed["o1_id"], product_id=p1.id, quantity=3, unit_price=p1.price),
        OrderItem(order_id=seed["o1_id"], product_id=p2.id, quantity=2, unit_price=p2.price),
        OrderItem(order_id=seed["o2_id"], product_id=p1.id, quantity=1, unit_price=p1.price),
        OrderItem(order_id=seed["o3_old_id"], product_id=p1.id, quantity=10, unit_price=p1.price),  # вне окна
    ])
    db.commit()

    res = db.execute(text("""
      select c.name as client_name, coalesce(sum(oi.quantity * oi.unit_price),0) as total_amount
      from clients c
      left join orders o on o.client_id = c.id
      left join order_items oi on oi.order_id = o.id
      group by c.name
      order by total_amount desc
    """)).mappings().all()

    acme = next(r for r in res if r["client_name"] == "ACME")
    assert float(acme["total_amount"]) == 3*999 + 2*699 + 9990

    globex = next(r for r in res if r["client_name"] == "Globex")
    assert float(globex["total_amount"]) == 1*999

    res2 = db.execute(text("""
      select p.id, p.name, count(c.id) as child_count_lvl1
      from categories p
      left join categories c on c.parent_id = p.id
      group by p.id, p.name
      order by child_count_lvl1 desc, p.name
    """)).mappings().all()
    root = next(r for r in res2 if r["name"] == "Электроника")
    assert root["child_count_lvl1"] == 1

    _create_top5_view(db)
    top = db.execute(text("select * from v_top5_products_last_month")).mappings().all()
    assert top[0]["product_name"] == "Phone X"
    assert top[0]["total_qty"] == 4
