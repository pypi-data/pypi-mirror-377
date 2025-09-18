import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from .storage import publishing_actor_for_actor_id

from .testing import *  # noqa

from . import extension


@pytest.fixture
def test_client():
    app = FastAPI()
    app.include_router(extension.api_router, prefix="/html_display")

    return TestClient(app)


def test_get_html_object(test_client):
    response = test_client.get("/html/name/2fd16a00-309b-4f3a-9d91-aa9516e59c1f")
    assert response.status_code == 404


def test_get_object_not_found(test_client):
    response = test_client.get(
        "/html_display/object/2fd16a00-309b-4f3a-9d91-aa9516e59c1f"
    )
    assert response.status_code == 404


def test_get_object(test_client, published_object):
    assert published_object

    object_id = published_object["id"]

    response = test_client.get(object_id)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/activity+json"


def test_get_object_html(test_client, published_object):
    assert published_object
    url_in_obj = published_object.get("url", [])
    url = url_in_obj[0].get("href").replace("@", "html_display/html/")

    response = test_client.get(url)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


async def test_get_object_html_not_found(
    sql_session_for_test, test_client, actor_for_test
):
    actor = await publishing_actor_for_actor_id(
        sql_session_for_test, actor_for_test.actor_id
    )
    await sql_session_for_test.commit()

    response = test_client.get(
        f"/html_display/html/{actor.name}/2fd16a00-309b-4f3a-9d91-aa9516e59c1f"
    )

    assert response.status_code == 404


async def test_get_object_html_actor_mismatch(
    sql_session_for_test, test_client, published_object
):
    actor = await publishing_actor_for_actor_id(sql_session_for_test, "some_id")
    await sql_session_for_test.commit()

    response = test_client.get(
        f"/html_display/html/{actor.name}/" + published_object.get("id").split("/")[-1]
    )

    assert response.status_code == 404
