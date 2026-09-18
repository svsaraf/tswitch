"""Score-style measurement backed by the TypeSafe AI score primitive."""

from collections.abc import Sequence
from typing import Any

from typesafe_sdk import AsyncTypeSafeClient, Score, TypeSafeClient

from ._core import aask, ask, content, json_value


def tscore(
    value: Any,
    instructions: Any,
    levels: Sequence[Any],
    /,
    *,
    model: str | None = None,
    api_key: str | None = None,
    client: TypeSafeClient | None = None,
) -> float:
    """Return the score of `value` along the ordered `levels`.

    Args:
        value: The value to score: text, a JSON-like object or array, or any
            Python object (non-JSON values are described by their `repr`).
        instructions: The question to ask about `value`, as text or JSON.
        levels: An ordered, nonempty list of level descriptions, one per score
            from zero; each may be text, JSON, or any Python object.
        model: Model name override; `None` uses the client or environment default.
        api_key: TypeSafe AI API key; `None` reads `TYPESAFE_API_KEY`. Ignored
            when `client` is supplied.
        client: An existing `TypeSafeClient` to reuse; it is not closed. When
            `None`, a short-lived client is created per call.

    Returns:
        The score as a float from `0` to `len(levels) - 1`; it can fall between
        two levels.

    Raises:
        ValueError: `levels` is empty.
        TypeSafeError: No API key is available.
        TypeSafeAPIError: The API request fails after any retries.

    Examples:
        ```python
        from tswitch import tscore

        frustration = tscore(
            "I was charged twice and I am furious!",
            "How frustrated does the customer appear?",
            ["Calm and neutral.", "Concerned but civil.", "Very angry."],
        )
        assert 0 <= frustration <= 2
        ```
    """
    if not levels:
        raise ValueError("tscore() requires at least one level.")
    question = Score(
        instructions=content(instructions),
        criteria=[json_value(level) for level in levels],
    )
    response = ask(question, name="score", value=value, model=model, api_key=api_key, client=client)
    return response.answers["score"].score


async def atscore(
    value: Any,
    instructions: Any,
    levels: Sequence[Any],
    /,
    *,
    model: str | None = None,
    api_key: str | None = None,
    client: AsyncTypeSafeClient | None = None,
) -> float:
    """Async variant of [`tscore`][tswitch.tscore].

    Args:
        value: The value to score; see `tscore` for the accepted forms.
        instructions: The question to ask about `value`, as text or JSON.
        levels: An ordered, nonempty list of level descriptions, one per score
            from zero.
        model: Model name override; `None` uses the client or environment default.
        api_key: TypeSafe AI API key; `None` reads `TYPESAFE_API_KEY`. Ignored
            when `client` is supplied.
        client: An existing `AsyncTypeSafeClient` to reuse; it is not closed.
            When `None`, a short-lived client is created per call.

    Returns:
        The score as a float from `0` to `len(levels) - 1`; it can fall between
        two levels.

    Raises:
        ValueError: `levels` is empty.
        TypeSafeError: No API key is available.
        TypeSafeAPIError: The API request fails after any retries.
    """
    if not levels:
        raise ValueError("atscore() requires at least one level.")
    question = Score(
        instructions=content(instructions),
        criteria=[json_value(level) for level in levels],
    )
    response = await aask(question, name="score", value=value, model=model, api_key=api_key, client=client)
    return response.answers["score"].score
