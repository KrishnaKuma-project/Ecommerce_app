from fastapi import FastAPI
from . import order_history,Order_tracking, order_cancel

app = FastAPI()

app.include_router(order_history.router,tags=["Order History"])
app.include_router(Order_tracking.router, tags=["Order Tracking"])
app.include_router(order_cancel.router, tags=["Order Cancel."])