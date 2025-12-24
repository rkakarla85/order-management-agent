from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
from business_manager import BusinessManager
from ai_agent import get_sheets_manager 

router = APIRouter()
business_manager = BusinessManager()

class BusinessCreate(BaseModel):
    name: str
    type: str # retail or restaurant
    sheet_id: str
    config: Optional[dict] = {}

@router.get("/admin/businesses")
def list_businesses():
    return business_manager.list_businesses()

@router.post("/admin/businesses")
def create_business(biz: BusinessCreate):
    return business_manager.create_business(biz.dict())

@router.get("/orders")
def get_orders(business_id: str = "electronics_default"):
    sheets = get_sheets_manager(business_id)
    if not sheets:
        raise HTTPException(status_code=404, detail="Business not found")
    return sheets.get_orders()
