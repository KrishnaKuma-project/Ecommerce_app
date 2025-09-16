from fastapi import APIRouter, HTTPException, Depends
from . import database, models, schema
import requests

router = APIRouter()

@router.post("/admin-dashboard_helper/{email}")
def admin_dashboard_helper(
    email : str,
    #data: schema.admin_dashboard_helper,
    db = Depends(database.get_db)
):
    sales_count = db.query(models.order_details).count()

    if not sales_count :
        raise HTTPException(status_code=404, detail="No sales details found.")
    
    return {"Sales data":sales_count}