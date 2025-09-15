from fastapi import FastAPI, HTTPException
from . import add_cart,database,show_cart,remove_cart

app = FastAPI()
@app.on_event("startup")
def startup():
    database.Base.metadata.create_all(bind=database.engine)

app.include_router(show_cart.router,tags=["Show cart."])
app.include_router(add_cart.router,tags=["Add and Remove iteam in cart."])
app.include_router(remove_cart.router,tags=["Remove item from cart."])
