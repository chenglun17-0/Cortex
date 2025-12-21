from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db import get_session
from app.models import Organization

router = APIRouter()

@router.post("/", response_model=Organization)
def create_organization(org: Organization, session: Session = Depends(get_session)):
    session.add(org)
    session.commit()
    session.refresh(org)
    return org

@router.get("/", response_model=List[Organization])
def get_organizations(session: Session = Depends(get_session)):
    statement = select(Organization)
    results = session.exec(statement).all()
    return results