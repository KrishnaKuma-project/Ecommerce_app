from fastapi import APIRouter, HTTPException,Depends
from . import schema,models,database
import requests

router = APIRouter()

@router.post("/remove-cart_item")
def remove_cart_item(data:schema.romove_item_from_cart, db=Depends(database.get_db)):
    get_cart_item = db.query(models.cart_list).filter(
        models.cart_list.id == data.cart_id
    ).first()

    if not get_cart_item:
        raise HTTPException(status_code=404,detail="Cart item not found.")
    
    db.delete(get_cart_item)
    db.commit()

    return {"message": f"Cart item with id {data.cart_id} deleted successfully."}

@router.post("/remove-all_cart_item")
def remove_full_cart(data:schema.show_cart,db=Depends(database.get_db)):
    cart_item = db.query(models.cart_list).filter(
        models.cart_list.email==data.email
    ).all()

    if not cart_item:
        raise HTTPException(status_code=404, detail="No cart item found.")
    
    for item in cart_item:
        db.delete(item)

    db.commit()

    return{
        "message": f"All {len(cart_item)} cart items for {data.email} deleted successfully."
    }
