"""Tests exercising the conversation runner without network calls."""

from __future__ import annotations

from _pytest.monkeypatch import MonkeyPatch
from openai.types.chat import ChatCompletionMessageParam

import collinear.simulate.runner as runner_module
from collinear.schemas.steer import Role
from collinear.schemas.steer import SteerCombination
from collinear.schemas.steer import SteerConfig
from collinear.simulate.runner import SimulationRunner


def test_run_builds_conversation_and_returns_results(monkeypatch: MonkeyPatch) -> None:
    """Monkeypatch turn generation to validate run() behavior without network."""

    def fake_generate(
        _self: SimulationRunner,
        _combo: SteerCombination,
        _conversation: list[ChatCompletionMessageParam],
        role: Role,
    ) -> str:
        return {Role.USER: "u", Role.ASSISTANT: "a"}[role]

    monkeypatch.setattr(SimulationRunner, "_generate_turn", fake_generate)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        steer_api_key="demo-001",
    )

    config = SteerConfig(
        ages=["25"],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"impatience": [1]},
    )

    results = runner.run(
        config=config,
        k=1,
        num_exchanges=2,
        batch_delay=0.0,
        progress=False,
    )
    assert len(results) == 1
    res = results[0]

    assert [m["role"] for m in res.conv_prefix] == ["user", "assistant", "user"]
    assert res.response == "a"


def test_progress_updates_per_user_turn(monkeypatch: MonkeyPatch) -> None:
    """Progress bar receives one update per user turn when enabled."""
    updates: list[int] = []
    totals: list[int] = []
    closed: list[bool] = []

    class FakeBar:
        def __init__(
            self,
            total: int | None = None,
            desc: str | None = None,
            unit: str | None = None,
        ) -> None:
            if not isinstance(total, int):
                raise TypeError("expected integer total")
            totals.append(total)
            self.total = total
            self.n = 0
            self.desc = desc
            self.unit = unit

        def update(self, value: int) -> None:
            self.n += value
            updates.append(value)

        def refresh(self) -> None:
            pass

        def close(self) -> None:
            closed.append(True)

    def fake_tqdm(*, total: int, desc: str | None = None, unit: str | None = None) -> FakeBar:
        return FakeBar(total=total, desc=desc, unit=unit)

    monkeypatch.setattr(runner_module, "_PROGRESS_FACTORY", fake_tqdm)

    def fake_generate(
        _self: SimulationRunner,
        _combo: SteerCombination,
        _conversation: list[ChatCompletionMessageParam],
        role: Role,
    ) -> str:
        return {Role.USER: "u", Role.ASSISTANT: "a"}[role]

    monkeypatch.setattr(SimulationRunner, "_generate_turn", fake_generate)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        steer_api_key="demo-001",
    )

    config = SteerConfig(
        ages=["25"],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"impatience": [1]},
    )

    results = runner.run(config=config, k=1, num_exchanges=2, batch_delay=0.0)

    assert len(results) == 1
    assert totals == [2]
    assert updates == [1, 1]
    assert closed == [True]


def test_progress_adjusts_when_simulation_skipped(monkeypatch: MonkeyPatch) -> None:
    """Progress total shrinks when a simulation aborts early."""
    bars: list[FakeBar] = []
    updates: list[int] = []

    class FakeBar:
        def __init__(
            self,
            total: int | None = None,
            desc: str | None = None,
            unit: str | None = None,
        ) -> None:
            if not isinstance(total, int):
                raise TypeError("expected integer total")
            self.total = total
            self.n = 0
            self.desc = desc
            self.unit = unit
            bars.append(self)

        def update(self, value: int) -> None:
            self.n += value
            updates.append(value)

        def refresh(self) -> None:
            pass

        def close(self) -> None:
            pass

    def fake_tqdm(*, total: int, desc: str | None = None, unit: str | None = None) -> FakeBar:
        return FakeBar(total=total, desc=desc, unit=unit)

    monkeypatch.setattr(runner_module, "_PROGRESS_FACTORY", fake_tqdm)

    def failing_generate(
        _self: SimulationRunner,
        _combo: SteerCombination,
        _conversation: list[ChatCompletionMessageParam],
        role: Role,
    ) -> str:
        if role is Role.USER:
            raise SimulationRunner.InvalidTraitError("bad trait")
        return "a"

    monkeypatch.setattr(SimulationRunner, "_generate_turn", failing_generate)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        steer_api_key="demo-001",
    )

    config = SteerConfig(
        ages=["25"],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"impatience": [1]},
    )

    results = runner.run(config=config, k=1, num_exchanges=2, batch_delay=0.0)

    assert results == []
    assert updates == [1]
    assert len(bars) == 1
    assert bars[0].total == 1
