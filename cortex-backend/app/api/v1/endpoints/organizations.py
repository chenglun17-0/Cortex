from typing import List

from fastapi import APIRouter, Depends
from app.models.organization import Organization as OrganizationModel
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, Organization
router = APIRouter()

@router.post("/", response_model=Organization)
async def create_organization(org: OrganizationCreate):
    org_obj = await OrganizationModel.create(**org.model_dump())
    return org_obj
@router.get("/", response_model=List[Organization])
async def get_organizations():
    return await OrganizationModel.all()