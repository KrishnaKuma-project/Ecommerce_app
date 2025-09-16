from fastapi import FastAPI
from . import admin_Dashboard, user_block_unblock,database,product_management

app=FastAPI()
app.include_router(admin_Dashboard.router,tags=["Admin Dashboard."])
app.include_router(user_block_unblock.router, tags=["Block & Unblock User"])
app.include_router(product_management.router, tags=["All user list."])

@app.on_event("startup")
def startup():
    database.Base.metadata.create_all(bind=database.engine)

@app.get("/")
def summa ():
    return {"Message":"admin panel working"}