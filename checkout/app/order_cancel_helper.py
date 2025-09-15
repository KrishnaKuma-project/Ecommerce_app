from fastapi import APIRouter, Depends, HTTPException
from . import database, models, schema
from datetime import datetime
import requests

router = APIRouter()

@router.post("/order-cancel_hepler")
def order_cancel_helper_process(
    data:schema.order_cancel_helper_process_schema,
    db = Depends(database.get_db)
):
    order_check = db.query(models.order_details).filter(
        models.order_details.id == data.order_id
    ).first()
    if not order_check:
        raise HTTPException(status_code=404, detail="Order ID not found.")
    
    if order_check.delivery_date <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Given order Id is not eligible for cancelation.")
    
    db.delete(order_check)
    db.commit()


    return {"Message":"Your order canceled."}