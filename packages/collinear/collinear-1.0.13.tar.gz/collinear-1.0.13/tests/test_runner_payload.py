"""Tests verifying Steer API payload shape and configurables."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TypedDict
from typing import cast

import httpx
from _pytest.monkeypatch import MonkeyPatch
from typing_extensions import Self

if TYPE_CHECKING:
    from types import TracebackType

from collinear.schemas.steer import SteerConfig
from collinear.simulate.runner import SimulationRunner


class _Captured(TypedDict):
    url: str
    headers: dict[str, str]
    json: dict[str, object]


def _install_fake_http(monkeypatch: MonkeyPatch, captured: _Captured) -> None:
    class FakeAsyncClient:
        def __init__(self, timeout: float | None = None) -> None:
            pass

        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> None:
            return None

        async def post(
            self,
            url: str,
            *,
            headers: dict[str, str],
            json: dict[str, object],
        ) -> httpx.Response:
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return httpx.Response(
                status_code=200,
                json=cast("dict[str, object]", {"response": "ok"}),
            )

    monkeypatch.setattr(httpx, "AsyncClient", cast("type[httpx.AsyncClient]", FakeAsyncClient))


DEFAULT_STEER_TEMP = 0.7
DEFAULT_STEER_MAX = 256
DEFAULT_STEER_SEED = -1
OVERRIDE_STEER_TEMP = 0.33
OVERRIDE_STEER_MAX = 128
OVERRIDE_SEED = 42


def test_steer_payload_uses_trait_dict_and_defaults(monkeypatch: MonkeyPatch) -> None:
    """Default payload uses trait_dict, temperature=0.7, max_tokens=256."""
    captured: _Captured = {"url": "", "headers": {}, "json": {}}
    _install_fake_http(monkeypatch, captured)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="k",
        assistant_model_name="gpt-test",
        steer_api_key="demo-001",
    )

    cfg = SteerConfig(
        ages=[30],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"impatience": [1]},
        locations=["San Francisco"],
        languages=["English"],
        tasks=["telecom"],
    )

    res = runner.run(config=cfg, k=1, num_exchanges=1, batch_delay=0.0)
    assert res
    payload = captured["json"]
    assert "trait_dict" in payload
    assert "trait" not in payload
    assert "strength" not in payload
    assert payload["trait_dict"] == {"impatience": 1}
    assert payload["temperature"] == DEFAULT_STEER_TEMP
    assert payload["max_tokens"] == DEFAULT_STEER_MAX
    assert payload["seed"] == DEFAULT_STEER_SEED
    assert "task" not in payload
    assert payload["messages"] == []
    assert payload["user_characteristics"] == {
        "age": 30,
        "gender": "female",
        "occupation": "engineer",
        "location": "San Francisco",
        "language": "English",
        "intent": "billing",
        "task": "telecom",
    }


def test_steer_payload_respects_overrides(monkeypatch: MonkeyPatch) -> None:
    """Per-run overrides for temperature and max_tokens are applied to payload."""
    captured: _Captured = {"url": "", "headers": {}, "json": {}}
    _install_fake_http(monkeypatch, captured)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="k",
        assistant_model_name="gpt-test",
        steer_api_key="demo-001",
    )

    cfg = SteerConfig(
        ages=[28],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"skeptical": [2]},
        locations=["Austin"],
        languages=["English"],
        tasks=["telecom"],
    )

    _ = runner.run(
        config=cfg,
        k=1,
        num_exchanges=1,
        batch_delay=0.0,
        steer_temperature=OVERRIDE_STEER_TEMP,
        steer_max_tokens=OVERRIDE_STEER_MAX,
        steer_seed=OVERRIDE_SEED,
    )
    payload = captured["json"]
    assert payload["trait_dict"] == {"skeptical": 2}
    assert payload["temperature"] == OVERRIDE_STEER_TEMP
    assert payload["max_tokens"] == OVERRIDE_STEER_MAX
    assert payload["seed"] == OVERRIDE_SEED
    user_characteristics = cast("dict[str, object]", payload["user_characteristics"])
    assert user_characteristics["task"] == "telecom"


def test_payload_omits_missing_user_characteristics(monkeypatch: MonkeyPatch) -> None:
    """If characteristics are absent they are omitted from the payload."""
    captured: _Captured = {"url": "", "headers": {}, "json": {}}
    _install_fake_http(monkeypatch, captured)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="k",
        assistant_model_name="gpt-test",
        steer_api_key="demo-001",
    )

    cfg = SteerConfig(
        traits={"impatience": [0]},
    )

    _ = runner.run(config=cfg, k=1, num_exchanges=1, batch_delay=0.0)

    payload = captured["json"]
    assert payload["user_characteristics"] == {}
