from fastapi import APIRouter,HTTPException,Depends
from . import database,schema,models
import requests
from datetime import datetime

router = APIRouter()

def get_user_details(email: str):
    try:
        resp = requests.get(f"http://user_management:8000/users/{email}", timeout=5)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            return None
        else:
            raise HTTPException(status_code=resp.status_code, detail="User service error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error contacting user service: {e}")

@router.post("/order-tracking_helper")
def order_tracking_helper_function(data:schema.order_helper,db=Depends(database.get_db)):
    user_check = get_user_details(data.email)

    if not user_check:
        raise HTTPException(status_code=404, detail="User not found, use login email.")
    
    tracking_details_from_db = db.query(
        models.order_details.id,
        models.order_details.address,
        models.order_details.price,
        models.order_details.delivery_date
    ).filter(models.order_details.email==data.email).all()

    if not tracking_details_from_db:
        raise HTTPException(status_code=404, detail="Orders not found.")
    
    Processing_result = []
    Delivered_result = []
    
    for order in tracking_details_from_db:
        if order.delivery_date >= datetime.utcnow():
            status = "Processing / Will be delivered soon "
            Processing_result.append({
            "order_id": order.id,
            "delivery_date": order.delivery_date,
            "status": status
        })
        else:
            status =  "Delivered"
        
    return {"Processing Order ":Processing_result,"Delivered Order" : Delivered_result}