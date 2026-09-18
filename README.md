# tswitch

Typesafe `switch`, `score`, and `bool` primitives for Python, powered by [TypeSafe AI](https://typesafe.ai).

## Installation

```bash
pip install tswitch
```

Set your API key (see [typesafe.ai](https://typesafe.ai)):

```bash
export TYPESAFE_API_KEY=apikey_...
```

## Quickstart

```python
from tswitch import tswitch

tone = tswitch(
    "I was charged twice and I am furious!",
    calm="Polite, measured, or friendly language.",
    angry="Hostile, frustrated, or expletive language.",
)
# tone == "angry"
```

Dispatch on structured state, then map case names to results:

```python
from tswitch import tswitch

ticket = {"subject": "Refund please", "body": "You billed me twice this month."}

route = {
    "billing": ["billing-team@example.com", "P1"],
    "general": ["support@example.com", "P3"],
}[
    tswitch(
        ticket,
        billing="Problems with charges, invoices, refunds, or subscriptions.",
        general="Anything else.",
    )
]
```

## Score a value on a spectrum

`tscore` returns a float position along your ordered levels — it can fall between
two of them, so it maps onto a threshold:

```python
from tswitch import tscore

frustration = tscore(
    "I was charged twice and I am furious!",
    "How frustrated does the customer appear?",
    ["Calm and neutral.", "Concerned but civil.", "Very angry or using strong language."],
)
if frustration >= 2:
    escalate_to_human()
```

## Judge a yes/no statement

`tbool` returns `True` when the probability that your statement is true is at or
above `threshold` (default `0.5`), so it maps onto an `if`:

```python
from tswitch import tbool

if tbool(
    "I was charged twice. Please refund the duplicate.",
    "Does the customer request a refund?",
    true="The customer wants money returned.",
    false="The customer is asking for information only.",
):
    issue_refund()
```

Phrase the statement so it is clearly true or false. If you want to measure a
level of something ("how strong is this candidate in Python?"), use `tscore`
with defined levels instead.

## The value

The value may be text, a JSON-like dict or list (nested non-JSON objects are described
by their `repr`), or any other Python object, which is described by its `repr`:

```python
import datetime

tswitch(
    {"at": datetime.datetime(2026, 1, 1, 3, 0), "text": "URGENT: site is down"},
    urgent="Reports of outages or unavailable services.",
    routine="Ordinary questions or feature requests.",
)
```

## Case descriptions

Each case is keyed by its name and valued by a description of what matches — a string,
JSON-like content, or `None` for an undescribed label:

```python
tswitch(
    "The plot dragged in the second act.",
    plot="Concerns about storyline or pacing.",
    cast="Concerns about acting or characters.",
    effects=None,
)
```

Descriptions don't have to be strings — any JSON-like value works, and non-JSON
objects are described by their `repr`:

```python
bugs = tswitch(
    {"error": "TypeError: 'NoneType' object is not iterable", "version": "1.4.2"},
    crash={"matches": "failures that stop the program", "signals": ["traceback", "exit code"]},
    cosmetic=("visual problems", "layout issues"),
    other=object(),  # described by repr(object())
)
```

Cases are keyword arguments, so names with dashes or spaces are unpacked from a dict:

```python
tswitch(
    "The plot dragged in the second act.",
    **{"slow-burn": "Deliberate, gradual pacing.", "messy": "Confused or erratic pacing."},
)
```

## Async

```python
import asyncio
from tswitch import atswitch, atscore, atbool

async def main():
    tone = await atswitch(
        "Thanks, that solved it!",
        calm="Polite, measured, or friendly language.",
        angry="Hostile, frustrated, or expletive language.",
    )
    frustration = await atscore(
        "Thanks, that solved it!",
        "How frustrated does the customer appear?",
        ["Calm and neutral.", "Concerned but civil.", "Very angry."],
    )
    friendly = await atbool(tone, f"Is {tone!r} friendly language?")
    print(tone, frustration, friendly)

asyncio.run(main())
```

Every function has an async twin: `atswitch`, `atscore`, and `atbool`.

## API

### `tswitch(value, /, *, model=None, api_key=None, client=None, **cases)` → `str`

Returns the name of the case matching `value`. Raises `ValueError` if no cases are
supplied, and `TypeSafeError` if no API key is available.

### `tscore(value, instructions, levels, /, *, model=None, api_key=None, client=None)` → `float`

Returns the score of `value` along the ordered `levels`, from `0` to
`len(levels) - 1`; it can fall between two levels. Raises `ValueError` if `levels`
is empty.

### `tbool(value, instructions, /, *, true=None, false=None, threshold=0.5, model=None, api_key=None, client=None)` → `bool`

Returns whether `instructions` is true of `value`, using the optional `true`/`false`
outcome descriptions and requiring a probability of yes at or above `threshold`.
Raises `ValueError` if `threshold` is outside `[0, 1]`.

### `atswitch`, `atscore`, `atbool`

The async variants of the functions above, with identical signatures and results.

Options:

- `model` — model name override (`None` uses the environment or account default).
- `api_key` — API key override (`None` reads `TYPESAFE_API_KEY`).
- `client` — a reusable `TypeSafeClient` / `AsyncTypeSafeClient` from
  `typesafe-sdk`. It is used for the call and never closed; without it a short-lived
  client is created per call, so pass your own client in hot loops:

  ```python
  from typesafe_sdk import TypeSafeClient
  from tswitch import tswitch

  with TypeSafeClient() as client:
      for email in emails:
          kind = tswitch(email, sales="...", support="...", client=client)
  ```

Errors from the underlying SDK (`TypeSafeAPIError` and subclasses) propagate unchanged;
see the [typesafe-sdk docs](https://docs.typesafe.ai) for details.
