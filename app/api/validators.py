from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject
from app.schemas.charity_project import CharityProjectUpdate


async def check_name_duplicate(
    charity_project_name: str,
    session: AsyncSession,
) -> None:
    charity_project = await charity_project_crud.get_charity_project_by_name(
        charity_project_name=charity_project_name, session=session
    )
    if charity_project:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


async def check_charity_project_exists(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    charity_project = await charity_project_crud.get(
        obj_id=project_id, session=session
    )
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Проект не найден!'
        )
    return charity_project


async def check_charity_project_before_edit(
    project_id: int,
    charity_project_in: CharityProjectUpdate,
    session: AsyncSession,
) -> CharityProject:
    charity_project = await check_charity_project_exists(
        project_id=project_id, session=session
    )
    if charity_project.close_date:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!',
        )

    invested = charity_project_in.full_amount
    if invested and charity_project.invested_amount > invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Нельзя установить требуемую сумму меньше уже вложенной',
        )

    new_name = charity_project_in.name
    await check_name_duplicate(charity_project_name=new_name, session=session)
    return charity_project


async def check_charity_project_before_delete(
    project_id: int, session: AsyncSession
) -> CharityProject:
    charity_project = await check_charity_project_exists(
        project_id=project_id, session=session
    )

    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!',
        )
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!',
        )

    return charity_project
