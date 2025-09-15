from fastapi import APIRouter, HTTPException, Depends,BackgroundTasks
import os 
from dotenv import load_dotenv
from email.message import EmailMessage
from datetime import datetime , timedelta
from sqlalchemy.orm import Session
import aiosmtplib
import random
import requests
from . import schema,database,models


router = APIRouter()
load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

async def sent_otp_email (to_email:str,otp:str):
    message = EmailMessage()
    message["From"]=EMAIL_USER
    message["To"]=to_email
    message["subject"]="Your OTP Code"
    message.set_content(f"Your OTP Code is {otp}, this valid for 10 minutes.")

    await aiosmtplib.send(
        message,
        hostname = EMAIL_HOST,
        port = EMAIL_PORT,
        start_tls=True,
        username=EMAIL_USER,
        password=EMAIL_PASS
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


@router.post("/notification-email")
async def sent_otp(data: schema.email_request_schema,background_tasks:BackgroundTasks,db:Session=Depends(database.get_db)):
    otp = random.randint(100000,999999)
    otp_expiry_time =datetime.utcnow()+timedelta(minutes=10)

    user_check = get_user_details(data.email)
    if not user_check:
        raise HTTPException(status_code=404, detail="User not found.")

    otp_check = db.query(models.notification_table).filter(models.notification_table.email==data.email).first()
    if not otp_check:
        new_otp = models.notification_table(
            email=data.email,
            otp_number=otp,
            otp_expiry_time=otp_expiry_time,    
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_otp)
        db.commit()
        db.refresh(new_otp)
        return {"Message": f"Otp send to {new_otp.email}"}
    
    otp_check.otp_number=otp
    otp_check.otp_expiry_time=otp_expiry_time
    db.commit()

    background_tasks.add_task(sent_otp_email,data.email,otp)

    return {"Message":f"OTP send to {data.email}"}
