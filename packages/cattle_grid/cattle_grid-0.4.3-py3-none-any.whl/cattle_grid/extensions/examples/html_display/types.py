from pydantic import Field
from cattle_grid.model.common import WithActor


class NameActorMessage(WithActor):
    """Message for renaming an actor"""

    name: str = Field(description="Name for the actor", examples=["john"])
