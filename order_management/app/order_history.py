from fastapi import APIRouter, HTTPException,Depends
from . import database,schema
import requests

router = APIRouter()

CHECKOUT_SERVICE_URL = "http://checkout:8000"

def get_order_details(email : str) -> dict | None:
    try:
        resp=requests.post(
            f"{CHECKOUT_SERVICE_URL}/order-history",
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
                detail=f"Checkout servies error"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comes in cart service: {str(e)}"
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


@router.post("/order-history")
def user_order_history(data : schema.order_history_schema, db = Depends(database.get_db)):
    user_check = get_user_details(data.email)

    if not user_check:
        raise HTTPException(status_code=404,detail="Enter the user email to view order history.")
    
    order_detail_list = get_order_details(data.email)

    if not order_detail_list:
        raise HTTPException(status_code=404, detail="No order detail")
    
#     return [
#     {
#         "id": order["id"],
#         "email": order.email,
#         "items": order["items"],
#         "address": order["address"],
#         "payment_options": order["payment_options"],
#         "price": order["price"],
#         "discount_price": order["discount_price"],
#         "discount_type": order["discount_type"],
#         "created_at": order["created_at"],
#     }
#     for order in order_detail_list
# ]
    return order_detail_list