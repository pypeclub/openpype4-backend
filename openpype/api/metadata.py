VERSION = "0.0.1"

app_meta = {
    "title": "OpenPype server",
    "description": "Open VFX and Animation pipeline server",
    "version": VERSION,
    "contact": {
        "name": "Pype Club",
        "email": "info@pype.club",
        "url": "https://openpype.io",
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    "terms_of_service": "https://pype.club/terms",
}


tags_meta = [
    {
        "name": "Authentication",
        "description": """
Authentication endpoints
        """,
    },
    {
        "name": "Projects",
        "description": """
Project is a collection of folders and other entities.
Each project has a unique name, which is used as its identifier.

To address an entity within the project, you need to provide
both the project name and the entity ID.
        """,
    },
    {
        "name": "Folders",
        "description": """
Endpoints for managing folders.
        """,
    },
]
