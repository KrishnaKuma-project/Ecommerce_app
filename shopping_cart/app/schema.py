from pydantic import BaseModel

class add_to_cart(BaseModel):
    email: str
    product_id: int
    product_count: int = 1

class CartResponse(BaseModel):
    id: int
    email: str
    product_id: int
    product_name: str
    product_price: str
    product_count: int

    class Config:
        from_attributes = True 

class show_cart (BaseModel):
    email : str

class romove_item_from_cart (BaseModel):
    email : str
    cart_id : int