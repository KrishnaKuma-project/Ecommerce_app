from pydantic import BaseModel

class remove_product (BaseModel):
    email : str 
    product_id : int

class add_product (BaseModel):
    email : str
    product_name : str
    product_description : str
    product_categorie : str
    product_price : str
    product_sku : str
    product_specifications : str

class show_product_by_id (BaseModel):
    id : int

class show_product_by_name (BaseModel):
    product_name : str

class show_product_by_categorie (BaseModel):
    product_categorie : str

class show_product_by_price (BaseModel):
    product_price : str

class show_product (BaseModel):
    id : int
    product_name : str
    product_description : str
    product_categorie : str
    product_price : str
    product_stock_status : str
    product_sku : str
    product_specifications : str

    class Config:
        orm_mode = True

class edit_product (BaseModel):
    product_name : str | None = None
    product_description : str | None = None
    product_categorie : str | None = None
    product_price : str | None = None
    product_stock_status : str | None = None
    product_sku : str | None = None
    product_specifications : str | None = None
