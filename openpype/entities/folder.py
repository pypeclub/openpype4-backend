import time
from typing import Any

from nxtools import logging

from openpype.access.utils import ensure_entity_access
from openpype.entities.core import ProjectLevelEntity, attribute_library
from openpype.entities.models import ModelSet
from openpype.exceptions import (
    ConstraintViolationException,
    ForbiddenException,
    NotFoundException,
)
from openpype.lib.postgres import Postgres
from openpype.types import ProjectLevelEntityType
from openpype.utils import EntityID, SQLTool, dict_exclude


class FolderEntity(ProjectLevelEntity):
    entity_type: ProjectLevelEntityType = "folder"
    model: ModelSet = ModelSet("folder", attribute_library["folder"])

    @classmethod
    async def load(
        cls,
        project_name: str,
        entity_id: str,
        transaction=None,
        for_update=False,
    ) -> "FolderEntity":
        """Load a folder from the database by its project name and IDself.

        This is reimplemented, because we need to select dynamic
        attribute hierarchy.path along with the base data and
        the attributes inherited from parent entities.
        """
        project_name = project_name.lower()

        if EntityID.parse(entity_id) is None:
            raise ValueError(f"Invalid {cls.entity_type} ID specified")

        query = f"""
            SELECT
                f.id as id,
                f.name as name,
                f.folder_type as folder_type,
                f.parent_id as parent_id,
                f.thumbnail_id as thumbnail_id,
                f.attrib as attrib,
                f.data as data,
                f.active as active,
                f.created_at as created_at,
                f.updated_at as updated_at,
                h.path as path,
                ia.attrib AS inherited_attrib,
                p.attrib AS project_attrib
            FROM project_{project_name}.folders as f
            INNER JOIN
                project_{project_name}.hierarchy as h
                ON f.id = h.id
            LEFT JOIN
                project_{project_name}.exported_attributes as ia
                ON f.parent_id = ia.folder_id
            INNER JOIN public.projects as p
                ON p.name ILIKE $2
            WHERE f.id=$1
            {'FOR UPDATE OF f'
                if transaction and for_update else ''
            }
            """

        try:
            async for record in Postgres.iterate(query, entity_id, project_name):
                attrib = record["project_attrib"] or {}
                if (ia := record["inherited_attrib"]) is not None:
                    attrib.update(ia)
                elif record["parent_id"] is not None:
                    logging.warning(
                        f"Folder {record['path']} does not have inherited attributes."
                        "this shouldn't happen"
                    )
                attrib.update(record["attrib"])
                own_attrib = list(record["attrib"].keys())
                payload = {**record, "attrib": attrib}
                return cls.from_record(
                    project_name=project_name,
                    payload=payload,
                    validate=False,
                    own_attrib=own_attrib,
                )
        except Postgres.UndefinedTableError:
            raise NotFoundException(f"Project {project_name} not found")
        raise NotFoundException("Entity not found")

    async def save(self, transaction=None) -> bool:
        """Save the folder to the database.

        This overriden method also clears exported_attributes,
        which is then repopulated during commit.
        """

        commit = not transaction
        transaction = transaction or Postgres

        attrib = {}
        for key in self.own_attrib:
            if (value := getattr(self.attrib, key)) is not None:
                attrib[key] = value

        if self.exists:
            # Update existing entity

            # Delete all affected exported attributes
            # we will re-populate all non-existent records in the commit

            # TODO: do not delete when attributes don't change
            await transaction.execute(
                f"""
                DELETE FROM project_{self.project_name}.exported_attributes
                WHERE path LIKE '{self.path}%'
                """
            )

            await transaction.execute(
                *SQLTool.update(
                    f"project_{self.project_name}.{self.entity_type}s",
                    f"WHERE id = '{self.id}'",
                    name=self.name,
                    folder_type=self.folder_type,
                    parent_id=self.parent_id,
                    thumbnail_id=self.thumbnail_id,
                    attrib=attrib,
                    updated_at=time.time(),
                )
            )

        else:
            # Create a new entity
            try:
                await transaction.execute(
                    *SQLTool.insert(
                        f"project_{self.project_name}.{self.entity_type}s",
                        **dict_exclude(self.dict(exclude_none=True), ["own_attrib"]),
                    )
                )
            except Postgres.ForeignKeyViolationError as e:
                raise ConstraintViolationException(e.detail)

            except Postgres.UniqueViolationError as e:
                raise ConstraintViolationException(e.detail)

        if commit:
            await self.commit(transaction)
        return True

    async def commit(self, transaction=None) -> None:
        """Refresh hierarchy materialized view on folder save."""

        transaction = transaction or Postgres

        await transaction.execute(
            f"""
            DELETE FROM project_{self.project_name}.thumbnails
            WHERE id = $1
            """,
            self.id,
        )
        await transaction.execute(
            f"""
            REFRESH MATERIALIZED VIEW CONCURRENTLY
            project_{self.project_name}.hierarchy
            """
        )

        query = f"""
            SELECT
                h.id as id,
                h.path as path,
                f.attrib as own_attrib,
                f.parent_id as parent_id,
                p.attrib as project_attrib,
                e.attrib as inherited_attrib
            FROM
                project_{self.project_name}.hierarchy AS h
            INNER JOIN
                project_{self.project_name}.folders AS f
                ON h.id = f.id
            LEFT JOIN
                project_{self.project_name}.exported_attributes AS e
                ON e.folder_id = f.parent_id
            INNER JOIN
                public.projects AS p
                ON p.name ILIKE '{self.project_name}'
            WHERE h.path NOT IN
                (SELECT path FROM project_{self.project_name}.exported_attributes)
            ORDER BY h.path ASC
        """

        cache: dict[str, dict[str, Any]] = {}

        async for row in Postgres.iterate(query, transaction=transaction):
            parent_path = "/".join(row["path"].split("/")[:-1])
            attr: dict[str, Any] = {}
            if (inherited := row["inherited_attrib"]) is not None:
                attr |= inherited
            elif not row["parent_id"]:
                attr |= row["project_attrib"]
            elif parent_path in cache:
                attr |= cache[parent_path]
            else:
                logging.error(f"Unable to build exported attrs for {row['path']}.")
                continue

            if row["own_attrib"] is not None:
                attr |= row["own_attrib"]

            cache[row["path"]] = attr
            await transaction.execute(
                f"""
                INSERT INTO project_{self.project_name}.exported_attributes
                (folder_id, path, attrib) VALUES ($1, $2, $3)
                """,
                row["id"],
                row["path"],
                attr,
            )

    async def get_versions(self, transaction=None):
        """Return of version ids associated with this folder."""
        query = f"""
            SELECT v.id as version_id
            FROM project_{self.project_name}.versions as v
            INNER JOIN project_{self.project_name}.subsets as s
                ON s.id = v.subset_id
            WHERE s.folder_id = $1
            """
        return [row["version_id"] async for row in Postgres.iterate(query, self.id)]

    async def ensure_create_access(self, user):
        """Check if the user has access to create a new entity.

        Raises FobiddenException if the user does not have access.
        Reimplements the method from the parent class, because in
        case of folders we need to check the parent folder.
        """
        if self.parent_id is None:
            if not user.is_manager:
                raise ForbiddenException("Only managers can create root folders")
        else:
            await ensure_entity_access(
                user,
                self.project_name,
                self.entity_type,
                self.parent_id,
                "create",
            )

    #
    # Properties
    #

    @property
    def parent_id(self) -> str | None:
        return self._payload.parent_id

    @parent_id.setter
    def parent_id(self, value: str) -> None:
        self._payload.parent_id = value

    @property
    def folder_type(self) -> str | None:
        return self._payload.folder_type

    @folder_type.setter
    def folder_type(self, value: str) -> None:
        self._payload.folder_type = value

    @property
    def thumbnail_id(self) -> str | None:
        return self._payload.thumbnail_id

    @thumbnail_id.setter
    def thumbnail_id(self, value: str) -> None:
        self._payload.thumbnail_id = value

    #
    # Read only properties
    #

    @property
    def path(self) -> str:
        return self._payload.path
