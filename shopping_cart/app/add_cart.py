from fastapi import APIRouter, HTTPException,Depends
from . import schema,models,database
import requests

router = APIRouter()

PRODUCT_SERVICE_URL = "http://product_catalog:8000"

def get_product_details(product_id: int) -> dict | None:
    try:
        resp = requests.post(
            f"{PRODUCT_SERVICE_URL}/by-product_id",
            json={"id": product_id},
            timeout=5
        )
        
        if resp.status_code == 200:
            return resp.json()  
        elif resp.status_code == 404:
            return None 
        else:
            raise HTTPException(
                status_code=resp.status_code,
                detail="Product service error"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comes in product service: {str(e)}"
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


    
@router.post("/add-cart_iteam")
def add_iteam_on_cart(data:schema.add_to_cart,db=Depends(database.get_db)):
    
    user_check = get_user_details(data.email)
    if not user_check:
        raise HTTPException(status_code=404, detail="User not found.")
    product_details = get_product_details(data.product_id)
    if not product_details:
        raise HTTPException(status_code=404, detail="Product Id not found.")
    
    if data.product_count ==0:
        raise HTTPException(status_code=400,detail="Minimum 1 count to add into cart.")
    
    new_cart = models.cart_list(
        email = data.email,
        product_id = product_details["id"],
        product_name = product_details["product_name"],
        product_price = product_details["product_price"],
        product_count = data.product_count
    )
    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)

    return {"Message":"Product added to cart.",
            "Product_name":f"{new_cart.product_name}."}