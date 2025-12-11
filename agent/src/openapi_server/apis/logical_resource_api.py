# coding: utf-8

from typing import Dict, List  # noqa: F401

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.models.error import Error
from openapi_server.models.logical_resource import LogicalResource
from openapi_server.models.logical_resource_create import LogicalResourceCreate
from openapi_server.models.logical_resource_update import LogicalResourceUpdate


router = APIRouter()


@router.post(
    "/logicalResource",
    responses={
        201: {"model": LogicalResource, "description": "Created"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["logicalResource"],
    summary="Creates a LogicalResource",
    response_model_by_alias=True,
)
async def create_logical_resource(
    logical_resource: LogicalResourceCreate = Body(None, description="The LogicalResource to be created"),
) -> LogicalResource:
    """This operation creates a LogicalResource entity."""
    ...


@router.delete(
    "/logicalResource/{id}",
    responses={
        204: {"description": "Deleted"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["logicalResource"],
    summary="Deletes a LogicalResource",
    response_model_by_alias=True,
)
async def delete_logical_resource(
    #id: str = Path(None, description="Identifier of the LogicalResource"),
    id: str = Path( description="Identifier of the LogicalResource"),
) -> None:
    """This operation deletes a LogicalResource entity."""
    ...


@router.get(
    "/logicalResource",
    responses={
        200: {"model": List[LogicalResource], "description": "Success"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["logicalResource"],
    summary="List or find LogicalResource objects",
    response_model_by_alias=True,
)
async def list_logical_resource(
    fields: str = Query(None, description="Comma-separated properties to be provided in response"),
    offset: int = Query(None, description="Requested index for start of resources to be provided in response"),
    limit: int = Query(None, description="Requested number of resources to be provided in response"),
) -> List[LogicalResource]:
    """This operation list or find LogicalResource entities"""
    ...


@router.patch(
    "/logicalResource/{id}",
    responses={
        200: {"model": LogicalResource, "description": "Updated"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["logicalResource"],
    summary="Updates partially a LogicalResource",
    response_model_by_alias=True,
)
async def patch_logical_resource(
    #id: str = Path(None, description="Identifier of the LogicalResource"),
    id: str = Path( description="Identifier of the LogicalResource"),
    logical_resource: LogicalResourceUpdate = Body(None, description="The LogicalResource to be updated"),
) -> LogicalResource:
    """This operation updates partially a LogicalResource entity."""
    ...


@router.get(
    "/logicalResource/{id}",
    responses={
        200: {"model": LogicalResource, "description": "Success"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["logicalResource"],
    summary="Retrieves a LogicalResource by ID",
    response_model_by_alias=True,
)
async def retrieve_logical_resource(
    #id: str = Path(None, description="Identifier of the LogicalResource"),
    id: str = Path( description="Identifier of the LogicalResource"),
    fields: str = Query(None, description="Comma-separated properties to provide in response"),
) -> LogicalResource:
    """This operation retrieves a LogicalResource entity. Attribute selection is enabled for all first level attributes."""
    ...


@router.put(
    "/logicalResource/{id}",
    responses={
        200: {"model": LogicalResource, "description": "Updated"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["logicalResource"],
    summary="Updates a LogicalResource",
    response_model_by_alias=True,
)
async def update_logical_resource(
    #id: str = Path(None, description="Identifier of the LogicalResource"),
    id: str = Path(description="Identifier of the LogicalResource"),
    logical_resource: LogicalResourceUpdate = Body(None, description="The LogicalResource to be updated"),
) -> LogicalResource:
    """This operation updates a LogicalResource entity."""
    ...
