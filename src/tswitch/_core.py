"""Shared plumbing for the tswitch primitive wrappers."""

from collections.abc import Mapping, Sequence
from typing import Any

from typesafe_sdk import (
    AsyncTypeSafeClient,
    JSONContent,
    Question,
    SystemOneResponse,
    TypeSafeClient,
)


def json_value(value: Any) -> Any:
    """Coerce a description to a JSON-like value, describing objects by their `repr`."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [json_value(item) for item in value]
    return repr(value)


def content(value: Any) -> JSONContent:
    """Coerce a top-level state or instructions value to a JSON-compatible form."""
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [json_value(item) for item in value]
    return repr(value)


def ask(
    question: Question,
    /,
    *,
    name: str,
    value: Any,
    model: str | None = None,
    api_key: str | None = None,
    client: TypeSafeClient | None = None,
) -> SystemOneResponse:
    """Send one question about `value` synchronously, reusing `client` when supplied."""
    if client is not None:
        return client.system_one(state=content(value), questions={name: question}, model=model)
    with TypeSafeClient(api_key=api_key, model=model) as own:
        return own.system_one(state=content(value), questions={name: question}, model=model)


async def aask(
    question: Question,
    /,
    *,
    name: str,
    value: Any,
    model: str | None = None,
    api_key: str | None = None,
    client: AsyncTypeSafeClient | None = None,
) -> SystemOneResponse:
    """Send one question about `value` asynchronously, reusing `client` when supplied."""
    if client is not None:
        return await client.system_one(state=content(value), questions={name: question}, model=model)
    async with AsyncTypeSafeClient(api_key=api_key, model=model) as own:
        return await own.system_one(state=content(value), questions={name: question}, model=model)
