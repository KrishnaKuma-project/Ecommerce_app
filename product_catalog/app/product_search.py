from fastapi import APIRouter, Depends, HTTPException
from . import database, models, schema
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/see-all-product",response_model=list[schema.show_product])
def see_all_product_process(db=Depends(database.get_db)):
    all_product_list = db.query(models.product_table).all()
    return all_product_list

@router.post("/by-product_name",response_model=list[schema.show_product])
def search_by_name (data:schema.show_product_by_name, db=Depends(database.get_db)):
    product_detail = db.query(models.product_table).filter(models.product_table.product_name==data.product_name)
     
    if not product_detail:
        raise HTTPException(status_code=404, detail="Product name not found.")
    
    return product_detail

@router.post("/by-product_id",response_model=schema.show_product)
def search_by_id (data:schema.show_product_by_id,db=Depends(database.get_db)):
    product_detail = db.query(models.product_table).filter(models.product_table.id==data.id).first()

    if not product_detail:
        raise HTTPException(status_code=404, detail="Product id not found in the database.")
    
    return product_detail

@router.post("/by-product_category",response_model=list[schema.show_product])
def search_by_category(data:schema.show_product_by_categorie,db=Depends(database.get_db)):
    product_details = db.query(models.product_table).filter(models.product_table.product_categorie==data.product_categorie).all()

    if not product_details:
        raise HTTPException(status_code=404,detail=f"No product in the {data.product_categorie}.")
    
    return product_details

@router.post("/by-product_price",response_model=list[schema.show_product])
def search_by_price(data:schema.show_product_by_price,db=Depends(database.get_db)):
    product_details = db.query(models.product_table).filter(
        models.product_table.product_price==data.product_price
    ).all()

    if not product_details:
        raise HTTPException(status_code=404, detail=f"No product on the {data.product_price}")
    
    return product_details