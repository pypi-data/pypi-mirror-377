import asyncio
from behave import given, then

from cattle_grid.extensions.examples.html_display.types import NameActorMessage


@given('"{alice}" sets her display name to "{alex}"')  # type: ignore
async def html_set_display_name(context, alice, alex):
    connection = context.connections[alice]
    alice_id = context.actors[alice].get("id")

    await connection.trigger(
        "html_display_name", NameActorMessage(actor=alice_id, name=alex).model_dump()
    )

    await asyncio.sleep(0.2)


@then("The profile contains an url")  # type: ignore
def profile_contains_url(context):
    urls = context.profile.get("url")

    print(urls)
    print(context.profile)

    assert isinstance(urls, list)
    assert len(urls) >= 1
