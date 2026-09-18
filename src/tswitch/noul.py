"""Yes/no judgments backed by the TypeSafe AI noul primitive."""

from typing import Any

from typesafe_sdk import AsyncTypeSafeClient, Noul, TypeSafeClient

from ._core import aask, ask, content, json_value


def tbool(
    value: Any,
    instructions: Any,
    /,
    *,
    true: Any = None,
    false: Any = None,
    threshold: float = 0.5,
    model: str | None = None,
    api_key: str | None = None,
    client: TypeSafeClient | None = None,
) -> bool:
    """Return whether `instructions` is true of `value`.

    Args:
        value: The value to judge: text, a JSON-like object or array, or any
            Python object (non-JSON values are described by their `repr`).
        instructions: The statement to judge, phrased so it is clearly true or
            false, as text or JSON.
        true: Optional description of what a yes answer looks like.
        false: Optional description of what a no answer looks like.
        threshold: The probability of yes at or above which the answer counts
            as true; must be within `[0, 1]`. Defaults to `0.5`.
        model: Model name override; `None` uses the client or environment default.
        api_key: TypeSafe AI API key; `None` reads `TYPESAFE_API_KEY`. Ignored
            when `client` is supplied.
        client: An existing `TypeSafeClient` to reuse; it is not closed. When
            `None`, a short-lived client is created per call.

    Returns:
        `True` when the probability that the statement is true is at or above
        `threshold`, else `False`.

    Raises:
        ValueError: `threshold` is outside `[0, 1]`.
        TypeSafeError: No API key is available.
        TypeSafeAPIError: The API request fails after any retries.

    Examples:
        ```python
        from tswitch import tbool

        refund = tbool(
            "I was charged twice. Please refund the duplicate.",
            "Does the customer request a refund?",
        )
        assert refund is True
        ```
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1.")
    criteria: dict[str, Any] = {}
    if true is not None:
        criteria["true"] = json_value(true)
    if false is not None:
        criteria["false"] = json_value(false)
    question = Noul(instructions=content(instructions), criteria=criteria or None)
    response = ask(question, name="noul", value=value, model=model, api_key=api_key, client=client)
    return response.answers["noul"].noul >= threshold


async def atbool(
    value: Any,
    instructions: Any,
    /,
    *,
    true: Any = None,
    false: Any = None,
    threshold: float = 0.5,
    model: str | None = None,
    api_key: str | None = None,
    client: AsyncTypeSafeClient | None = None,
) -> bool:
    """Async variant of [`tbool`][tswitch.tbool].

    Args:
        value: The value to judge; see `tbool` for the accepted forms.
        instructions: The statement to judge, phrased so it is clearly true or
            false.
        true: Optional description of what a yes answer looks like.
        false: Optional description of what a no answer looks like.
        threshold: The probability of yes at or above which the answer counts
            as true; must be within `[0, 1]`.
        model: Model name override; `None` uses the client or environment default.
        api_key: TypeSafe AI API key; `None` reads `TYPESAFE_API_KEY`. Ignored
            when `client` is supplied.
        client: An existing `AsyncTypeSafeClient` to reuse; it is not closed.
            When `None`, a short-lived client is created per call.

    Returns:
        `True` when the probability that the statement is true is at or above
        `threshold`, else `False`.

    Raises:
        ValueError: `threshold` is outside `[0, 1]`.
        TypeSafeError: No API key is available.
        TypeSafeAPIError: The API request fails after any retries.
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1.")
    criteria: dict[str, Any] = {}
    if true is not None:
        criteria["true"] = json_value(true)
    if false is not None:
        criteria["false"] = json_value(false)
    question = Noul(instructions=content(instructions), criteria=criteria or None)
    response = await aask(question, name="noul", value=value, model=model, api_key=api_key, client=client)
    return response.answers["noul"].noul >= threshold
