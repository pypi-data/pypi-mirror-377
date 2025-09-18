from unittest.mock import MagicMock

import pytest

from .config import HtmlDisplayConfiguration
from .publisher import Publisher


@pytest.fixture
def publisher():
    return Publisher(
        actor=MagicMock(actor="http://actor.test/", name="name"),
        config=HtmlDisplayConfiguration(),
    )


def test_create_html_link(publisher):
    result = publisher.create_html_link()

    assert isinstance(result, dict)


def test_update_object(publisher):
    obj = {}
    publisher.update_object(obj)

    assert isinstance(obj.get("id"), str)
    assert isinstance(obj.get("url"), list)
