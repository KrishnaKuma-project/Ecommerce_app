from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from . import schema, database, models, google_login,password_hashing,password_change, user_profile_update
import os
import time

app = FastAPI()

app.include_router(password_change.router, tags=["Password Change:"])
app.include_router(user_profile_update.router, tags=["Profile Update:"])
#app.include_router(google_login.router, tags=["google login."])

# def create_tables_with_retry(retries=5, delay=5):
#     for attempt in range(retries):
#         try:
#             database.Base.metadata.create_all(bind=database.engine)
#             return
#         except OperationalError:
#             print(f"DB not ready, retrying... ({attempt+1}/{retries})")
#             time.sleep(delay)
#     raise RuntimeError("Could not connect to DB after retries")

Login_status = []

# @app.on_event("startup")
# def on_startup():
#     create_tables_with_retry()

@app.post("/user-all_user_list")
def all_user_list_helper(db=Depends(database.get_db)):
    user_list = db.query(models.user_details).all()
    if not user_list:
        raise HTTPException(status_code=404, detail="User not found.")
    
    return user_list

@app.get("/users/{email}")
def get_user(email: str, db: Session = Depends(database.get_db)):
    user = db.query(models.user_details).filter(models.user_details.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.mobile:
        raise HTTPException(status_code=404, detail="User mobile not found.")
    return {"email": user.email, "user_type": user.user_type, "mobile":user.mobile}


@app.post("/login")
def login_api(data: schema.Login_schema,db=Depends(database.get_db)):
    user_check = db.query(models.user_details).filter(models.user_details.email==data.email).first()

    if not user_check:
        raise HTTPException(status_code=404, detail="Email ID not found in database.")
    
    if not password_hashing.verify_password(data.password,user_check.password):
        raise HTTPException(status_code=401, detail="You given invalid Password.")
    
    # if not data.otp == user_check.otp:
    #     raise HTTPException(status_code=401, detail="Invalid OTP.")
    
    token = password_hashing.create_access_token({"sub":user_check.username,"user_type":user_check.user_type})
    if not user_check.email in Login_status:
        Login_status.append(user_check.email)

    return {"Message" : "Login Successfully",
            "Access_token":token,
            "Token":"bearer"}

@app.post ("/signup")
def signup_api(data:schema.Signup_schema,db=Depends(database.get_db)):
    user_email_check = db.query(models.user_details).filter(models.user_details.email==data.email).first()
    if user_email_check:
        raise HTTPException(status_code=401, detail="Email Already in database.")
    
    user_username_check = db.query(models.user_details).filter(models.user_details.username==data.username).first()
    if user_username_check:
        raise HTTPException(status_code=401,detail="Username already in database.")
    
    user_mobile_check = db.query(models.user_details).filter(models.user_details.mobile==data.mobile).first()
    if user_mobile_check:
        raise HTTPException(status_code=401,detail="Mobile number already in database.")
    
    hashed_pwd = password_hashing.get_password_hashed(data.password)
    new_user= models.user_details(
        name=data.name,
        username=data.username,
        password=hashed_pwd,
        email=data.email,
        mobile=data.mobile,
        user_type=data.user_type,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    show_user_data = schema.signup_show(
        id=new_user.id,
        name=new_user.name,
        username=new_user.username,
        email=new_user.email,
        mobile=new_user.mobile,
        user_type=new_user.user_type
        )
    return show_user_data

@app.post("/logout")
def logout_process (data:schema.loguot_schema):
    if not data.email in Login_status:
        raise HTTPException(status_code=404, detail="User status already logout.")
    
    Login_status.remove(data.email)
    
    return {"Message" : "You logout process successfull."}