# -*- coding: utf-8 -*-
# Global fixtures: test engine/session, app client, clean schema & seed data.

import os
import datetime as dt
import threading
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from core.db import Base, get_db
from app import app  # FastAPI app
import models  # noqa: F401  # ensure models metadata is imported

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+psycopg2://shop:shop@db:5432/shop")

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True, future=True)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


@pytest.fixture(scope="function")
def db() -> Session:
    """Clean schema each test and provide a DB session."""
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP VIEW IF EXISTS v_top5_products_last_month CASCADE;")
        conn.exec_driver_sql("DROP MATERIALIZED VIEW IF EXISTS v_top5_products_last_month CASCADE;")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db: Session) -> TestClient:
    """FastAPI TestClient with overridden DB dependency."""

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    c = TestClient(app)
    try:
        yield c
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seed(db: Session) -> Dict[str, int]:
    """Minimal seed: categories/closure, products, clients, orders."""
    from models.category import Category, CategoryClosure
    from models.product import Product
    from models.client import Client
    from models.order import Order

    # Root category
    root = Category(name="Электроника", parent_id=None)
    db.add(root)
    db.flush()

    # Child category
    phones = Category(name="Смартфоны", parent_id=root.id)
    db.add(phones)
    db.flush()

    # Closure
    db.add_all([
        CategoryClosure(ancestor_id=root.id, descendant_id=root.id, depth=0),
        CategoryClosure(ancestor_id=phones.id, descendant_id=phones.id, depth=0),
        CategoryClosure(ancestor_id=root.id, descendant_id=phones.id, depth=1),
    ])

    # Products
    p1 = Product(name="Phone X", price=999.00, stock_qty=100, category_id=phones.id)
    p2 = Product(name="Phone Y", price=699.00, stock_qty=50, category_id=phones.id)
    db.add_all([p1, p2])

    # Clients
    c1 = Client(name="ACME", address="Main St")
    c2 = Client(name="Globex", address="2nd St")
    db.add_all([c1, c2])
    db.flush()

    # Orders
    o1 = Order(client_id=c1.id)  # now
    o2 = Order(client_id=c2.id, order_date=dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=10))
    o3_old = Order(client_id=c1.id, order_date=dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=45))  # вне окна 30д
    db.add_all([o1, o2, o3_old])
    db.commit()

    return {
        "root_id": root.id,
        "phones_id": phones.id,
        "p1_id": p1.id,
        "p2_id": p2.id,
        "c1_id": c1.id,
        "c2_id": c2.id,
        "o1_id": o1.id,
        "o2_id": o2.id,
        "o3_old_id": o3_old.id,
    }


# Утилита для конкурентных вызовов CRUD
class ThreadResult:
    def __init__(self):
        self.ok = False
        self.status = None
        self.exc = None
        self.new_qty = None
        self.stock_left = None
        self.lock = threading.Lock()

    def set_ok(self, new_qty, stock_left):
        with self.lock:
            self.ok = True
            self.new_qty = new_qty
            self.stock_left = stock_left

    def set_err(self, status, exc):
        with self.lock:
            self.ok = False
            self.status = status
            self.exc = exc
