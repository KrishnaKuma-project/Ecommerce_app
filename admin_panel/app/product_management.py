from fastapi import APIRouter, HTTPException,Depends
from . import database, models, schema, user_block_unblock
import requests

router = APIRouter()

def get_all_user_list():
    try :
        resp = requests.post(f"http://user_management:8000/user-all_user_list")
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            return None
        else:
            raise HTTPException(status_code=resp.status_code, detail="User service error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error contacting user service: {e}")


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

@router.post("/admin-get_user_list")
def all_user_list_process (
    data : schema.all_user_list_schema,
    db = Depends(database.get_db)
):
    user_admin_check = get_user_details(data.email)
    if not user_admin_check:
        raise HTTPException(status_code=404,detail="User detail not found.")
    
    if user_admin_check["user_type"] != "admin":
        raise HTTPException(status_code=401, detail="Only admin can access this.")
    
    all_user_list = get_all_user_list()
    if not all_user_list:
        raise HTTPException(status_code=404, detail="Something went wrong. please try again.")
    
    user_list = []
    for user in all_user_list:
        user_list.append(user)

    return user_list