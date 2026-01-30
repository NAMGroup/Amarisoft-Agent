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
from openapi_server.models.resource import Resource
from openapi_server.models.resource_create import ResourceCreate
from openapi_server.models.resource_update import ResourceUpdate

import uuid
from  openapi_server import main
from fastapi.responses import JSONResponse
router = APIRouter()


@router.post(
    "/resource",
    responses={
        201: {"model": Resource, "description": "Created"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["resource"],
    summary="Creates a Resource",
    response_model_by_alias=True,
)
async def create_resource(
    resource: ResourceCreate = Body(None, description="The Resource to be created"),
) -> Resource:
    """This operation creates a Resource entity."""
    ...


@router.delete(
    "/resource/{id}",
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
    tags=["resource"],
    summary="Deletes a Resource",
    response_model_by_alias=True,
)
async def delete_resource(
    id: str = Path(None, description="Identifier of the Resource"),
) -> None:
    """This operation deletes a Resource entity."""
    ...


@router.get(
    "/resource",
    responses={
        200: {"model": List[Resource], "description": "Success"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["resource"],
    summary="List or find Resource objects",
    response_model_by_alias=True,
)
async def list_resource(
    fields: str = Query(None, description="Comma-separated properties to be provided in response"),
    offset: int = Query(None, description="Requested index for start of resources to be provided in response"),
    limit: int = Query(None, description="Requested number of resources to be provided in response"),
) -> List[Resource]:
    """This operation list or find Resource entities"""
    ...


@router.patch(
    "/resource/{id}",
    responses={
        200: {"model": Resource, "description": "Updated"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["resource"],
    summary="Updates partially a Resource",
    response_model_by_alias=True,
)
async def patch_resource(
    id: str = Path(None, description="Identifier of the Resource"),
    resource: ResourceUpdate = Body(None, description="The Resource to be updated"),
) -> Resource:
    """This operation updates partially a Resource entity."""
    ...
    print("===>")
     #Basically we have to check whether there is an action ResourceCharacteristic
    #Lets create a temp Resource
    #TODO: Check for each member value (if exists)
    newResource=Resource(id=str(uuid.uuid1()),href="")
    newResource.category=resource.category
    newResource.name=resource.name
    newResource.description=resource.description
    
    newResource.resource_characteristic=resource.resource_characteristic
    newResource.activation_feature=resource.activation_feature
    action_present=None
    print(newResource)

    if  newResource.activation_feature:
        main.myAgent.action_params=None
        main.myAgent.action_present=None
        for activation_feature in newResource.activation_feature:
            if activation_feature.name==main.myAgent.profile:
                for feature_char in activation_feature.feature_characteristic:
                    if(feature_char.name=="action"):
                        main.myAgent.action_present=feature_char.value["value"]
                    #Check if there are parameters
                    if(feature_char.name=="action_parameters"):
                        main.myAgent.action_params=feature_char.value["value"]


    if main.myAgent.profile_actions is not None:
        if main.myAgent.action_present  not in main.myAgent.profile_actions:
            print("Yeah I do not how to do this.... ")
            print(main.myAgent.action_present)
            return JSONResponse(status_code=405, content={"code": "405", "reason":"Command Not Found", "message": "Command not present", "status":"", "reference_error":"", "base_type":"","schema_location":"", "type":""})

            return None
        print(main.myAgent.profile_actions)
        print(main.myAgent.callbacks.callbacks)
        # if main.myAgent.profile_actions[main.myAgent.action_present] is None:
        if main.myAgent.action_present in main.myAgent.profile_actions:
            callback_result = main.myAgent.callbacks.process_event(main.myAgent.action_present, main.myAgent.CMD_DEBUG_MODE, main.myAgent.action_params)
            if callback_result is False:
                print("No callback registered")
                return JSONResponse(status_code=405, content={"code": "405", "reason":"Command Callback Not Found", "message": "Command Callback not present", "status":"", "reference_error":"", "base_type":"","schema_location":"", "type":""})
            else:
                # Success - return callback result if it exists, otherwise return the resource
                return callback_result if callback_result is not None else newResource

        else:
            print("Oooops")


@router.get(
    "/resource/{id}",
    responses={
        200: {"model": Resource, "description": "Success"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["resource"],
    summary="Retrieves a Resource by ID",
    response_model_by_alias=True,
)
async def retrieve_resource(
    id: str = Path(None, description="Identifier of the Resource"),
    fields: str = Query(None, description="Comma-separated properties to provide in response"),
) -> Resource:
    """This operation retrieves a Resource entity. Attribute selection is enabled for all first level attributes."""
    ...
