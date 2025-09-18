"""
Extension to add information to the context

See [FEP-f228](https://codeberg.org/fediverse/fep/src/branch/main/fep/f228/fep-f228.md)

This extension requires the muck out extension to be installed.
"""

import logging

from sqlalchemy import select
from uuid6 import uuid7
from cattle_grid.dependencies import CommittingSession
from cattle_grid.extensions import Extension

from muck_out.types.validated import Object


from cattle_grid.extensions.util import lifespan_for_sql_alchemy_base_class
from .models import Base, ContextInformation


logger = logging.getLogger(__name__)

extension = Extension(
    "context processor", __name__, lifespan=lifespan_for_sql_alchemy_base_class(Base)
)


@extension.transform(inputs=["parsed"], outputs=["context"])
async def transform(
    data: dict[str, dict], session: CommittingSession
) -> dict[str, dict]:
    parsed = data["parsed"]
    activity_type = parsed.get("activity", {}).get("type")

    if activity_type != "Create":
        return {"context": {}}

    try:
        obj = Object.model_validate(parsed.get("embeddedObject"))
    except Exception as e:
        logger.exception(e)
        return {"context": {}}

    in_context = await session.scalar(
        select(ContextInformation).where(ContextInformation.object_id == obj.id)
    )
    if in_context:
        return {"context": {"id": str(in_context.context_id)}}

    reply_for = await session.scalar(
        select(ContextInformation).where(
            ContextInformation.object_id == obj.in_reply_to
        )
    )

    if reply_for:
        context_id = reply_for.context_id
        session.add(
            ContextInformation(
                context_id=context_id, object_id=obj.id, parent_id=reply_for.object_id
            )
        )
    else:
        context_id = uuid7()
        session.add(ContextInformation(context_id=context_id, object_id=obj.id))

    return {"context": {"id": str(context_id)}}
