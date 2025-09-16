"""Tests for pairwise trait mixing (mix_traits=True)."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TypedDict
from typing import cast

import httpx
import pytest
from _pytest.monkeypatch import MonkeyPatch
from typing_extensions import Self

if TYPE_CHECKING:
    from types import TracebackType

from collinear.schemas.steer import SteerConfig
from collinear.simulate.runner import SimulationRunner


def test_mixed_combinations_count_and_contents() -> None:
    """When mix_traits=True, generate pairwise combinations of intensities."""
    cfg = SteerConfig(
        ages=["25", "30"],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing", "cancel"],
        traits={
            "confusion": [2],
            "impatience": [0, 3],
            "skeptical": [1],
        },
    )

    combos = cfg.combinations(mix_traits=True)

    base = 2 * 1 * 1 * 2

    pair_intensity_products = 5
    assert len(combos) == base * pair_intensity_products

    pair_size = 2
    assert all(len(c.traits) == pair_size for c in combos)


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


def test_mixed_payload_sends_two_traits(monkeypatch: MonkeyPatch) -> None:
    """Runner payload contains exactly two traits when mix_traits=True."""
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
        traits={"confusion": [2], "impatience": [0, 3]},
    )

    res = runner.run(
        config=cfg,
        k=1,
        num_exchanges=1,
        batch_delay=0.0,
        mix_traits=True,
    )
    assert res

    payload = captured["json"]
    assert "trait_dict" in payload
    td = cast("dict[str, float]", payload["trait_dict"])
    assert set(td.keys()) == {"confusion", "impatience"}
    expected_confusion_levels = set(cfg.traits["confusion"])
    expected_impatience_levels = set(cfg.traits["impatience"])
    assert td["confusion"] in expected_confusion_levels
    assert td["impatience"] in expected_impatience_levels


def test_mixing_requires_two_traits() -> None:
    """mix_traits=True requires at least two distinct traits."""
    cfg = SteerConfig(
        ages=["25"],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"confusion": [2]},
    )
    with pytest.raises(ValueError, match="at least two traits"):
        _ = cfg.combinations(mix_traits=True)
