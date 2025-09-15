from fastapi import APIRouter, Depends, HTTPException
from . import database, models, schema
import requests

router = APIRouter()

CHECKOUT_SERVICE_URL = "http://checkout:8000"

def get_order_cancel_status(order_id : int) -> dict | None:
    try:
        resp=requests.post(
            f"{CHECKOUT_SERVICE_URL}/order-cancel_hepler",
            json={"order_id":order_id},
            timeout=5
        )
        if resp.status_code ==200:
            return resp.json()
        elif resp.status_code == 404:
            return None
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Order tracking servies error"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comes in tracking service: {str(e)}"
        )

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

@router.post("/order-cancel")
def order_cancel_process(data : schema.order_cancel_process_schema, db = Depends(database.get_db)):
    user_check = get_user_details(data.email)
    if not user_check:
        raise HTTPException (status_code=404, detail="User not found, use login email.")
    
    cancel_request = get_order_cancel_status(data.order_id)
    if not cancel_request:
        raise HTTPException(status_code=404, detail="Order not found.")
    
    return cancel_request