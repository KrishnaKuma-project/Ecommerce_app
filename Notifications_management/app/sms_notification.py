from fastapi import APIRouter, Depends,HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from twilio.rest import Client
from . import database, schema, models
import random 
import requests, os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from . import database, models

router = APIRouter()

account_sid ="AC8c86885c8858eb2d7483b7097250ae2a"
auth_token ="c8255d7d89e0d3f206cbb39f2d3bd509"
TWILIO_PHONE ="+18573092042"

client = Client(account_sid, auth_token)

def send_otp_sms(mobile: str, otp: str):
    """Send OTP SMS using Twilio Messaging API"""
    try:
        message = client.messages.create(
            body=f"Your OTP is {otp}. It is valid for 10 minutes.",
            from_=TWILIO_PHONE,
            to=f"+91{mobile}"
        )
        print("SMS SID:", message.sid)
    except Exception as e:
        print("Failed to send SMS:", e)

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


@router.post("/otp_sms")
def SMS_OTP (data:schema.sms_requerst_schema, backgroundtask : BackgroundTasks ,db : Session = Depends(database.get_db)):
    user_check = get_user_details(data.email)
    if not user_check:
        raise HTTPException(status_code=404, detail="User not found.")

    mobile=user_check["mobile"]

    if not mobile :
        raise HTTPException(status_code=404, detail="MObile number not found in the database.")
    
    otp = random.randint(100000,999999)
    otp_expiry_time =datetime.utcnow()+timedelta(minutes=10)

    new_details= db.query(models.notification_table).filter(
        models.notification_table.email == data.email
    ).first()

    if not new_details:
        new_details = models.notification_table(
            email=data.email,
            otp_number=otp,
            otp_expiry_time=otp_expiry_time,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(new_details)
    else:  
        new_details.otp_number = otp
        new_details.otp_expiry_time = otp_expiry_time
        new_details.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(new_details)

    backgroundtask.add_task(send_otp_sms, mobile, str(otp))

    return {"message": "OTP generated and sent successfully via Twilio"}