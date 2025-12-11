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
from openapi_server.models.event_subscription_input import EventSubscriptionInput


router = APIRouter()


@router.post(
    "/hub",
    responses={
        201: {"model": EventSubscription, "description": "Subscribed"},
        400: {"model": Error, "description": "Bad Request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method Not allowed"},
        409: {"model": Error, "description": "Conflict"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["events subscription"],
    summary="Register a listener",
    response_model_by_alias=True,
)
async def register_listener(
    data: EventSubscriptionInput = Body(None, description="Data containing the callback endpoint to deliver the information"),
) -> EventSubscription:
    """Sets the communication endpoint address the service instance must use to deliver information about its health state, execution state, failures and metrics."""
    ...


@router.delete(
    "/hub/{id}",
    responses={
        204: {"description": "Deleted"},
        400: {"model": Error, "description": "Bad request"},
        401: {"model": Error, "description": "Unauthorized"},
        403: {"model": Error, "description": "Forbidden"},
        404: {"model": Error, "description": "Not Found"},
        405: {"model": Error, "description": "Method not allowed"},
        500: {"model": Error, "description": "Internal Server Error"},
    },
    tags=["events subscription"],
    summary="Unregister a listener",
    response_model_by_alias=True,
)
async def unregister_listener(
    #id: str = Path(None, description="The id of the registered listener"),
    id: str = Path( description="The id of the registered listener"),
) -> None:
    """Resets the communication endpoint address the service instance must use to deliver information about its health state, execution state, failures and metrics."""
    ...
