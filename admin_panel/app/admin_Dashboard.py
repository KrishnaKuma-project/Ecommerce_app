from fastapi import APIRouter, HTTPException, Depends
from . import database, schema, models
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

def get_sales_data(email : str):
    try:
        url = f"http://checkout:8000/admin-dashboard_helper/{email}"
        resp = requests.post(url, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            return None
        else:
            raise HTTPException(status_code=resp.status_code, detail="Dashboard service error")
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Error contacting dashboard service: {e}")

@router.post("/admin-dashboard_sales")
def admin_dashboard_process(
    email:str,
    #data:schema.admin_dashboard_schema,
    db = Depends(database.get_db)
):
    get_user_type = get_user_details(email)
    if not get_user_type:
        raise HTTPException(status_code=404, detail= "User not found.")
    
    if get_user_type["user_type"] != "admin":
        raise HTTPException(status_code=401, detail="Only admin can access this.")
    
    sales_details = get_sales_data(email)
    if not sales_details :
        raise HTTPException(status_code=404, detail="No sales data found.")
    
    # new_detail = models.admin_activity(
    #     email = email,
    #     last_activity = "view sales data",
    # )
    # db.add(new_detail)
    # db.commit()
    # print("DB Add successfully.")
    
    return sales_details