from fastapi import APIRouter, Depends, HTTPException
from . import schema, main, database
import requests

router = APIRouter()

CHECKOUT_SERVICE_URL = "http://checkout:8000"

def get_order_status(email : str) -> dict | None:
    try:
        resp=requests.post(
            f"{CHECKOUT_SERVICE_URL}/order-tracking_helper",
            json={"email":email},
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

@router.post("/order-tracking")
def order_tracking_process (
    data : schema.order_tracking_process_schema,
    db = Depends(database.get_db)
):
    order_detail_list = get_order_status(data.email)
    if not order_detail_list:
        raise HTTPException (status_code=404, detail="Order details not found.")
    
    return order_detail_list