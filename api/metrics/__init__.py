from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from openpype.lib.postgres import Postgres
from openpype.lib.redis import Redis

router = APIRouter(prefix="", include_in_schema=False)


@router.get(
    "/metrics",
    response_class=PlainTextResponse,
)
async def get_system_metrics():
    result = ""
    async for record in Postgres.iterate("SELECT name FROM users"):
        name = record["name"]
        requests = await Redis.get("user-requests", name)
        num_requests = 0 if requests is None else int(requests)
        result += f'openpype_user_requests{{name="{name}"}} {num_requests}\n'

    return PlainTextResponse(result)
