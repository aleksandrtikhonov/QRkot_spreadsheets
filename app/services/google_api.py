from datetime import datetime, timedelta

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.services.const import (
    FORMAT,
    SHEETS_SERVICE_VERSION,
    SHEET_TYPE,
    SHEET_ID,
    TITLE,
    ROW_COUNT,
    COLUMN_COUNT,
    DRIVE_SERVICE_VERSION,
)


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', SHEETS_SERVICE_VERSION)
    spreadsheet_body = {
        'properties': {'title': f'Отчет от {now}', 'locale': 'ru_RU'},
        'sheets': [
            {
                'properties': {
                    'sheetType': SHEET_TYPE,
                    'sheetId': SHEET_ID,
                    'title': TITLE,
                    'gridProperties': {
                        'rowCount': ROW_COUNT,
                        'columnCount': COLUMN_COUNT,
                    },
                }
            }
        ],
    }

    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
    spreadsheet_id: str, wrapper_services: Aiogoogle
) -> None:
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email,
    }
    service = await wrapper_services.discover('drive', DRIVE_SERVICE_VERSION)
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id, json=permissions_body, fields='id'
        )
    )


async def spreadsheets_update_value(
    spreadsheet_id: str, projects: list, wrapper_services: Aiogoogle
) -> None:
    service = await wrapper_services.discover('sheets', SHEETS_SERVICE_VERSION)
    values = [
        ['Отчет от', datetime.now().strftime(FORMAT)],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание'],
    ]

    for project in projects:
        values.append(
            [
                project.name,
                str(timedelta(days=project.project_duration)),
                project.description,
            ]
        )

    update_body = {'majorDimension': 'ROWS', 'values': values}
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range='A1:E30',
            valueInputOption='USER_ENTERED',
            json=update_body,
        )
    )
