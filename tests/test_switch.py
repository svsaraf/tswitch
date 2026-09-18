import asyncio
import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tswitch as tswitch_pkg
from tswitch import atbool, atscore, atswitch, tbool, tscore, tswitch


def _response(answers):
    return SimpleNamespace(answers=answers)


def _switch_response(label):
    return _response({"switch": SimpleNamespace(choice=label)})


def _score_response(score):
    return _response({"score": SimpleNamespace(score=score)})


def _noul_response(noul):
    return _response({"noul": SimpleNamespace(noul=noul)})


def _sync_client(response):
    client = MagicMock()
    client.__enter__.return_value = client
    client.__exit__.return_value = False
    client.system_one.return_value = response
    return client


def _async_client(response):
    client = AsyncMock()
    client.__aenter__.return_value = client
    client.__aexit__.return_value = False
    client.system_one.return_value = response
    return client


def test_tswitch_returns_matching_case_label():
    with patch("tswitch._core.TypeSafeClient", return_value=_sync_client(_switch_response("angry"))):
        assert (
            tswitch(
                "I was charged twice and I am furious!",
                calm="Polite language.",
                angry="Hostile language.",
            )
            == "angry"
        )


def test_tswitch_passes_state_and_criteria():
    client = _sync_client(_switch_response("spam"))
    with patch("tswitch._core.TypeSafeClient", return_value=client):
        tswitch("hello", spam="matches spam", eggs=None)

    kwargs = client.system_one.call_args.kwargs
    assert kwargs["state"] == "hello"
    assert kwargs["model"] is None
    question = kwargs["questions"]["switch"]
    assert question.criteria == {"spam": "matches spam", "eggs": None}
    assert question.instructions


def test_tswitch_no_cases_raises():
    with patch("tswitch._core.TypeSafeClient", return_value=_sync_client(_switch_response("x"))):
        with pytest.raises(ValueError):
            tswitch("hello")


def test_tswitch_state_coercion():
    client = _sync_client(_switch_response("a"))
    with patch("tswitch._core.TypeSafeClient", return_value=client):
        tswitch(42, a=None, b=None)
        assert client.system_one.call_args.kwargs["state"] == "42"

        tswitch({"when": datetime.datetime(2026, 1, 1), "tags": ("urgent",)}, a=None, b=None)
        assert client.system_one.call_args.kwargs["state"] == {
            "when": repr(datetime.datetime(2026, 1, 1)),
            "tags": ["urgent"],
        }


def test_tswitch_model_passthrough():
    client = _sync_client(_switch_response("a"))
    with patch("tswitch._core.TypeSafeClient", return_value=client):
        tswitch("hello", a=None, model="m")
        assert client.system_one.call_args.kwargs["model"] == "m"


def test_tswitch_api_key_forwarded_to_client():
    with patch("tswitch._core.TypeSafeClient", return_value=_sync_client(_switch_response("a"))) as ctor:
        tswitch("hello", a=None, api_key="ts_test")
        assert ctor.call_args.kwargs["api_key"] == "ts_test"


def test_tswitch_reuses_supplied_client_without_closing():
    client = _sync_client(_switch_response("billing"))
    with patch("tswitch._core.TypeSafeClient") as ctor:
        assert tswitch("refund please", billing=None, general=None, client=client) == "billing"
        ctor.assert_not_called()
        client.close.assert_not_called()

    question = client.system_one.call_args.kwargs["questions"]["switch"]
    assert set(question.criteria) == {"billing", "general"}


def test_tscore_returns_score():
    with patch("tswitch._core.TypeSafeClient", return_value=_sync_client(_score_response(1.4))):
        assert (
            tscore(
                "I was charged twice and I am furious!",
                "How frustrated does the customer appear?",
                ["Calm and neutral.", "Concerned but civil.", "Very angry."],
            )
            == 1.4
        )


def test_tscore_passes_state_and_criteria():
    client = _sync_client(_score_response(0.0))
    sentinel = object()
    with patch("tswitch._core.TypeSafeClient", return_value=client):
        tscore("hello", "How urgent is it?", ["not urgent", ("urgent",), sentinel])

    kwargs = client.system_one.call_args.kwargs
    assert kwargs["state"] == "hello"
    question = kwargs["questions"]["score"]
    assert question.instructions == "How urgent is it?"
    assert question.criteria == ["not urgent", ["urgent"], repr(sentinel)]


def test_tscore_no_levels_raises():
    with patch("tswitch._core.TypeSafeClient", return_value=_sync_client(_score_response(0.0))):
        with pytest.raises(ValueError):
            tscore("hello", "How urgent?", [])


def test_tbool_returns_true_above_threshold():
    with patch("tswitch._core.TypeSafeClient", return_value=_sync_client(_noul_response(0.9))):
        assert tbool("I was charged twice. Please refund the duplicate.", "Does the customer request a refund?")


def test_tbool_returns_false_below_threshold():
    with patch("tswitch._core.TypeSafeClient", return_value=_sync_client(_noul_response(0.3))):
        assert not tbool("Just saying hi!", "Does the customer request a refund?")


def test_tbool_threshold_comparison():
    with patch("tswitch._core.TypeSafeClient", return_value=_sync_client(_noul_response(0.9))):
        assert tbool("x", "Is x true?", threshold=0.9)
        assert not tbool("x", "Is x true?", threshold=0.95)


def test_tbool_criteria_descriptions():
    client = _sync_client(_noul_response(1.0))
    with patch("tswitch._core.TypeSafeClient", return_value=client):
        tbool("hello", "Is it a greeting?", true="Words of welcome.", false="Anything else.")
        question = client.system_one.call_args.kwargs["questions"]["noul"]
        assert question.criteria == {"true": "Words of welcome.", "false": "Anything else."}

        tbool("hello", "Is it a greeting?")
        question = client.system_one.call_args.kwargs["questions"]["noul"]
        assert question.criteria is None


def test_tbool_invalid_threshold_raises():
    with patch("tswitch._core.TypeSafeClient", return_value=_sync_client(_noul_response(1.0))):
        for bad in (-0.1, 1.1, float("nan")):
            with pytest.raises(ValueError):
                tbool("x", "Is x true?", threshold=bad)


def test_atswitch_returns_matching_case_label():
    asyncio.run(_run_atswitch())


async def _run_atswitch():
    with patch("tswitch._core.AsyncTypeSafeClient", return_value=_async_client(_switch_response("calm"))):
        result = await atswitch(
            "Thanks, that solved it!",
            calm="Polite language.",
            angry="Hostile language.",
        )
    assert result == "calm"


def test_atswitch_no_cases_raises():
    with pytest.raises(ValueError):

        async def _call():
            with patch("tswitch._core.AsyncTypeSafeClient", return_value=_async_client(_switch_response("x"))):
                await atswitch("hello")

        asyncio.run(_call())


def test_atswitch_reuses_supplied_client():
    asyncio.run(_run_atswitch_reuse())


async def _run_atswitch_reuse():
    client = _async_client(_switch_response("spam"))
    with patch("tswitch._core.AsyncTypeSafeClient") as ctor:
        assert await atswitch("hello", spam=None, eggs=None, client=client) == "spam"
        ctor.assert_not_called()
        client.close.assert_not_called()


def test_atscore_returns_score():
    asyncio.run(_run_atscore())


async def _run_atscore():
    with patch("tswitch._core.AsyncTypeSafeClient", return_value=_async_client(_score_response(2.0))):
        result = await atscore("hello", "How urgent?", ["a", "b", "c"])
    assert result == 2.0


def test_atscore_no_levels_raises():
    with pytest.raises(ValueError):

        async def _call():
            with patch("tswitch._core.AsyncTypeSafeClient", return_value=_async_client(_score_response(0.0))):
                await atscore("hello", "How urgent?", [])

        asyncio.run(_call())


def test_atbool_returns_bool():
    asyncio.run(_run_atbool())


async def _run_atbool():
    with patch("tswitch._core.AsyncTypeSafeClient", return_value=_async_client(_noul_response(0.8))):
        result = await atbool("It's broken!", "Does this message report a bug?")
    assert result is True


def test_atbool_invalid_threshold_raises():
    with pytest.raises(ValueError):

        async def _call():
            with patch("tswitch._core.AsyncTypeSafeClient", return_value=_async_client(_noul_response(1.0))):
                await atbool("x", "Is x true?", threshold=2.0)

        asyncio.run(_call())


def test_atbool_reuses_supplied_client():
    asyncio.run(_run_atbool_reuse())


async def _run_atbool_reuse():
    client = _async_client(_noul_response(0.1))
    with patch("tswitch._core.AsyncTypeSafeClient") as ctor:
        assert await atbool("hello", "Is it spam?", client=client) is False
        ctor.assert_not_called()
        client.close.assert_not_called()


def test_version():
    assert isinstance(tswitch_pkg.__version__, str)
