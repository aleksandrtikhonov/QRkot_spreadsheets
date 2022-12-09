from typing import Optional, List, Dict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_charity_project_by_name(
            self,
            charity_project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        db_charity_project = await session.execute(
            select(CharityProject).where(
                CharityProject.name == charity_project_name
            )
        )
        return db_charity_project.scalars().first()

    async def get_projects_by_completion_rate(
            self, session: AsyncSession
    ) -> List[Dict[str, str]]:
        closed_projects = await session.execute(
            select(
                CharityProject.name,
                CharityProject.description,
                (func.julianday(CharityProject.close_date) - func.julianday(
                    CharityProject.create_date)).label('project_duration'),
            )
            .where(CharityProject.fully_invested.is_(True))
            .order_by('project_duration')
        )
        return closed_projects.all()


charity_project_crud = CRUDCharityProject(CharityProject)
