"""Backwards compatibility: user can override USER_PROMPT_TEMPLATE."""

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
                status_code=200,
                json=cast("dict[str, object]", {"response": "ok"}),
            )

    monkeypatch.setattr(httpx, "Client", cast("type[httpx.Client]", FakeClient))


def test_user_prompt_template_override(monkeypatch: MonkeyPatch) -> None:
    """Setting USER_PROMPT_TEMPLATE yields exact system prompt content."""
    captured: _Captured = {"url": "", "headers": {}, "json": {}}
    _install_fake_http(monkeypatch, captured)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="k",
        assistant_model_name="gpt-test",
        steer_api_key="demo-001",
    )

    runner.USER_PROMPT_TEMPLATE = (
        "You are a {age} year old {gender}, who works as {article} {occupation}. "
        "You are {trait}. Your intention is: {intent}. "
        "Location={location}; Language={language}."
    )

    cfg = SteerConfig(
        ages=["35"],
        genders=["female"],
        occupations=["engineer"],
        intents=["booking"],
        traits={"impatience": [2]},
        locations=["US"],
        languages=["Spanish"],
    )

    _ = runner.run(config=cfg, k=1, num_exchanges=1, batch_delay=0.0)

    messages = cast("list[dict[str, object]]", captured["json"].get("messages", []))
    assert messages
    sys_prompt = cast("str", messages[0].get("content"))
    assert (
        sys_prompt == "You are a 35 year old female, who works as an engineer. You are impatience. "
        "Your intention is: booking. Location=US; Language=Spanish."
    )
