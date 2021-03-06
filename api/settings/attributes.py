from typing import Any

from settings.router import router

from openpype.lib.postgres import Postgres
from openpype.types import Field, OPModel


class AttributeModel(OPModel):
    name: str
    title: str
    example: str
    description: str
    attribType: str
    scope: list[str] = Field(default_factory=list)
    builtIn: bool
    writable: bool


class SettingsResponseModel(OPModel):
    attributes: list[AttributeModel] = Field(
        default_factory=list, description="List of attributes user has access to"
    )


@router.get("/attributes", response_model=SettingsResponseModel)
async def get_settings():

    query = "SELECT name, scope, builtin, data FROM attributes ORDER BY position"

    attributes: list[AttributeModel] = []
    async for row in Postgres.iterate(query):
        data: dict[str, Any] = row["data"]

        # TODO: skip attributes user does not have read access to
        # TODO: set writable flag according to user rights

        attributes.append(
            AttributeModel(
                name=row["name"],
                title=data.get("title", row["name"]),
                example=str(data.get("example", "")),
                description=data.get("description", ""),
                scope=row["scope"],
                attribType=data.get("type", "string"),
                builtIn=row["builtin"],
                writable=True,
            )
        )

    return SettingsResponseModel(attributes=attributes)
