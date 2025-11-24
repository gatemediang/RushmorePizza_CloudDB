import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your services
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.menu_service import get_menu_items, get_stores
from services.order_service import place_order

app = FastAPI(title="RushMore Pizza API", version="1.0.0")


class LineItem(BaseModel):
    item_id: int = Field(..., gt=0)
    order_type: str = Field(..., pattern="^(Box|Slice)$")
    quantity: int = Field(..., gt=0)


class OrderRequest(BaseModel):
    store_id: int = Field(..., gt=0)
    customer_id: Optional[int] = Field(None, gt=0)
    items: List[LineItem]
    payment_method: str = Field("cash", pattern="^(cash|card|online)$")


class OrderResponse(BaseModel):
    order_id: int
    total_amount: float
    lines: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/menu")
def menu():
    try:
        return get_menu_items()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stores")
def stores():
    try:
        return get_stores()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orders", response_model=OrderResponse)
def create_order(req: OrderRequest):
    try:
        result = place_order(
            customer_id=req.customer_id,
            store_id=req.store_id,
            items=[i.dict() for i in req.items],
            payment_method=req.payment_method,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
