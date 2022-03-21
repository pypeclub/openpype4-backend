from typing import Annotated

from strawberry.types import Info

from openpype.access.utils import folder_access_list
from openpype.utils import EntityID, SQLTool

from ..connections import FoldersConnection
from ..edges import FolderEdge
from ..nodes.folder import FolderNode
from .common import (
    ARGAfter,
    ARGBefore,
    ARGFirst,
    ARGIds,
    ARGLast,
    FieldInfo,
    argdesc,
    create_pagination,
    resolve,
)


async def get_folders(
    root,
    info: Info,
    first: ARGFirst = None,
    after: ARGAfter = None,
    last: ARGLast = None,
    before: ARGBefore = None,
    ids: ARGIds = None,
    parent_id: Annotated[
        str | None,
        argdesc(
            """
            ID of the parent folder.
            Use 'root' to get top level folders.
            """
        ),
    ] = None,
    folder_types: Annotated[
        list[str] | None, argdesc("List of folder types to filter by")
    ] = None,
    paths: Annotated[list[str] | None, argdesc("List of paths to filter by")] = None,
    path_ex: Annotated[str | None, argdesc("Match paths by regular expression")] = None,
    name: Annotated[
        str | None, argdesc("Text string to filter names by. Use `%` as wildcard.")
    ] = None,
    has_children: Annotated[
        bool | None, argdesc("Whether to filter by folders with children")
    ] = None,
    has_subsets: Annotated[
        bool | None, argdesc("Whether to filter by folders with subsets")
    ] = None,
    has_tasks: Annotated[
        bool | None, argdesc("Whether to filter by folders with tasks")
    ] = None,
) -> FoldersConnection:
    """Return a list of folders."""

    project_name = root.project_name
    fields = FieldInfo(info, ["folders.edges.node", "folder"])

    #
    # SQL
    #

    sql_columns = [
        "folders.id AS id",
        "folders.name AS name",
        "folders.active AS active",
        "folders.folder_type AS folder_type",
        "folders.parent_id AS parent_id",
        "folders.attrib AS attrib",
        "folders.created_at AS created_at",
        "folders.updated_at AS updated_at",
    ]

    sql_joins = []
    sql_group_by = ["folders.id"]
    sql_conditions = []
    sql_having = []

    use_hierarchy = (
        (paths is not None)
        or (path_ex is not None)
        or fields.has_any("path", "parents")
    )

    user = info.context["user"]
    access_list = await folder_access_list(user, project_name, "read")

    if access_list is not None:
        sql_conditions.append(f"path like ANY ('{{ {','.join(access_list)} }}')")
        use_hierarchy = True

    # We need to use children-join
    if (has_children is not None) or fields.has_any("childrenCount", "hasChildren"):
        sql_columns.append("COUNT(children.id) AS children_count")
        sql_joins.append(
            f"""
            LEFT JOIN
                project_{project_name}.folders AS children
                ON folders.id = children.parent_id
            """
        )

    if (has_subsets is not None) or fields.has_any("subsetsCount", "hasSubsets"):
        sql_columns.append("COUNT(subsets.id) AS subset_count")
        sql_joins.append(
            f"""
            LEFT JOIN
                project_{project_name}.subsets AS subsets
                ON folders.id = subsets.folder_id
            """
        )

    if (has_tasks is not None) or fields.has_any("tasksCount", "hasTasks"):
        sql_columns.append("COUNT(tasks.id) AS task_count")
        sql_joins.append(
            f"""
            LEFT JOIN
                project_{project_name}.tasks AS tasks
                ON folders.id = tasks.folder_id
            """
        )

    # We need to join hierarchy view
    if use_hierarchy:
        sql_columns.append("hierarchy.path AS path")
        sql_group_by.append("path")
        sql_joins.append(
            f"""
            LEFT JOIN
                project_{project_name}.hierarchy AS hierarchy
                ON folders.id = hierarchy.id
            """
        )

    #
    # Conditions
    #

    if ids:
        sql_conditions.append(f"folders.id IN {SQLTool.id_array(ids)}")

    if parent_id is not None:
        sql_conditions.append(
            "folders.parent_id IS NULL"
            if parent_id == "root"
            else f" folders.parent_id = '{EntityID.parse(parent_id)}'"
        )

    if folder_types is not None:
        sql_conditions.append(f"folders.folder_type in {SQLTool.array(folder_types)}")

    if name is not None:
        sql_conditions.append(f"folders.name ILIKE '{name}'")

    if has_subsets is not None:
        sql_having.append(
            "COUNT(subsets.id) > 0" if has_subsets else "COUNT(subsets.id) = 0"
        )

    if has_children is not None:
        sql_having.append(
            "COUNT(children.id) > 0" if has_children else "COUNT(children.id) = 0"
        )

    if has_tasks is not None:
        sql_having.append("COUNT(tasks.id) > 0" if has_tasks else "COUNT(tasks.id) = 0")

    if paths is not None:
        sql_conditions.append(f"hierarchy.path IN {SQLTool.array(paths)}")

    if path_ex is not None:
        sql_conditions.append(f"hierarchy.path ~ '{path_ex}'")

    #
    # Pagination
    #

    order_by = "id"
    pagination, paging_conds = create_pagination(order_by, first, after, last, before)
    sql_conditions.extend(paging_conds)

    #
    # Query
    #

    query = f"""
        SELECT
            {", ".join(sql_columns)}
        FROM
            project_{project_name}.folders AS folders
        {" ".join(sql_joins)}
        {SQLTool.conditions(sql_conditions)}
        GROUP BY {",".join(sql_group_by)}
        {SQLTool.conditions(sql_having).replace("WHERE", "HAVING", 1)}
        {pagination}
    """

    return await resolve(
        FoldersConnection,
        FolderEdge,
        FolderNode,
        project_name,
        query,
        first,
        last,
        context=info.context,
        order_by=order_by,
    )


async def get_folder(root, info: Info, id: str) -> FolderNode | None:
    """Return a folder node based on its ID"""
    if not id:
        return None
    connection = await get_folders(root, info, ids=[id])
    if not connection.edges:
        return None
    return connection.edges[0].node
