from typing import Any

from nxtools import logging

from openpype.lib.postgres import Postgres

# The following parameters may be used:
# name, scope, type, title, default, example,
# gt, lt, regex, min_len, max_len, description
#
# Scope and type are required.
# All project attributes should have a default value
#
# Available types:
#   integer, float, string, boolean, list_of_strings
#
# Possible validation rules:
# - gt (for integers and floats)
# - lt (for integers and floats)
# - regex (for strings)


DEFAULT_ATTRIBUTES: dict[str, dict[str, Any]] = {
    "fps": {
        "scope": "P, F, V, R, T",
        "type": "float",
        "title": "FPS",
        "default": 25,
        "example": 25,
        "description": "Frame rate",
    },
    "resolutionWidth": {
        "scope": "P, F, V, R, T",
        "type": "integer",
        "title": "Width",
        "default": 1920,
        "example": 1920,
        "gt": 1,
        "lt": 50000,
        "description": "Horizontal resolution",
    },
    "resolutionHeight": {
        "scope": "P, F, V, R, T",
        "type": "integer",
        "title": "Height",
        "default": 1080,
        "example": 1080,
        "gt": 1,
        "lt": 50000,
        "description": "Vertical resolution",
    },
    "pixelAspect": {
        "scope": "P, F, V, R",
        "type": "float",
        "title": "Pixel aspect",
        "default": 1.0,
        "example": 1.0,
    },
    "clipIn": {
        "scope": "P, F, V, R",
        "type": "integer",
        "title": "Clip In",
        "default": 1,
        "example": 1,
    },
    "clipOut": {
        "scope": "P, F, V, R",
        "type": "integer",
        "title": "Clip Out",
        "default": 1,
        "example": 1,
    },
    "frameStart": {
        "scope": "P, F, V, R",
        "type": "integer",
        "title": "Start frame",
        "default": 1001,
        "example": 1001,
    },
    "frameEnd": {
        "scope": "P, F, V, R",
        "type": "integer",
        "title": "End frame",
        "default": 1001,
    },
    "handleStart": {
        "scope": "P, F, V, R",
        "type": "integer",
        "title": "Handle start",
        "default": 0,
    },
    "handleEnd": {
        "scope": "P, F, V, R",
        "type": "integer",
        "title": "Handle end",
        "default": 0,
    },
    "fullName": {
        "scope": "U",
        "type": "string",
        "title": "Full name",
        "example": "Jane Doe",
    },
    "email": {
        "scope": "U",
        "type": "string",
        "title": "E-Mail",
        "example": "jane.doe@openpype.cloud",
    },
    "avatarUrl": {
        "scope": "U",
        "type": "string",
        "title": "Avatar URL",
    },
    "subsetGroup": {
        "scope": "S",
        "type": "string",
        "title": "Subset group",
    },
    "intent": {
        "scope": "V",
        "type": "string",
        "title": "Intent",
    },
    "source": {
        "scope": "V",
        "type": "string",
        "title": "Source",
    },
    "comment": {
        "scope": "V",
        "type": "string",
        "title": "Comment",
    },
    "machine": {
        "scope": "V",
        "type": "string",
        "title": "Machine",
        "example": "workstation42",
    },
    "families": {
        "scope": "V",
        "type": "list_of_strings",
        "title": "Families",
    },
    "colorSpace": {
        "scope": "V",
        "type": "string",
        "title": "Color space",
        "example": "rec709",
    },
    "path": {
        "scope": "R",
        "type": "string",
        "title": "Path",
    },
    "template": {
        "scope": "R",
        "type": "string",
        "title": "Template",
    },
    "extension": {
        "scope": "R",
        "type": "string",
        "title": "File extension",
    },
}


async def deploy_attributes() -> None:
    await Postgres.execute("DELETE FROM public.attributes")

    position = 0
    for name, tdata in DEFAULT_ATTRIBUTES.items():
        try:
            scope = [
                {
                    "p": "project",
                    "u": "user",
                    "f": "folder",
                    "t": "task",
                    "s": "subset",
                    "v": "version",
                    "r": "representation",
                }[k.strip().lower()]
                for k in tdata["scope"].split(",")
            ]
        except KeyError:
            logging.error(f"Unknown scope specified on {name}. Skipping")
            continue

        if tdata["type"] not in [
            "integer",
            "float",
            "string",
            "boolean",
            "list_of_strings",
        ]:
            logging.error(f"Unknown type sepecified on {name}. Skipping.")
            continue

        data = {
            "type": tdata["type"],
            "title": tdata.get("title", name.capitalize()),
        }

        for key in ["default", "example", "regex", "description", "gt", "lt"]:
            if (value := tdata.get(key)) is not None:
                data[key] = value

        await Postgres.execute(
            """
            INSERT INTO public.attributes
                (name, position, scope, builtin, data)
            VALUES
                ($1, $2, $3, TRUE, $4)
            """,
            name,
            position,
            scope,
            data,
        )
        position += 1
