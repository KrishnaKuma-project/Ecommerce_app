from fastapi import APIRouter,HTTPException,Depends
from . import schema, database, models, main

router = APIRouter()

@router.post ("/user-update")
def user_detail_update(data:schema.profile_update, db=Depends(database.get_db)):
    if not data.email in main.Login_status:
        raise HTTPException(status_code=404, detail="You want login first to update user details.")
    
    user_details_from_db = db.query(models.user_details).filter(models.user_details.email== data.email).first()

    update_list=[]

    if not user_details_from_db:
        raise HTTPException(status_code=404, detail="User detail not found in database.")
    
    if not user_details_from_db.email == data.email:
        user_details_from_db.email =data.email
        db.commit()
        update_list.append("email")

    if not data.name=="string":
        if not user_details_from_db.name == data.name:
            user_details_from_db.name = data.name
            db.commit()
            update_list.append("name")
    
    if not data.mobile=="string":
        if not user_details_from_db.mobile== data.mobile:
            user_details_from_db.mobile = data.mobile
            db.commit()
            update_list.append("mobile")

    if not data.username =="string":
        if not user_details_from_db.username == data.username:
            user_details_from_db.username=data.username
            db.commit()
            update_list.append("username")

    db.refresh(user_details_from_db)

    return{"Updated":f"{update_list}"}