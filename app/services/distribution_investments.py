from datetime import datetime
from typing import Union, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models import CharityProject, Donation


def close_fully_invested_object(obj: Union[CharityProject, Donation]) -> None:
    obj.fully_invested = True
    obj.invested_amount = obj.full_amount
    obj.close_date = datetime.now()


async def investment_process(session: AsyncSession) -> None:
    investments_open = await donation_crud.get_opened_objects(session=session)
    open_projects = await charity_project_crud.get_opened_objects(
        session=session
    )
    if not investments_open or not open_projects:
        return
    for donation in investments_open:
        await closing_invested_object(donation, open_projects)
    await session.commit()


async def closing_invested_object(
    donation: Donation, open_projects: List[CharityProject]
) -> None:
    for project in open_projects:
        left_fundraising = project.full_amount - project.invested_amount
        available_donation = donation.full_amount - donation.invested_amount
        project_balance = left_fundraising - available_donation

        if project_balance == 0:
            close_fully_invested_object(donation)
            close_fully_invested_object(project)

        if project_balance < 0:
            donation.invested_amount += abs(project_balance)
            close_fully_invested_object(project)

        if project_balance > 0:
            project.invested_amount += available_donation
            close_fully_invested_object(donation)
