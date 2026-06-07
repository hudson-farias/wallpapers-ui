from fastapi import HTTPException

from routers import router
from models.screens import ScreenAliasDTO
from services import plasma
from services import screens as screens_service


@router.get('/screens', status_code = 200)
async def get_screens():
    screens = await screens_service.merge_aliases(plasma.list_screens())
    return {
        'screens': screens,
        'dbus_available': any(screen.get('available') for screen in screens),
    }


@router.put('/screens/{screen_id}/alias', status_code = 200)
async def put_screen_alias(screen_id: int, body: ScreenAliasDTO):
    if screen_id < 0:
        raise HTTPException(status_code = 400, detail = 'screen_id inválido')

    try:
        alias = await screens_service.set_alias(screen_id, body.alias)
    except ValueError as exc:
        raise HTTPException(status_code = 400, detail = str(exc))

    plasma_screens = plasma.list_screens()
    plasma_screen = next((screen for screen in plasma_screens if screen['id'] == screen_id), None)
    name = plasma_screen['name'] if plasma_screen else f'Desktop {screen_id}'

    return {
        'ok': True,
        'screen_id': screen_id,
        'alias': alias,
        'display_name': alias or name,
    }
