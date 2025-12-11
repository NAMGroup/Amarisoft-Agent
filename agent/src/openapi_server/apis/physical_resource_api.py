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
from openapi_server.models.physical_resource import PhysicalResource
from openapi_server.models.physical_resource_create import PhysicalResourceCreate
from openapi_server.models.physical_resource_update import PhysicalResourceUpdate


router = APIRouter()


@router.post(
    "/physicalResource",
    responses={
        201: {"model": PhysicalResource, "description": "Created"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["physicalResource"],
    summary="Creates a PhysicalResource",
    response_model_by_alias=True,
)
async def create_physical_resource(
    physical_resource: PhysicalResourceCreate = Body(None, description="The PhysicalResource to be created"),
) -> PhysicalResource:
    """This operation creates a PhysicalResource entity."""
    ...


@router.delete(
    "/physicalResource/{id}",
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
    tags=["physicalResource"],
    summary="Deletes a PhysicalResource",
    response_model_by_alias=True,
)
async def delete_physical_resource(
    #id: str = Path(None, description="Identifier of the PhysicalResource"),
    id: str = Path( description="Identifier of the PhysicalResource"),
) -> None:
    """This operation deletes a PhysicalResource entity."""
    ...


@router.get(
    "/physicalResource",
    responses={
        200: {"model": List[PhysicalResource], "description": "Success"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["physicalResource"],
    summary="List or find PhysicalResource objects",
    response_model_by_alias=True,
)
async def list_physical_resource(
    fields: str = Query(None, description="Comma-separated properties to be provided in response"),
    offset: int = Query(None, description="Requested index for start of resources to be provided in response"),
    limit: int = Query(None, description="Requested number of resources to be provided in response"),
) -> List[PhysicalResource]:
    """This operation list or find PhysicalResource entities"""
    ...


@router.patch(
    "/physicalResource/{id}",
    responses={
        200: {"model": PhysicalResource, "description": "Updated"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["physicalResource"],
    summary="Updates partially a PhysicalResource",
    response_model_by_alias=True,
)
async def patch_physical_resource(
    #id: str = Path(None, description="Identifier of the PhysicalResource"),
    id: str = Path(description="Identifier of the PhysicalResource"),
    physical_resource: PhysicalResourceUpdate = Body(None, description="The PhysicalResource to be updated"),
) -> PhysicalResource:
    """This operation updates partially a PhysicalResource entity."""
    ...


@router.get(
    "/physicalResource/{id}",
    responses={
        200: {"model": PhysicalResource, "description": "Success"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["physicalResource"],
    summary="Retrieves a PhysicalResource by ID",
    response_model_by_alias=True,
)
async def retrieve_physical_resource(
    #id: str = Path(None, description="Identifier of the PhysicalResource"),
    id: str = Path( description="Identifier of the PhysicalResource"),
    fields: str = Query(None, description="Comma-separated properties to provide in response"),
) -> PhysicalResource:
    """This operation retrieves a PhysicalResource entity. Attribute selection is enabled for all first level attributes."""
    ...
