from typing import Any

from muck_out.transform.utils import remove_html
from muck_out.types import ActorStub, Actor
from muck_out.types.validated.actor import PropertyValue


def actor_stub(data: dict[str, Any]) -> ActorStub:
    """Returns the stub actor"""
    stub = ActorStub.model_validate(data)

    return stub


def normalize_property_value(data: dict[str, Any]) -> PropertyValue | dict[str, Any]:
    if data.get("type") == "PropertyValue":
        return PropertyValue.model_validate(
            {
                "name": remove_html(data.get("name")),
                "value": remove_html(data.get("value")),
            }
        )
    return data


def normalize_actor(data: dict[str, Any]) -> Actor | None:
    """Normalizes an ActivityPub actor"""

    try:
        stub = actor_stub(data)

        return Actor.model_validate(stub.model_dump(by_alias=True))

    except Exception:
        return None
