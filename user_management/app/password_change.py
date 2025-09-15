from fastapi import APIRouter, Depends, HTTPException
from . import schema, database, models, password_hashing

router = APIRouter()

@router.post("/password-change")
def password_change(data:schema.password_change,db=Depends(database.get_db)):
    if not data.new_password == data.confirm_password:
        raise HTTPException(status_code=401,detail="New password and Confirm password should be same.")

    user_check = db.query(models.user_details).filter(models.user_details.email==data.email).first()

    if not user_check :
        raise HTTPException(status_code=404,detail="User not found.")
    
    check_old_password = password_hashing.verify_password(data.old_password,user_check.password)
    if not check_old_password:
        raise HTTPException(status_code=401, detail="Old password is incorrect.")
    
    hash_pw = password_hashing.get_password_hashed(data.new_password)

    user_check.password = hash_pw
    db.commit()
    db.refresh(user_check)

    return {"message": "Password changed successfully"}