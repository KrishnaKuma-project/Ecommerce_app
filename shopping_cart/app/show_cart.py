from fastapi import APIRouter, HTTPException, Depends
from . import database, models, schema

router = APIRouter()

@router.post("/show-cart")
def show_user_cart(data:schema.show_cart,db=Depends(database.get_db)):
    
    cart_items = db.query(models.cart_list).filter(
        models.cart_list.email == data.email
    ).all()

    if not cart_items:
        raise HTTPException(status_code=404, detail="No cart iteam found.")
    
    items_list =[]
    shipping=50
    total_price = 0
    total_tax = 0

    for items in cart_items:
        id = items.id
        price =int(items.product_price)
        sub_total = price * items.product_count
        tax = round(sub_total * 0.05, 2)
        total_tax += tax
        total_price += sub_total

        items_list.append({
            "cart_id":items.id,
            "product_name": items.product_name,
            "product_price": price,
            "product_count": items.product_count,
            "subtotal": sub_total
        })
    
    grand_total = (total_price+total_tax+shipping)

    return {
        "email":data.email,
        "cart_ids": [item["cart_id"] for item in items_list],
        "cart_items": items_list,
        "items_price": total_price,
        "shipping_cost": shipping,
        "total_tax" : total_tax,
        "total_price": grand_total
    }