from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from decimal import Decimal
import uvicorn
from pydantic import BaseModel, field_validator
from datetime import date as date_type, datetime

from database import SessionLocal, Contract

app = FastAPI(title="OpenLisboa Contracts API", description="API for public procurement contracts", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas for response validation
class ContractBase(BaseModel):
    id: int
    title: Optional[str] = None
    value: Optional[float] = None
    date: Optional[date_type] = None
    authority: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator('value', mode='before')
    @classmethod
    def coerce_decimal(cls, v):
        if isinstance(v, Decimal):
            return float(v)
        return v


class AggregatedValue(BaseModel):
    name: str
    total_value: float
    contract_count: int

@app.get("/contracts", response_model=List[ContractBase])
def read_contracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Returns a paginated list of contracts."""
    contracts = db.query(Contract).order_by(desc(Contract.date)).offset(skip).limit(limit).all()
    return contracts

@app.get("/top-companies", response_model=List[AggregatedValue])
def top_companies(limit: int = 10, db: Session = Depends(get_db)):
    """Returns companies ordered by total contract value."""
    results = db.query(
        Contract.company.label('name'),
        func.sum(Contract.value).label('total_value'),
        func.count(Contract.id).label('contract_count')
    ).group_by(Contract.company).order_by(desc(func.sum(Contract.value))).limit(limit).all()
    
    return [
        {"name": row.name, "total_value": float(row.total_value) if row.total_value else 0.0, "contract_count": row.contract_count}
        for row in results
    ]

@app.get("/top-authorities", response_model=List[AggregatedValue])
def top_authorities(limit: int = 10, db: Session = Depends(get_db)):
    """Returns contracting authorities by total spending."""
    results = db.query(
        Contract.authority.label('name'),
        func.sum(Contract.value).label('total_value'),
        func.count(Contract.id).label('contract_count')
    ).group_by(Contract.authority).order_by(desc(func.sum(Contract.value))).limit(limit).all()
    
    return [
        {"name": row.name, "total_value": float(row.total_value) if row.total_value else 0.0, "contract_count": row.contract_count}
        for row in results
    ]

@app.get("/company/{name}", response_model=List[ContractBase])
def contracts_by_company(name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Returns all contracts won by a specific company."""
    contracts = db.query(Contract).filter(Contract.company.ilike(f"%{name}%")).order_by(desc(Contract.date)).offset(skip).limit(limit).all()
    return contracts

@app.get("/authority/{name}", response_model=List[ContractBase])
def contracts_by_authority(name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Returns all contracts issued by a specific authority."""
    contracts = db.query(Contract).filter(Contract.authority.ilike(f"%{name}%")).order_by(desc(Contract.date)).offset(skip).limit(limit).all()
    return contracts

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
