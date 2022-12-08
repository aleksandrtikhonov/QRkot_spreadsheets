from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationAllDB, DonationCreate, DonationDB
from app.services.distribution_investments import investment_process

router = APIRouter()


@router.get(
    '/',
    response_model=List[DonationAllDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    return await donation_crud.get_multi(session=session)


@router.get(
    '/my', response_model=List[DonationDB], response_model_exclude_none=True
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    return await donation_crud.get_user_donations(session=session, user=user)


@router.post('/', response_model=DonationDB, response_model_exclude_none=True)
async def create_donation(
    donation_in: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    donation = await donation_crud.create(
        obj_in=donation_in, session=session, user=user
    )
    await investment_process(session=session)
    await session.refresh(donation)
    return donation
