from fastapi import FastAPI
from contextlib import asynccontextmanager

from routers.order_items import router as order_items_router
from utils.init_db import create_schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_schema()
    yield


app = FastAPI(
    title="Orders API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(order_items_router, prefix="/orders", tags=["order-items"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
