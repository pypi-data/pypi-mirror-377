from uuid import UUID

from .models import PublishingActor
from .storage import object_for_name_and_uuid, publishing_actor_for_actor_id

from .testing import *  # noqa


async def test_publishing_actor_for_actor_id(sql_session_for_test):
    actor_id = "http://actor.test/some/id"

    result = await publishing_actor_for_actor_id(sql_session_for_test, actor_id)

    assert isinstance(result, PublishingActor)
    assert result.actor == actor_id


async def test_publishing_actor_for_actor_id_returns_stored_actor(sql_session_for_test):
    actor_id = "http://actor.test/some/id"

    one = await publishing_actor_for_actor_id(sql_session_for_test, actor_id)

    await sql_session_for_test.commit()

    two = await publishing_actor_for_actor_id(sql_session_for_test, actor_id)

    assert one.name == two.name


async def test_object_for_name_and_uuid_not_found(sql_session_for_test):
    result = await object_for_name_and_uuid(
        sql_session_for_test, "name", UUID("2fd16a00-309b-4f3a-9d91-aa9516e59c1f")
    )

    assert result is None
