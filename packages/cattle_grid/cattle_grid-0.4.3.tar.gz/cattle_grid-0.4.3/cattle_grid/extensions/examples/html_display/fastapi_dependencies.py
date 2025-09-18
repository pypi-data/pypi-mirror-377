import uuid
import logging

from typing import Annotated
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from cattle_grid.activity_pub.actor import actor_to_object
from cattle_grid.database.activity_pub_actor import Actor
from cattle_grid.dependencies.fastapi import SqlSession
from .models import PublishedObject, PublishingActor

logger = logging.getLogger(__name__)


async def publishing_actor_for_name(session: SqlSession, actor_name: str):
    actor = await session.scalar(
        select(PublishingActor).where(PublishingActor.name == actor_name)
    )

    if not actor:
        raise HTTPException(404)

    return actor


PublishingActorForName = Annotated[PublishingActor, Depends(publishing_actor_for_name)]
"""Returns the publishing actor"""


async def published_object(session: SqlSession, uuid: uuid.UUID):
    obj = await session.scalar(
        select(PublishedObject).where(PublishedObject.id == uuid)
    )
    if not obj:
        raise HTTPException(404)

    return obj


PublishedObjectForUUID = Annotated[PublishedObject, Depends(published_object)]
"""Returns the published object"""


async def get_actor_profile(
    session: SqlSession, publishing_actor: PublishingActorForName
):
    actor = await session.scalar(
        select(Actor)
        .where(Actor.actor_id == publishing_actor.actor)
        .options(joinedload(Actor.identifiers))
    )

    if actor is None:
        logger.warning(
            "Could not find actor for publishing actor with name %s",
            publishing_actor.name,
        )
        raise HTTPException(404)

    return actor_to_object(actor)


ActorProfile = Annotated[dict, Depends(get_actor_profile)]
"""Returns the actor profile"""
