from fastapi import APIRouter, Response

from openpype.exceptions import NotFoundException
from openpype.types import OPModel, Field
from openpype.lib.postgres import Postgres
from anatomy.anatomy import AnatomyPreset

router = APIRouter(tags=["Anatomy"], prefix="/anatomy")

VERSION = "4.0.0"


class AnatomyPresetListItem(OPModel):
    name: str
    primary: bool
    version: str


class AnatomyPresetListModel(OPModel):
    presets: list[AnatomyPresetListItem]


@router.get("/schema")
def get_anatomy_schema():
    """Returns the anatomy JSON schema.

    The schema is used to display the anatomy preset editor form.
    """
    return AnatomyPreset.schema()


@router.get("/presets")
async def get_anatomy_presets() -> AnatomyPresetListModel:
    """Return a list of stored anatomy presets."""

    presets = []
    query = "SELECT * from anatomy_presets ORDER BY name, version"
    async for row in Postgres.iterate(query):
        presets.append(
            AnatomyPresetListItem(
                name=row["name"], primary=row["is_primary"], version=row["version"]
            )
        )
    return AnatomyPresetListModel(presets=presets)


@router.get(
    "/presets/{preset_name}",
    response_model=AnatomyPreset,
)
async def get_anatomy_preset(preset_name: str):
    """Returns the anatomy preset with the given name.

    Use `_` character as a preset name to return the default preset.
    """
    if preset_name == "_":
        tpl = AnatomyPreset()
        return tpl

    query = "SELECT * FROM anatomy_presets WHERE name = %s"
    async for row in Postgres.iterate(query):
        tpl = AnatomyPreset(**row["data"])
        return tpl

    raise NotFoundException(f"Anatomy preset {preset_name} not found.")


@router.put("/presets/{preset_name}")
async def update_anatomy_preset(preset_name: str, preset: AnatomyPreset):
    """Create/update an anatomy preset with the given name."""

    await Postgres.execute(
        """
        INSERT INTO anatomy_presets (name, version, data)
        VALUES ($1, $2, $3)
        ON CONFLICT (name, version) DO update
        SET data = $4
        """,
        (preset_name, VERSION, preset.dict(), preset.dict()),
    )
    return Response(status_code=200)


@router.post("/preset/{preset_name}/primary")
async def set_primary_preset(preset_name: str):
    """Set the given preset as the primary preset."""

    async with Postgres.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                UPDATE anatomy_presets
                SET is_primary = FALSE
                WHERE is_primary = TRUE
                """
            )
            await conn.execute(
                """
                UPDATE anatomy_presets
                SET is_primary = TRUE
                WHERE name = $1
                """,
                preset_name,
            )

    return Response(status_code=200)


@router.delete("/preset/{preset_name}")
async def delete_anatomy_preset(preset_name: str):
    """Delete the anatomy preset with the given name."""
    return Response(status_code=501)


class DeployRequestModel(OPModel):
    """The request model for the deploy endpoint."""

    project_name: str = Field(
        ...,
        description="The name of the project to deploy to.",
        example="superProject42",
    )
    preset: AnatomyPreset = Field(
        ...,
        description="The anatomy preset to deploy.",
    )


@router.post("/deploy")
def deploy_anatomy_preset(preset: AnatomyPreset):
    """Deploy the anatomy preset.

    Create a new project from the anatomy preset.
    """
    return Response(status_code=501)
