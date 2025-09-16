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
    class FakeClient:
        def __init__(self, timeout: float | None = None) -> None:
            pass

        def __enter__(self) -> Self:
            return self

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> None:
            return None

        def post(
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

    monkeypatch.setattr(httpx, "Client", cast("type[httpx.Client]", FakeClient))


DEFAULT_STEER_TEMP = 0.7
DEFAULT_STEER_MAX = 256
OVERRIDE_STEER_TEMP = 0.33
OVERRIDE_STEER_MAX = 128


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
        ages=["25"],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"impatience": [2.5]},
    )

    res = runner.run(config=cfg, k=1, num_exchanges=1, batch_delay=0.0)
    assert res
    payload = captured["json"]
    assert "trait_dict" in payload
    assert "trait" not in payload
    assert "strength" not in payload
    assert payload["trait_dict"] == {"impatience": 2.5}
    assert payload["temperature"] == DEFAULT_STEER_TEMP
    assert payload["max_tokens"] == DEFAULT_STEER_MAX


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
        ages=["25"],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"skeptical": [4]},
    )

    _ = runner.run(
        config=cfg,
        k=1,
        num_exchanges=1,
        batch_delay=0.0,
        steer_temperature=OVERRIDE_STEER_TEMP,
        steer_max_tokens=OVERRIDE_STEER_MAX,
    )
    payload = captured["json"]
    assert payload["trait_dict"] == {"skeptical": 4.0}
    assert payload["temperature"] == OVERRIDE_STEER_TEMP
    assert payload["max_tokens"] == OVERRIDE_STEER_MAX
