from fastapi import APIRouter,HTTPException,Depends
from . import database,models,schema
import requests

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

@router.post("/add-product")
def add_product_process (data:schema.add_product,db=Depends(database.get_db)):
    check_user = get_user_details(data.email)

    if not check_user :
        raise HTTPException(status_code=404, detail="Email ID not found in database, use your login email.")
    
    if check_user["user_type"] !="admin":
        raise HTTPException(status_code=401,detail="Only admin can add product.")
    
    new_product = models.product_table(
        product_name=data.product_name,
        product_description=data.product_description,
        product_categorie=data.product_categorie,
        product_price=data.product_price,
        product_sku=data.product_sku,
        product_specifications=data.product_specifications
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product added successfully",
        "product_id": new_product.id,
        "product_name": new_product.product_name
    }