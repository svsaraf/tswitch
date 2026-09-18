"""Switch-style dispatch backed by the TypeSafe AI choice primitive."""

from typing import Any

from typesafe_sdk import AsyncTypeSafeClient, Choice, TypeSafeClient

from ._core import aask, ask, json_value

_INSTRUCTIONS = "Choose the single case that best matches the state."


def tswitch(
    value: Any,
    /,
    *,
    model: str | None = None,
    api_key: str | None = None,
    client: TypeSafeClient | None = None,
    **cases: Any,
) -> str:
    """Return the name of the case that matches `value`.

    Args:
        value: The value to switch on: text, a JSON-like object or array, or any
            Python object (non-JSON values are described by their `repr`).
        model: Model name override; `None` uses the client or environment default.
        api_key: TypeSafe AI API key; `None` reads `TYPESAFE_API_KEY`. Ignored
            when `client` is supplied.
        client: An existing `TypeSafeClient` to reuse; it is not closed. When
            `None`, a short-lived client is created per call.
        **cases: At least one case, keyed by case name and valued by a
            description of what matches (text, JSON, or `None` for undescribed).

    Returns:
        The name of the matching case.

    Raises:
        ValueError: No cases are supplied.
        TypeSafeError: No API key is available.
        TypeSafeAPIError: The API request fails after any retries.

    Examples:
        ```python
        from tswitch import tswitch

        tone = tswitch(
            "I was charged twice and I am furious!",
            calm="Polite, measured, or friendly language.",
            angry="Hostile, frustrated, or expletive language.",
        )
        assert tone == "angry"
        ```
    """
    if not cases:
        raise ValueError("tswitch() requires at least one case.")
    question = Choice(
        instructions=_INSTRUCTIONS,
        criteria={name: json_value(description) for name, description in cases.items()},
    )
    response = ask(question, name="switch", value=value, model=model, api_key=api_key, client=client)
    return response.answers["switch"].choice


async def atswitch(
    value: Any,
    /,
    *,
    model: str | None = None,
    api_key: str | None = None,
    client: AsyncTypeSafeClient | None = None,
    **cases: Any,
) -> str:
    """Async variant of [`tswitch`][tswitch.tswitch].

    Args:
        value: The value to switch on; see `tswitch` for the accepted forms.
        model: Model name override; `None` uses the client or environment default.
        api_key: TypeSafe AI API key; `None` reads `TYPESAFE_API_KEY`. Ignored
            when `client` is supplied.
        client: An existing `AsyncTypeSafeClient` to reuse; it is not closed.
            When `None`, a short-lived client is created per call.
        **cases: At least one case, keyed by case name and valued by a
            description of what matches.

    Returns:
        The name of the matching case.

    Raises:
        ValueError: No cases are supplied.
        TypeSafeError: No API key is available.
        TypeSafeAPIError: The API request fails after any retries.
    """
    if not cases:
        raise ValueError("atswitch() requires at least one case.")
    question = Choice(
        instructions=_INSTRUCTIONS,
        criteria={name: json_value(description) for name, description in cases.items()},
    )
    response = await aask(question, name="switch", value=value, model=model, api_key=api_key, client=client)
    return response.answers["switch"].choice
