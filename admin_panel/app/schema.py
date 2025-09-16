from pydantic import BaseModel

class admin_dashboard_schema(BaseModel):
    email:str

class block_unblock_user_schema(BaseModel):
    your_email : str
    user_email : str

class all_user_list_schema(BaseModel):
    email : str