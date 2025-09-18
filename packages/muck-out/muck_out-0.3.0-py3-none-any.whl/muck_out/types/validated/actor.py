from pydantic import BaseModel, Field

from .common import CommonAll


class PropertyValue(BaseModel):
    """
    Key value pairs in the attachment of an actor
    as used by Mastodon
    """

    type: str = Field("PropertyValue", description="""Fixed type for serialization""")

    name: str = Field(
        examples=["Pronouns"],
        description="""
    Key of the value
    """,
    )

    value: str = Field(
        examples=["They/them"],
        description="""
    Value
    """,
    )


class Actor(CommonAll):
    """Describes an ActivityPub actor"""

    type: str = Field(
        examples=["Person", "Service", "Application"],
        description="""The type of Actor""",
    )

    inbox: str | None = Field(
        None,
        examples=["https://actor.example/inbox"],
        description="""
    The inbox of the actor
    """,
    )

    outbox: str | None = Field(
        None,
        examples=["https://actor.example/outbox"],
        description="""
    The outbox of the actor
    """,
    )

    icon: dict | None = Field(
        None,
        examples=[{"type": "Image", "url": "https://actor.example/icon.png"}],
        description="""
    The avatar of the actor
    """,
    )

    summary: str | None = Field(
        None,
        examples=["My Fediverse account"],
        description="""
    Description of the actor
    """,
    )

    name: str | None = Field(
        None,
        examples=["Alice"],
        description="""
    Display name of the actor
    """,
    )

    also_known_as: list[str] | None = Field(
        None,
        examples=[["https://alice.example", "https://alice.example/profile"]],
        alias="alsoKnownAs",
        description="Other uris associated with the actor",
    )

    attachments: list[dict | PropertyValue] | None = Field(
        None, description="""attachments ... currently used for property values"""
    )

    preferred_username: str | None = Field(
        None, examples=["john"], alias="preferredUsername"
    )
