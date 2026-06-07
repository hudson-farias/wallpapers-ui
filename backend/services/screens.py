from database.screens import ScreenAliasesORM


async def alias_map() -> dict[int, str]:
    async with ScreenAliasesORM() as orm:
        entries = await orm.find_many()
    return {entry.screen_id: entry.alias for entry in entries}


async def merge_aliases(screens: list[dict]) -> list[dict]:
    aliases = await alias_map()
    merged: list[dict] = []

    for screen in screens:
        alias = aliases.get(screen['id'], '')
        merged.append(
            {
                **screen,
                'alias': alias,
                'display_name': alias or screen.get('name', f"Desktop {screen['id']}"),
            }
        )

    return merged


async def set_alias(screen_id: int, alias: str) -> str:
    alias = alias.strip()

    async with ScreenAliasesORM() as orm:
        existing = await orm.find_one(screen_id = screen_id)

        if not alias:
            if existing:
                await orm.delete(screen_id = screen_id)
            return ''

        if existing:
            await orm.update(existing.id, alias = alias)
        else:
            await orm.create(screen_id = screen_id, alias = alias)

    return alias
