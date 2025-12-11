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
from openapi_server.models.event_subscription import EventSubscription
from openapi_server.models.physical_resource_attribute_value_change_event import PhysicalResourceAttributeValueChangeEvent
from openapi_server.models.physical_resource_create_event import PhysicalResourceCreateEvent
from openapi_server.models.physical_resource_delete_event import PhysicalResourceDeleteEvent
from openapi_server.models.physical_resource_state_change_event import PhysicalResourceStateChangeEvent
from openapi_server.models.resource_attribute_value_change_event import ResourceAttributeValueChangeEvent
from openapi_server.models.resource_create_event import ResourceCreateEvent
from openapi_server.models.resource_delete_event import ResourceDeleteEvent
from openapi_server.models.resource_state_change_event import ResourceStateChangeEvent


router = APIRouter()


@router.post(
    "/listener/physicalResourceAttributeValueChangeEvent",
    responses={
        201: {"model": EventSubscription, "description": "Notified"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["notification listeners (client side)"],
    summary="Client listener for entity PhysicalResourceAttributeValueChangeEvent",
    response_model_by_alias=True,
)
async def listen_to_physical_resource_attribute_value_change_event(
    data: PhysicalResourceAttributeValueChangeEvent = Body(None, description="The event data"),
) -> EventSubscription:
    """Example of a client listener for receiving the notification PhysicalResourceAttributeValueChangeEvent"""
    ...


@router.post(
    "/listener/physicalResourceCreateEvent",
    responses={
        201: {"model": EventSubscription, "description": "Notified"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["notification listeners (client side)"],
    summary="Client listener for entity PhysicalResourceCreateEvent",
    response_model_by_alias=True,
)
async def listen_to_physical_resource_create_event(
    data: PhysicalResourceCreateEvent = Body(None, description="The event data"),
) -> EventSubscription:
    """Example of a client listener for receiving the notification PhysicalResourceCreateEvent"""
    ...


@router.post(
    "/listener/physicalResourceDeleteEvent",
    responses={
        201: {"model": EventSubscription, "description": "Notified"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["notification listeners (client side)"],
    summary="Client listener for entity PhysicalResourceDeleteEvent",
    response_model_by_alias=True,
)
async def listen_to_physical_resource_delete_event(
    data: PhysicalResourceDeleteEvent = Body(None, description="The event data"),
) -> EventSubscription:
    """Example of a client listener for receiving the notification PhysicalResourceDeleteEvent"""
    ...


@router.post(
    "/listener/physicalResourceStateChangeEvent",
    responses={
        201: {"model": EventSubscription, "description": "Notified"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["notification listeners (client side)"],
    summary="Client listener for entity PhysicalResourceStateChangeEvent",
    response_model_by_alias=True,
)
async def listen_to_physical_resource_state_change_event(
    data: PhysicalResourceStateChangeEvent = Body(None, description="The event data"),
) -> EventSubscription:
    """Example of a client listener for receiving the notification PhysicalResourceStateChangeEvent"""
    ...


@router.post(
    "/listener/resourceAttributeValueChangeEvent",
    responses={
        201: {"model": EventSubscription, "description": "Notified"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["notification listeners (client side)"],
    summary="Client listener for entity ResourceAttributeValueChangeEvent",
    response_model_by_alias=True,
)
async def listen_to_resource_attribute_value_change_event(
    data: ResourceAttributeValueChangeEvent = Body(None, description="The event data"),
) -> EventSubscription:
    """Example of a client listener for receiving the notification ResourceAttributeValueChangeEvent"""
    ...


@router.post(
    "/listener/resourceCreateEvent",
    responses={
        201: {"model": EventSubscription, "description": "Notified"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["notification listeners (client side)"],
    summary="Client listener for entity ResourceCreateEvent",
    response_model_by_alias=True,
)
async def listen_to_resource_create_event(
    data: ResourceCreateEvent = Body(None, description="The event data"),
) -> EventSubscription:
    """Example of a client listener for receiving the notification ResourceCreateEvent"""
    ...


@router.post(
    "/listener/resourceDeleteEvent",
    responses={
        201: {"model": EventSubscription, "description": "Notified"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["notification listeners (client side)"],
    summary="Client listener for entity ResourceDeleteEvent",
    response_model_by_alias=True,
)
async def listen_to_resource_delete_event(
    data: ResourceDeleteEvent = Body(None, description="The event data"),
) -> EventSubscription:
    """Example of a client listener for receiving the notification ResourceDeleteEvent"""
    ...


@router.post(
    "/listener/resourceStateChangeEvent",
    responses={
        201: {"model": EventSubscription, "description": "Notified"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["notification listeners (client side)"],
    summary="Client listener for entity ResourceStateChangeEvent",
    response_model_by_alias=True,
)
async def listen_to_resource_state_change_event(
    data: ResourceStateChangeEvent = Body(None, description="The event data"),
) -> EventSubscription:
    """Example of a client listener for receiving the notification ResourceStateChangeEvent"""
    ...
