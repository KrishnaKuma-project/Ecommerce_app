from pydantic import BaseModel

class order_history_schema (BaseModel):
    email : str 

class order_tracking_process_schema (BaseModel):
    email : str 

class order_cancel_process_schema(BaseModel):
    email : str
    order_id : int