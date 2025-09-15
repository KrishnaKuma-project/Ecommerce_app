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

@router.post ("/remove-product")
def product_removing(data:schema.remove_product,db=Depends(database.get_db)):
    user_detail =  get_user_details(data.email)

    if not user_detail :
        raise HTTPException(status_code=404, detail="Email ID not found in database, use your login email.")
    
    if user_detail["user_type"] !="admin":
        raise HTTPException(status_code=403,detail="Only admin can add product.")
    
    product_detail = db.query(models.product_table).filter(
        models.product_table.id == data.product_id
    ).first()

    if not product_detail:
        raise HTTPException(status_code=404, detail=f"Product ID {data.product_id} not found.")


    db.delete(product_detail)
    db.commit()

    return {"Message":f"Product {data.product_id} delete successfully"}