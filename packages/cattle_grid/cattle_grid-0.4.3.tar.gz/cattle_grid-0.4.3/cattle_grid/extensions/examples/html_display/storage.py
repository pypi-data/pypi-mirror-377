import random
import string
import uuid


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cattle_grid.extensions.examples.html_display.models import PublishingActor


def new_name():
    return "".join(random.choices(string.ascii_letters, k=12))


async def publishing_actor_for_actor_id(session: AsyncSession, actor_id: str):
    actor = await session.scalar(
        select(PublishingActor).where(PublishingActor.actor == actor_id)
    )
    if actor:
        return actor

    actor = PublishingActor(actor=actor_id, name=new_name())
    session.add(actor)
    return actor


async def object_for_name_and_uuid(session: AsyncSession, name: str, uuid: uuid.UUID):
    return None
