from fastapi import FastAPI, HTTPException,Depends
from . import database, schema, models, order_tracking_helper, order_cancel_helper
import requests

app = FastAPI()

app.include_router(order_tracking_helper.router,tags=["Order tracker."])
app.include_router(order_cancel_helper.router,tags=["Order Cancel."])

@app.on_event("startup")
def startup():
    database.Base.metadata.create_all(bind=database.engine)

CART_SERVICE_URL = "http://shopping_cart:8000"

def remove_cart_after_order(
        email: str,
        db=Depends(database.get_db)
)-> dict | None:
    try :
        resp=requests.post(
            f"{CART_SERVICE_URL}/remove-all_cart_item",
            json = {"email":email},
            timeout=5
        )
        if resp.status_code==200:
            return  resp.json()
        elif resp.status_code == 400:
            return None
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Cart servies error"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comes in cart service: {str(e)}"
        )


def get_cart_items(email : str) -> dict | None:
    try:
        resp=requests.post(
            f"{CART_SERVICE_URL}/show-cart",
            json={"email":email},
            timeout=5
        )
        if resp.status_code ==200:
            return resp.json()
        elif resp.status_code == 400:
            return None
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Cart servies error"
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

    
@app.post("/order-confirmation")
def order_confirmartion (data:schema.order_process, db =Depends(database.get_db)):
    get_user_from_db = get_user_details(data.email)
    
    if not get_user_from_db:
        raise HTTPException(status_code=404,detail="User not found.")
    
    get_cart_items_for_order = get_cart_items(data.email)

    if not get_cart_items_for_order:
        raise HTTPException (status_code=404, detail="Your cart is empty.")
    
    payment_options_active = ["cash on delivery"]
    if not data.payment_options.lower() in payment_options_active:
        raise HTTPException(status_code=404, detail="Only cash on delivery payment options are allowed.")

    discount_codes_list = ["SK05","NEW10"]
    if not data.discount_code == "string":
        if not data.discount_code.upper() in discount_codes_list:
            raise HTTPException(status_code=404, detail="Wrong discount code")
    
    discount_amount = 0
    if data.discount_code.upper()=="SK05":
        discount_amount = round(get_cart_items_for_order["total_price"]*0.05,2) #discount amount calculation

    if data.discount_code.upper()=="NEW10":
        discount_amount = round(get_cart_items_for_order["total_price"]*0.10,2)

    total_amount_after_discount = get_cart_items_for_order["total_price"] - discount_amount

    new_order = models.order_details(
        email = data.email,
        items = get_cart_items_for_order["cart_items"],
        address = data.address,
        payment_options = data.payment_options,
        price = total_amount_after_discount,
        discount_price=discount_amount,
        discount_type = data.discount_code
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    cart_remove_check = remove_cart_after_order(data.email)
    print("CART RESPONSE:", get_cart_items_for_order)

    return {"Message":"Order Confirmed."}

@app.post("/order-history")
def order_history_to_order_management(data:schema.order_history,db=Depends(database.get_db)):
    user_check = get_user_details(data.email)
    
    if not user_check:
        raise HTTPException(status_code=404, detail="User not found.")

    get_all_orders = db.query(models.order_details).filter(models.order_details.email == data.email).all()

    if not get_all_orders:
        raise HTTPException(status_code=404, detail="No orders found.")
    
    return [
        {
            "id": order.id,
            "items": order.items,
            "address": order.address,
            "payment_options": order.payment_options,
            "discount_price": order.discount_price,
            "discount_type": order.discount_type,
            "price": order.price,
            "delivery_date": order.delivery_date,
        }
        for order in get_all_orders
    ]