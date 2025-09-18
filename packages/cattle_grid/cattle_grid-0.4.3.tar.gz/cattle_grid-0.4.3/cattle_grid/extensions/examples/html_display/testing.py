from unittest.mock import AsyncMock
import pytest

from cattle_grid.extensions.testing import with_test_broker_for_extension
from cattle_grid.model import ActivityMessage
from cattle_grid.dependencies.globals import global_container
from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.extensions.util import lifespan_for_sql_alchemy_base_class
from .models import Base
from . import extension


@pytest.fixture(autouse=True)
async def create_tables(sql_engine_for_tests):
    lifespan = lifespan_for_sql_alchemy_base_class(Base)
    async with lifespan(sql_engine_for_tests):
        yield


@pytest.fixture
def mock_publish_activity():
    return AsyncMock()


@pytest.fixture
def mock_publish_object():
    return AsyncMock()


@pytest.fixture
async def test_broker(mock_publish_activity, mock_publish_object):
    extension.configure({})

    async with with_test_broker_for_extension(
        [extension],
        {
            "publish_activity": mock_publish_activity,
            "publish_object": mock_publish_object,
        },
    ) as tbr:
        yield tbr


@pytest.fixture
async def published_object(actor_for_test, test_broker, mock_publish_activity):
    obj = {
        "type": "Note",
        "to": ["as:Public"],
        "content": "I <3 milk!",
        "attributedTo": actor_for_test.actor_id,
    }

    await test_broker.publish(
        ActivityMessage(actor=actor_for_test.actor_id, data=obj),
        routing_key="html_display_publish_object",
        exchange=global_container.exchange,
    )

    mock_publish_activity.assert_awaited_once()

    args = mock_publish_activity.await_args

    activity = args[1]["data"]

    assert activity["type"] == "Create"

    return activity["object"]
