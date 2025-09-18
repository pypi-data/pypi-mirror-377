from typing import Annotated
from fastapi import Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ActivityResponse(JSONResponse):
    """Response that ensures the content-type is
    "application/activity+json"
    """

    media_type = "application/activity+json"


class APHeaders(BaseModel):
    """Headers every request should have. These should be added by the remote proxy."""

    x_cattle_grid_requester: str | None = Field(
        default=None, description="URI of the actor making the request"
    )
    x_cattle_grid_should_serve: str | None = Field(
        default=None, description="Type of content cattle_grid should serve"
    )
    x_ap_location: str = Field(description="URI of the resource being retrieved")


ActivityPubHeaders = Annotated[APHeaders, Header()]
"""Annotation to evaluate the [APHeaders][cattle_grid.tools.fastapi.APHeaders]"""
