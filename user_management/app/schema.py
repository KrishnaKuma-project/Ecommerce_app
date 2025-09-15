from pydantic import BaseModel, field_validator, EmailStr

class Login_schema (BaseModel):
    email : str 
    password : str 
    #otp : str

class Signup_schema (BaseModel):
    name :str 
    username : str 
    password : str 
    email : str
    mobile : str
    user_type : str

class signup_show (BaseModel):
    id : int
    name : str
    username : str
    email : str
    mobile : str
    user_type : str

class password_change (BaseModel):
    email : str
    old_password : str
    new_password : str
    confirm_password : str

class loguot_schema (BaseModel):
    email :str

class profile_update (BaseModel):
    email : str
    name : str | None = None
    mobile : str | None = None
    username : str | None = None