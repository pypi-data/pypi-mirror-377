from pydantic import Field

from muck_out.validators import HtmlStringOrNone, IdFieldOrNone, UrlList

from .common import CommonAll


class ActorStub(CommonAll):
    """Describes an ActivityPub actor"""

    inbox: IdFieldOrNone = Field(
        None,
        examples=["https://actor.example/inbox"],
        description="The inbox of the actor",
    )

    outbox: IdFieldOrNone = Field(
        None,
        examples=["https://actor.example/outbox"],
        description="The outbox of the actor",
    )

    icon: dict | None = Field(
        None,
        examples=[{"type": "Image", "url": "https://actor.example/icon.png"}],
        description="The avatar of the actor",
    )

    summary: HtmlStringOrNone = Field(
        None,
        examples=["My Fediverse account"],
        description="Description of the actor",
    )

    name: HtmlStringOrNone = Field(
        None,
        examples=["Alice"],
        description="Display name of the actor",
    )

    also_known_as: list[str] | None = Field(
        None,
        examples=[["https://alice.example", "https://alice.example/profile"]],
        alias="alsoKnownAs",
        description="Other uris associated with the actor",
    )

    url: UrlList = Field(
        default=[],
        description="A list of urls that expand on the content of the object",
    )

    preferred_username: str | None = Field(
        None, examples=["john"], alias="preferredUsername"
    )

    # attachments: list[dict | PropertyValue] | None = Field(
    #     None, description="""attachments ... currently used for property values"""
    # )
