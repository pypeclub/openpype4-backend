"""Entity field definitions.

This module contains the top-level field definitions for the entities.
Each field has its own column in the database.

Fields `id`, `created_at` and `updated_at` as well as `attrib` and `data`
are not part of the definition, since they are added
automatically by ModelSet class.

See .generator.FieldDefinition model for more information on specifiing
field parameters.
"""

from openpype.types import ENTITY_ID_EXAMPLE, ENTITY_ID_REGEX, NAME_REGEX

project_fields = [
    # Name is not here, since it's added by ModelSet class
    # (it is used as a primary key)
    {
        "name": "code",
        "type": "string",
        "regex": NAME_REGEX,
        "example": "prj",
        "title": "Project code",
        "required": True,
    },
    {
        "name": "library",
        "type": "boolean",
        "default": False,
    },
    {
        "name": "folder_types",
        "type": "dict",
        "default": {},
        "title": "Folder types",
        "example": {
            "Asset": {"icon": "asset"},
            "Shot": {"icon": "shot"},
            "Sequence": {"icon": "sequence"},
        },
    },
    {
        "name": "task_types",
        "type": "dict",
        "default": {},
        "title": "Task types",
        "example": {
            "Rigging": {},
            "Animation": {},
        },
    },
    {
        "name": "config",
        "type": "dict",
        "default": {},
        "title": "Project config",
    },
]


folder_fields = [
    {
        "name": "name",
        "type": "string",
        "required": True,
        "title": "Folder name",
        "regex": NAME_REGEX,
        "example": "bush",
    },
    {
        "name": "folder_type",
        "type": "string",
        "required": False,
        "title": "Folder type",
        "example": "Asset",
    },
    {
        "name": "parent_id",
        "type": "string",
        "title": "Parent ID",
        "description": "Parent folder ID in the hierarchy",
        "regex": ENTITY_ID_REGEX,
        "example": ENTITY_ID_EXAMPLE,
    },
    {
        "name": "thumbnail_id",
        "type": "string",
        "title": "Thumbnail ID",
        "required": False,
        "regex": ENTITY_ID_REGEX,
        "example": ENTITY_ID_EXAMPLE,
    },
    {
        "name": "path",
        "type": "string",
        "title": "Path",
        "example": "assets/characters/st_javelin",
        "dynamic": True,
    },
]


task_fields = [
    {
        "name": "name",
        "type": "string",
        "required": True,
        "title": "Folder ID",
        "regex": NAME_REGEX,
        "example": "modeling",
    },
    {
        "name": "task_type",
        "type": "string",
        "required": True,
        "title": "Task type",
        "example": "Modeling",
    },
    {
        "name": "assignees",
        "type": "list_of_strings",
        "title": "Assignees",
        "description": "List of users assigned to the task",
        "example": ["john_doe", "jane_doe"],
    },
    {
        "name": "folder_id",
        "type": "string",
        "title": "Folder ID",
        "description": "Folder ID",
        "regex": ENTITY_ID_REGEX,
        "example": ENTITY_ID_EXAMPLE,
    },
]


subset_fields = [
    {
        "name": "name",
        "type": "string",
        "required": True,
        "description": "Name of the subset",
        "regex": NAME_REGEX,
        "example": "modelMain",
    },
    {
        "name": "folder_id",
        "type": "string",
        "required": True,
        "title": "Folder ID",
        "description": "ID of the parent folder",
        "regex": ENTITY_ID_REGEX,
        "example": ENTITY_ID_EXAMPLE,
    },
    {
        "name": "family",
        "type": "string",
        "required": True,
        "title": "Family",
        "description": "Subset family",
        "regex": NAME_REGEX,
        "example": "model",
    },
]


version_fields = [
    {
        "name": "version",
        "type": "integer",
        "required": True,
        "title": "Version",
        "description": "Version number",
        "example": 1,
    },
    {
        "name": "subset_id",
        "type": "string",
        "required": True,
        "title": "Subset ID",
        "description": "ID of the parent subset",
        "regex": ENTITY_ID_REGEX,
        "example": ENTITY_ID_EXAMPLE,
    },
    {
        "name": "task_id",
        "type": "string",
        "required": False,
        "title": "Task ID",
        "description": "",
        "regex": ENTITY_ID_REGEX,
        "example": ENTITY_ID_EXAMPLE,
    },
    {
        "name": "thumbnail_id",
        "type": "string",
        "title": "Thumbnail ID",
        "required": False,
        "regex": ENTITY_ID_REGEX,
        "example": ENTITY_ID_EXAMPLE,
    },
    {
        "name": "author",
        "type": "string",
        "regex": NAME_REGEX,
        "example": "john_doe",
    },
]


representation_fields = [
    {
        "name": "name",
        "type": "string",
        "required": True,
        "title": "Name",
        "description": "The name of the representation",
        "example": "ma",
        "regex": NAME_REGEX,
    },
    {
        "name": "version_id",
        "type": "string",
        "required": True,
        "title": "Version ID",
        "description": "ID of the parent version",
        "regex": ENTITY_ID_REGEX,
        "example": ENTITY_ID_EXAMPLE,
    },
]
