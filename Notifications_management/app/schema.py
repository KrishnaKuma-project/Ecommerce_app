from pydantic import BaseModel

class email_request_schema(BaseModel):
    email : str

class sms_requerst_schema(BaseModel):
    email : str