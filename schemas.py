"""
Database Schemas for Телетекст (Nevinnomyssk)

Each Pydantic model corresponds to a MongoDB collection. The collection name
is the lowercase of the class name.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class Plan(BaseModel):
    """
    Internet tariff plans
    Collection: "plan"
    """
    name: str = Field(..., description="Plan name")
    speed_mbps: int = Field(..., ge=1, description="Speed in Mbps")
    price_rub: int = Field(..., ge=0, description="Monthly price in RUB")
    description: Optional[str] = Field(None, description="Short description")
    featured: bool = Field(False, description="Highlight this plan on the site")
    unlimited: bool = Field(True, description="Unlimited traffic")


class Lead(BaseModel):
    """
    Incoming contact requests
    Collection: "lead"
    """
    name: str = Field(..., description="Customer full name")
    phone: str = Field(..., description="Phone number")
    street_address: Optional[str] = Field(None, description="Street and house")
    apartment: Optional[str] = Field(None, description="Apartment/Office")
    comment: Optional[str] = Field(None, description="Additional info")
    source: Optional[str] = Field("website", description="Where the lead came from")


# Example generic models (kept for reference but not used by the app)
class User(BaseModel):
    name: str
    email: EmailStr
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    category: str
    in_stock: bool = True
