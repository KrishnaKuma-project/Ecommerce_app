from fastapi import APIRouter, Depends, HTTPException
from . import database, models, schema
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


@router.post ("/admin_access-user_block")
def user_block_process(
    data:schema.block_unblock_user_schema,
    db=Depends(database.get_db)
):
    user_check_for_admin = get_user_details(data.your_email)
    if not user_check_for_admin:
        raise HTTPException(status_code=404, detail="User not found.")
    
    if user_check_for_admin["user_type"]!="admin":
        raise HTTPException(status_code=401,detail="Only admin can access this.")
    
    user_check_for_user = get_user_details(data.user_email)
    if not user_check_for_user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    if user_check_for_user["user_type"]=="admin":
        raise HTTPException(status_code=401, detail="You can't block or unblock you admin.")
    
    block_user = models.user_block_unblock_details(
        email = data.user_email,
        blocked_user_email = data.your_email,
    )
    db.add(block_user)
    db.commit()

    return {"Message":f"User {data.user_email} Blocked."}

@router.post("/admin_access-user_unblock")
def user_unblock_process(
    data:schema.block_unblock_user_schema,
    db=Depends(database.get_db)
):
    user_check_for_unblock = get_user_details(data.user_email)
    if not user_check_for_unblock:
        raise HTTPException(status_code=404,detail="User not found.")
    
    if user_check_for_unblock["user_type"] == "admin":
        raise HTTPException(status_code=401,detail="You can't unblock admin.")
    
    user_check_for_admin = get_user_details(data.your_email)
    if not user_check_for_admin:
        raise HTTPException(status_code=404, detail="Your email not found in database.")
    
    if user_check_for_admin["user_type"] != "admin":
        raise HTTPException(status_code=401,detail="Only admin can unblock user.")

    check_blocked_user = db.query(models.user_block_unblock_details).filter(
        models.user_block_unblock_details.email == data.user_email
    ).first()
    if not check_blocked_user:
        raise HTTPException(status_code=404, detail="User not in Blocked list.")
    try:
        db.delete(check_blocked_user)
        db.commit()
    except Exception:
        return{"Message":"Something went wrong. please try again later"}
    
    return {"Message":f"User {data.user_email} Unblocked."}