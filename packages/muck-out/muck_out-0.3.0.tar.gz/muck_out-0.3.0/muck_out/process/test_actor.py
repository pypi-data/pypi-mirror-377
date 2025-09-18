import re
import pytest

from muck_out.types import Actor
from muck_out.types.validated.actor import PropertyValue

from .actor import normalize_property_value, normalize_actor, actor_stub


def test_normalize_actor_failure():
    assert normalize_actor({}) is None


actor_base = {
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "Person",
    "id": "https://example.com/users/alice",
}


@pytest.mark.parametrize(
    "data",
    [
        {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Person",
            "id": "https://example.com/users/alice",
            "inbox": "https://example.com/users/alice/inbox",
        },
        {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Person",
            "id": "https://example.com/users/alice",
            "inbox": "https://example.com/users/alice/inbox",
            "icon": {
                "type": "Image",
                "url": "https://example.com/users/alice/icon.png",
            },
        },
    ],
)
def test_normalize_actor(data):
    assert isinstance(normalize_actor(data), Actor)


def to_snake_case(string: str):
    return re.sub("([A-Z]+)", r"_\1", string).lower()


@pytest.mark.parametrize(
    "field, value, mapped",
    [
        ("summary", "<p>Hello, world!</p>", "<p>Hello, world!</p>"),
        (
            "summary",
            "<p>Test<script>alert('hi')</script></p>",
            "<p>Test</p>",
        ),
        ("name", "Alice", "Alice"),
        (
            "alsoKnownAs",
            ["https://example.com/users/alice"],
            ["https://example.com/users/alice"],
        ),
    ],
)
def test_normalize_actor_field(field: str, value: str, mapped: str):
    data = actor_base.copy()
    data[field] = value
    actor = normalize_actor(data)
    assert getattr(actor, to_snake_case(field)) == mapped


actor_object = {
    "@context": [
        "https://www.w3.org/ns/activitystreams",
    ],
    "id": "http://mitra/users/admin",
    "type": "Person",
    "name": None,
    "preferredUsername": "admin",
    "inbox": "http://mitra/users/admin/inbox",
    "outbox": "http://mitra/users/admin/outbox",
    "followers": "http://mitra/users/admin/followers",
    "following": "http://mitra/users/admin/following",
    "subscribers": "http://mitra/users/admin/subscribers",
    "featured": "http://mitra/users/admin/collections/featured",
    "assertionMethod": [
        {
            "id": "http://mitra/users/admin#main-key",
            "type": "Multikey",
            "controller": "http://mitra/users/admin",
            "publicKeyMultibase": "z4MXj1wBzi9jUstyPBJ7qsa7G5waXG8McxXkjvAVHFLMxhGiJTGXK1EWseFfrUaH6Btt7TCSB1Entgg5SyAaHc1Ssh698puSozC41J2no8rgpMVRPzFVBoAYuNamM5FW9qCP1XV2y1cJ2y3gmuoreUVyn1jgW7Gb3NxsEcxjfs3fE1SzXjCnkxqVikYjkByqbXeB4AvYeXP1wjS1KB9xzKAzAjnRrui6RLHi6sCji2f7kdmxALcmjMbLyKjmYozhoG5ZqVkfNNZuAf4PLgyJQ84rDNKUGRgZeCeNh31hLLMUsSFYgpArfp813dbusq3A5BnnWN24rQtrj7nN9gQsxYjSTRhLpQcSLnwCQxJ1Sc2u9zfDwcJdW",
        },
        {
            "id": "http://mitra/users/admin#ed25519-key",
            "type": "Multikey",
            "controller": "http://mitra/users/admin",
            "publicKeyMultibase": "z6Mkgo38JzBJ6pLDyNz6YhnDN3ZXU6GcBWpp2c5dCEXcJtwW",
        },
    ],
    "publicKey": {
        "id": "http://mitra/users/admin#main-key",
        "owner": "http://mitra/users/admin",
        "publicKeyPem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqh38rZnS2RDft6RAGt5O\np4teGYSYmaeB2l5UGRCpnzcVf3m4v/x6LpXJXG8bDkNNnIZ/OzZ8tNPzKZJ6sKpI\nngayjowI/YzN8BBPJuKtaB3B4ImNrvG865OQl0h+TtfXaNTRWK8U108bMW2HH2/n\nTWJiaYiCcxLPzFRPLLd/TG6IYgeSKlRpYJ5TOdpZg1Hcx7/eRljFvdq7wmUcbM2W\nXmUYv1sjmwGQ92VCEy8d0biE/IesHdE6QM/5ALdAcQGtTn5QK7AEe43VmklkTfV+\nqDs38r3kVAMuHxnpASj+nuMp7Y7dRm92aKJ1vj93HxXTE1Ajh2eQYk8ulHQjcLky\nGwIDAQAB\n-----END PUBLIC KEY-----\n",
    },
    "generator": {
        "type": "Application",
        "implements": [
            {
                "name": "RFC-9421: HTTP Message Signatures",
                "href": "https://datatracker.ietf.org/doc/html/rfc9421",
            },
            {
                "name": "RFC-9421 signatures using the Ed25519 algorithm",
                "href": "https://datatracker.ietf.org/doc/html/rfc9421#name-eddsa-using-curve-edwards25",
            },
        ],
    },
    "manuallyApprovesFollowers": False,
    "url": "http://mitra/users/admin",
    "published": "2025-09-11T13:34:15.718558Z",
    "updated": "2025-09-11T13:34:15.718558Z",
}


def test_actor_import():
    result = actor_stub(actor_object)

    assert result.url

    assert result.preferred_username == "admin"


def test_normalize_property_value_dict():
    data = {"type": "Other", "name": "wooo"}

    assert normalize_property_value(data) == data


def test_normalize_property_value():
    data = {
        "type": "PropertyValue",
        "name": "Blog",
        "value": '<a href="http://value.example/" target="_blank" rel="nofollow noopener noreferrer me" translate="no"><span class="invisible">http://</span><span class="">value.example/</span><span class="invisible"></span></a>',
    }

    result = normalize_property_value(data)

    assert isinstance(result, PropertyValue)

    assert result.value == "http://value.example/"
