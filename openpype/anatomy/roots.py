from pydantic import BaseModel, Field


class Root(BaseModel):
    name: str = Field(
        ...,
        title="Root name",
        regex="^[a-zA-Z0-9_]{1,}$",
    )

    windows: str = Field(
        "",
        title="Windows",
        regex=r'(?:[a-zA-Z]\:)?(?:\\[^\\/:*?"<>|\r\n]+)*',
    )

    linux: str = Field(
        "",
        title="Linux",
        regex="^(/[^/ ]*)+/?$",
    )

    darwin: str = Field(
        "",
        title="Darwin",
        regex="^(/[^/ ]*)+/?$",
    )


default_roots = [
    Root(
        name="work",
        windows="C:/projects",
        linux="/mnt/share/projects",
        darwin="/Volumes/projects",
    )
]