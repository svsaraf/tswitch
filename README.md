# tswitch

Typesafe `switch`, `score`, and `bool` primitives for Python, powered by [TypeSafe AI](https://typesafe.ai).

`tswitch` is a smart version of a switch statement
`tscore` is a smart version of a score
`tbool` returns true if something is correct

## Installation

```bash
pip install tswitch
```

Set your API key (see [typesafe.ai](https://typesafe.ai)):

```bash
export TYPESAFE_API_KEY=apikey_...
```

## Quickstart

`tswitch` looks at your value and returns the name of the case that matches:

```python
from tswitch import tswitch

tone = tswitch(
    "I was charged twice and I am furious!",
    calm="Polite, measured, or friendly language.",
    angry="Hostile, frustrated, or expletive language.",
)
print(tone)
```

```
angry
```

`tswitch` can only answer with one of the case names you gave it, so the result is
always `"calm"` or `"angry"` — never anything else. Use it like a `switch` statement:

```python
from tswitch import tswitch

email = "Hi! You billed me twice this month. Please fix it."

team = tswitch(
    email,
    billing="Problems with charges, invoices, refunds, or subscriptions.",
    general="Anything else.",
)
print(team)

if team == "billing":
    send_to("billing-team@example.com")
else:
    send_to("support@example.com")
```

```
billing
```

## Score a value on a spectrum

`tscore` returns a number: `0` for the first level you listed, `1` for the second,
`2` for the third, and so on. It can also land between two levels, like `1.8`:

```python
from tswitch import tscore

frustration = tscore(
    "I was charged twice and I am furious!",
    "How frustrated does the customer appear?",
    ["Calm and neutral.", "Concerned but civil.", "Very angry."],
)
print(frustration)
```

```
1.8
```

Here `0` means calm, `1` means concerned, and `2` means very angry — `1.8` means
"somewhere between concerned and very angry, closer to angry". That makes it easy to
act on with a plain comparison:

```python
if frustration >= 2:
    escalate_to_human()
```

## Answer a yes/no question

`tbool` returns `True` or `False`:

```python
from tswitch import tbool

refund = tbool(
    "You charged me twice this month. Please refund the extra charge.",
    "Does the customer ask for a refund?",
)
print(refund)
```

```
True
```

You can optionally describe what a yes and a no look like, and the answer is `True`
when the probability of yes is at or above `threshold` (default `0.5`):

```python
from tswitch import tbool

refund = tbool(
    "You charged me twice this month. Please refund the extra charge.",
    "Does the customer ask for a refund?",
    true="The customer wants money returned.",
    false="The customer is asking for information only.",
)
print(refund)
```

```
True
```

## The value

The value can be a string, a dictionary, a list, or any Python object. Dictionaries
and lists are sent as they are; anything the API can't read (like a date) is described
by its `repr`:

```python
import datetime

from tswitch import tswitch

result = tswitch(
    {"when": datetime.datetime(2026, 1, 1, 3, 0), "text": "URGENT: site is down"},
    urgent="Reports of outages or unavailable services.",
    routine="Ordinary questions or feature requests.",
)
print(result)
```

```
urgent
```

## Case descriptions

Each case is keyed by its name and valued by a description of what matches. A string
is the most common choice, and `None` means "no description":

```python
from tswitch import tswitch

result = tswitch(
    "The plot dragged in the second act.",
    plot="Concerns about storyline or pacing.",
    cast="Concerns about acting or characters.",
    effects=None,
)
print(result)
```

```
plot
```

Descriptions don't have to be strings — dictionaries, lists, and tuples work too, and
any other object is described by its `repr`:

```python
from tswitch import tswitch

result = tswitch(
    {"error": "TypeError: 'NoneType' object is not iterable", "version": "1.4.2"},
    crash={"matches": "failures that stop the program", "signals": ["traceback", "exit code"]},
    cosmetic=("visual problems", "layout issues"),
    other=object(),  # described by repr(object())
)
print(result)
```

```
crash
```

Cases are keyword arguments, so names with dashes or spaces are unpacked from a
dictionary:

```python
from tswitch import tswitch

result = tswitch(
    "The plot dragged in the second act.",
    **{"slow-burn": "Deliberate, gradual pacing.", "messy": "Confused or erratic pacing."},
)
print(result)
```

```
slow-burn
```

## Async

Every function has an async twin: `atswitch`, `atscore`, and `atbool`. They work the
same way, but you `await` them:

```python
import asyncio

from tswitch import atswitch

async def main():
    tone = await atswitch(
        "Thanks, that solved it!",
        calm="Polite, measured, or friendly language.",
        angry="Hostile, frustrated, or expletive language.",
    )
    print(tone)

asyncio.run(main())
```

```
calm
```

## API

#### `tswitch(value, /, *, model=None, api_key=None, client=None, **cases)` → `str`

Returns the name of the case matching `value`. Raises `ValueError` if no cases are
supplied, and `TypeSafeError` if no API key is available.

#### `tscore(value, instructions, levels, /, *, model=None, api_key=None, client=None)` → `float`

Returns the score of `value` along the ordered `levels`, from `0` to
`len(levels) - 1`; it can fall between two levels. Raises `ValueError` if `levels`
is empty.

#### `tbool(value, instructions, /, *, true=None, false=None, threshold=0.5, model=None, api_key=None, client=None)` → `bool`

Returns whether `instructions` is true of `value`, using the optional `true`/`false`
outcome descriptions and requiring a probability of yes at or above `threshold`.
Raises `ValueError` if `threshold` is outside `[0, 1]`.

#### `atswitch`, `atscore`, `atbool`

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
