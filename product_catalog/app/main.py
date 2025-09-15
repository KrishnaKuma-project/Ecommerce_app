from fastapi import FastAPI
from . import product_adding,models, database, product_search, product_remove

app = FastAPI()

@app.on_event("startup")
def startup():
    models.Base.metadata.create_all(bind=database.engine)

app.include_router(product_adding.router,tags=["Add Product From Database"])
app.include_router(product_remove.router,tags=["Remove Product From Database"])
app.include_router(product_search.router, tags=["Search Products "])

