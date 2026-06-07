from pathlib import Path

from fastapi import File, Form, HTTPException, UploadFile

from routers import router
from models.apply import ApplyDTO
from services import favorites as favorites_service
from services import images as images_service
from services import plasma, sources as sources_service


def _resolve_apply_path(body: ApplyDTO):
    if body.from_favorites: return favorites_service.resolve_favorite_path(body.slug, body.filename)
    return sources_service.resolve_image_path(body.slug, body.filename)


@router.post('/apply', status_code = 200)
async def apply_wallpaper(body: ApplyDTO):
    try: image_path = _resolve_apply_path(body)
    except FileNotFoundError: raise HTTPException(status_code = 404, detail = 'image not found')
    except ValueError as exc: raise HTTPException(status_code = 400, detail = str(exc))

    try: plasma.apply_wallpaper(body.screen_id, image_path)
    except RuntimeError as exc: raise HTTPException(status_code = 503, detail = str(exc))
    except Exception as exc: raise HTTPException(status_code = 500, detail = f'falha ao aplicar wallpaper: {exc}')

    return {'ok': True, 'screen_id': body.screen_id, 'image': str(image_path)}


@router.post('/apply/crop', status_code = 200)
async def apply_cropped_wallpaper(screen_id: int = Form(...), slug: str = Form(...), filename: str = Form(...), crop_x: int = Form(...), crop_y: int = Form(...), crop_width: int = Form(...), crop_height: int = Form(...), output_width: int = Form(1920), output_height: int = Form(1080), image: UploadFile = File(...)):
    if crop_width <= 0 or crop_height <= 0:
        raise HTTPException(status_code = 400, detail = 'crop inválido')

    content = await image.read()
    try:
        saved = images_service.save_cropped_image(
            content,
            width = output_width,
            height = output_height,
            left = crop_x,
            top = crop_y,
            crop_width = crop_width,
            crop_height = crop_height,
            original_name = filename,
        )
        plasma.apply_wallpaper(screen_id, Path(saved))
    except RuntimeError as exc: raise HTTPException(status_code = 503, detail = str(exc))
    except Exception as exc: raise HTTPException(status_code = 500, detail = f'falha ao aplicar crop: {exc}')

    return {'ok': True, 'screen_id': screen_id, 'image': str(saved)}
