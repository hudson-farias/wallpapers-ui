from fastapi import HTTPException, Query
from fastapi.responses import FileResponse

from routers import router
from database.sources import SourcesORM
from models.sources import Source, SourceDTO, parse_source
from services import cache as cache_service
from services import sources as sources_service


def image_count(slug: str) -> int:
    return len(sources_service.list_images(slug))


async def response_data() -> list[Source]:
    async with SourcesORM() as orm:
        entries = await orm.find_many()

    entries = sorted(entries, key = lambda entry: entry.slug)
    return [
        Source(
            id = entry.id,
            slug = entry.slug,
            source = entry.source,
            image_count = image_count(entry.slug),
        )
        for entry in entries
    ]


@router.get('/sources', status_code = 200)
async def get_sources():
    return {'sources': await response_data()}


@router.post('/sources', status_code = 201)
async def post_source(params: SourceDTO):
    try:
        data = parse_source(str(params.source))
    except ValueError as exc:
        raise HTTPException(status_code = 400, detail = str(exc))

    async with SourcesORM() as orm:
        existing_slug = await orm.find_one(slug = data['slug'])
        if existing_slug and existing_slug.source != data['source']:
            raise HTTPException(status_code = 400, detail = f"slug '{data['slug']}' já existe para outra fonte")

        existing_source = await orm.find_one(source = data['source'])
        if existing_source:
            raise HTTPException(status_code = 400, detail = 'fonte já cadastrada')

        await orm.create(**data)

    entry = await SourcesORM().find_one(slug = data['slug'])
    return Source(
        id = entry.id,
        slug = entry.slug,
        source = entry.source,
        image_count = 0,
    )


@router.delete('/sources/{source_id}', status_code = 200)
async def delete_source(source_id: int):
    async with SourcesORM() as orm:
        entry = await orm.find_one(id = source_id)
        if not entry:
            raise HTTPException(status_code = 404, detail = 'fonte não encontrada')

        slug = entry.slug
        await orm.delete(id = source_id)

    cache_service.remove_cache(slug)
    return {'ok': True, 'id': source_id, 'slug': slug}


@router.post('/sources/{slug}/refresh', status_code = 200)
async def refresh_source(slug: str):
    async with SourcesORM() as orm:
        entry = await orm.find_one(slug = slug)
        if not entry:
            raise HTTPException(status_code = 404, detail = 'fonte não encontrada')

    try:
        await cache_service.ensure_cache(entry.slug, entry.source, refresh = True)
    except RuntimeError as exc:
        raise HTTPException(status_code = 503, detail = str(exc))

    return {'slug': slug, 'images': sources_service.list_images(slug)}


@router.get('/sources/{slug}/images', status_code = 200)
async def get_source_images(slug: str, refresh: bool = Query(default = False)):
    async with SourcesORM() as orm:
        entry = await orm.find_one(slug = slug)
        if not entry:
            raise HTTPException(status_code = 404, detail = 'fonte não encontrada')

    try:
        await cache_service.ensure_cache(entry.slug, entry.source, refresh = refresh)
    except RuntimeError as exc:
        raise HTTPException(status_code = 503, detail = str(exc))

    return {'slug': slug, 'images': sources_service.list_images(slug)}


@router.get('/images/{slug}/{filename}', status_code = 200)
async def get_image(slug: str, filename: str):
    async with SourcesORM() as orm:
        if await orm.find_one(slug = slug) is None:
            raise HTTPException(status_code = 404, detail = 'fonte não encontrada')

    try:
        path = sources_service.resolve_image_path(slug, filename)
    except FileNotFoundError:
        raise HTTPException(status_code = 404, detail = 'image not found')
    except ValueError as exc:
        raise HTTPException(status_code = 400, detail = str(exc))

    return FileResponse(path)
