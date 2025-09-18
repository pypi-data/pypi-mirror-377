from dataclasses import dataclass, field
from uuid import UUID

from bovine.activitystreams.utils import as_list
from uuid6 import uuid7


from .config import HtmlDisplayConfiguration
from .models import PublishingActor


@dataclass
class Publisher:
    """Class for manipulating objects being published"""

    actor: PublishingActor
    config: HtmlDisplayConfiguration
    uuid: UUID = field(default_factory=uuid7)

    def update_object(self, obj):
        obj_id = self.config.url_start(self.actor.actor) + str(self.uuid)
        obj["id"] = obj_id
        self._add_url_to_obj(obj)

    def _add_url_to_obj(self, obj: dict):
        url_list = as_list(obj.get("url", []))

        url = (
            self.config.html_url_start(self.actor.actor)
            + self.actor.name
            + "/"
            + str(self.uuid)
        )

        obj["url"] = url_list + [self.create_html_link(url)]

    def create_html_link(self, url: str | None = None):
        if url is None:
            url = self.actor.actor_id + "#html"
        return {"type": "Link", "mediaType": "text/html", "href": url}
