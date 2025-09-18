import jinja2
from fastapi.templating import Jinja2Templates

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from cattle_grid.dependencies.fastapi import SqlSession
from cattle_grid.extensions.examples.html_display.format import format_actor_profile
from cattle_grid.extensions.examples.html_display.models import PublishedObject
from cattle_grid.tools.fastapi import ActivityResponse

from .fastapi_dependencies import (
    ActorProfile,
    PublishedObjectForUUID,
    PublishingActorForName,
)

templates = Jinja2Templates(
    env=jinja2.Environment(auto_reload=True, loader=jinja2.PackageLoader(__name__)),
)

router = APIRouter()


@router.get("/")
async def get_index():
    return "html extension"


@router.get("/object/{uuid}", response_class=ActivityResponse)
async def get__object(obj: PublishedObjectForUUID):
    return obj.data


@router.get("/html/{actor_name}", response_class=HTMLResponse)
@router.get("/html/{actor_name}/", response_class=HTMLResponse)
async def get_actor_html(
    actor: PublishingActorForName,
    profile: ActorProfile,
    request: Request,
    session: SqlSession,
):
    published_objects = await session.scalars(
        select(PublishedObject)
        .where(PublishedObject.actor == actor.actor)
        .order_by(PublishedObject.create_date.desc())
        .limit(10)
    )

    posts = [
        {
            "body": x.data.get("content"),
            "date": x.data.get("published"),
            "id": str(x.id),
        }
        for x in published_objects
    ]

    return templates.TemplateResponse(
        request,
        name="index.html.j2",
        context={
            "name": actor.name,
            "profile": format_actor_profile(profile),
            "posts": posts,
        },
    )


@router.get("/html/{actor_name}/{uuid}", response_class=HTMLResponse)
async def get_object_html(
    actor: PublishingActorForName,
    obj: PublishedObjectForUUID,
    request: Request,
):
    if actor.actor != obj.actor:
        raise HTTPException(404)

    return templates.TemplateResponse(
        request,
        name="object.html",
        context={"name": actor.name, "content": obj.data["content"]},
    )
