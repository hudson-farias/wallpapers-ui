from fastapi import HTTPException
from fastapi.responses import FileResponse

from routers import router
from models.favorites import FavoriteDTO
from services import favorites as favorites_service


@router.get('/favorites', status_code = 200)
async def get_favorites():
    slugs = favorites_service.list_slugs()
    return {
        'slugs': slugs,
        'count': favorites_service.favorite_count(),
    }


@router.get('/favorites/{slug}/images', status_code = 200)
async def get_favorite_slug_images(slug: str):
    try:
        favorites_service.validate_slug(slug)
    except ValueError as exc:
        raise HTTPException(status_code = 400, detail = str(exc))

    images = favorites_service.list_slug_images(slug)
    return {'slug': slug, 'images': images}


@router.post('/favorites', status_code = 201)
async def add_favorite(body: FavoriteDTO):
    try:
        path = favorites_service.add_favorite(body.slug, body.filename)
    except FileNotFoundError:
        raise HTTPException(status_code = 404, detail = 'imagem não encontrada no cache')
    except ValueError as exc:
        raise HTTPException(status_code = 400, detail = str(exc))

    return {
        'ok': True,
        'slug': body.slug,
        'filename': body.filename,
        'path': str(path),
    }


@router.delete('/favorites/{slug}/{filename:path}', status_code = 200)
async def remove_favorite(slug: str, filename: str):
    try:
        favorites_service.remove_favorite(slug, filename)
    except FileNotFoundError:
        raise HTTPException(status_code = 404, detail = 'favorito não encontrado')
    except ValueError as exc:
        raise HTTPException(status_code = 400, detail = str(exc))

    return {'ok': True, 'slug': slug, 'filename': filename}


@router.get('/favorites/images/{slug}/{filename:path}', status_code = 200)
async def get_favorite_image(slug: str, filename: str):
    try:
        path = favorites_service.resolve_favorite_path(slug, filename)
    except FileNotFoundError:
        raise HTTPException(status_code = 404, detail = 'image not found')
    except ValueError as exc:
        raise HTTPException(status_code = 400, detail = str(exc))

    return FileResponse(path)
