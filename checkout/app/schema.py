from pydantic import BaseModel

class order_process(BaseModel):
    email : str 
    address : str
    payment_options : str
    discount_code : str

class order_history(BaseModel):
    email :str

class order_helper(BaseModel):
    email : str

class remove_cart_after_order_schema (BaseModel):
    email :str

class order_cancel_helper_process_schema(BaseModel):
    order_id : int