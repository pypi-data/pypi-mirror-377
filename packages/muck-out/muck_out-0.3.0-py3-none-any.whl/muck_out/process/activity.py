"""Routines to normalize an ActivityPub activity or object.

The routines here take a dictionary and turn them into another
one."""

import logging

from bovine.activitystreams.utils import id_for_object

from muck_out.types import Activity, ActivityStub
from muck_out.transform.list_utils import list_from_value

from .object import normalize_object

from .base import normalize_to, normalize_id

logger = logging.getLogger(__name__)


def activity_stub(data: dict) -> ActivityStub:
    """Builds the activity stub"""
    return ActivityStub.model_validate(data)


def normalize_activity(activity: dict, actor: str | None = None) -> Activity:
    """
    Normalizes activities.

    :param activity: The activity being normalized
    :param actor: Actor receiving this activity
    :returns:
    """
    try:
        obj = activity.get("object")
        if isinstance(obj, dict):
            try:
                obj = normalize_object(obj)
            except Exception:
                if isinstance(obj, dict):
                    obj = obj.get("id")

        return Activity.model_validate(
            {
                "@context": activity.get("@context"),
                "id": normalize_id(activity),
                "type": activity.get("type"),
                "actor": id_for_object(activity.get("actor")),
                "object": obj,
                "to": normalize_to(activity.get("to"), actor),
                "cc": list_from_value(activity.get("cc")),
                "published": activity.get("published"),
                "target": activity.get("target"),
                "content": activity.get("content"),
            }
        )
    except Exception as e:
        # logger.exception(e)
        # logger.info(activity)

        raise e
