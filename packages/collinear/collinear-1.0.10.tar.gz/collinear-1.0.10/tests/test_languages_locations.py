"""Tests covering optional languages/locations axes and dynamic prompt lines."""

from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING
from typing import TypedDict
from typing import cast

import httpx
from _pytest.monkeypatch import MonkeyPatch
from typing_extensions import Self

from collinear.schemas.steer import SteerConfig
from collinear.simulate.runner import SimulationRunner


def test_single_trait_count_scales_with_languages_locations() -> None:
    """Combinations multiply by languages/locations when provided."""
    cfg = SteerConfig(
        ages=["25"],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"impatience": [1, 2]},
        locations=["US"],
        languages=["English", "Spanish"],
    )

    combos = cfg.combinations()

    base = 1 * 1 * 1 * 1 * 1 * 2
    assert len(combos) == base * 2


def test_mixed_trait_count_with_new_axes() -> None:
    """mix_traits=True scales by new axes as expected."""
    cfg = SteerConfig(
        traits={
            "confusion": [1],
            "impatience": [0, 3],
            "skeptical": [1],
        },
        locations=["US", "CA"],
        languages=["en", "es"],
    )

    combos = cfg.combinations(mix_traits=True)
    base = 1 * 1 * 1 * 1 * 2 * 2
    pair_products = 2 + 1 + 2
    assert len(combos) == base * pair_products


class _Captured(TypedDict):
    url: str
    headers: dict[str, str]
    json: dict[str, object]


if TYPE_CHECKING:
    from types import TracebackType


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
                status_code=200, json=cast("dict[str, object]", {"response": "ok"})
            )

    monkeypatch.setattr(httpx, "Client", cast("type[httpx.Client]", FakeClient))


def test_user_prompt_includes_location_and_language(monkeypatch: MonkeyPatch) -> None:
    """System prompt lists Location/Language lines when provided."""
    captured: _Captured = {"url": "", "headers": {}, "json": {}}
    _install_fake_http(monkeypatch, captured)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="k",
        assistant_model_name="gpt-test",
        steer_api_key="demo-001",
    )

    cfg = SteerConfig(
        traits={"impatience": [2]},
        locations=["US"],
        languages=["Spanish"],
    )

    _ = runner.run(config=cfg, k=1, num_exchanges=1, batch_delay=0.0)

    payload = captured["json"]
    messages = cast("list[dict[str, object]]", payload.get("messages", []))
    assert messages
    sys0 = cast("str", messages[0].get("content"))
    assert "Location: US" in sys0
    assert "Language: Spanish" in sys0
