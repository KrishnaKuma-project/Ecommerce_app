from fastapi import FastAPI
from . import email_trigger,database,sms_notification

app = FastAPI()
app.include_router(email_trigger.router,tags=["Email Notification."])
app.include_router(sms_notification.router, tags=["Sms Notification."])

@app.on_event("startup")
def startup():
    database.Base.metadata.create_all(bind=database.engine)

@app.get("/")
def summa ():
    return{"Message":"notification working."}