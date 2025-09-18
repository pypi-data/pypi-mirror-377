"""End-to-end, black box testing with mocked clients."""

from typing import cast

import httpx
import pytest

import collinear.simulate.runner as runner_module
from collinear.schemas.steer import SimulationResult
from collinear.schemas.steer import SteerConfig
from collinear.simulate.runner import SimulationRunner


@pytest.mark.asyncio
async def test_parallel_integration_with_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    """End-to-end: steer and assistant calls are mocked."""

    class FakeBar:
        def __init__(self, *, total: int, desc: str | None = None, unit: str | None = None) -> None:
            self.total = total
            self.n = 0
            self.desc = desc
            self.unit = unit

        def update(self, value: int) -> None:
            self.n += value

        def refresh(self) -> None:
            pass

        def close(self) -> None:
            pass

    def fake_progress_factory(
        total: int, desc: str | None = None, unit: str | None = None
    ) -> FakeBar:
        return FakeBar(total=total, desc=desc, unit=unit)

    monkeypatch.setattr(runner_module, "_PROGRESS_FACTORY", fake_progress_factory)

    async def fake_request_steer(
        _self: SimulationRunner,
        url: str,
        _headers: dict[str, str],
        _payload: dict[str, object],
    ) -> tuple[httpx.Response | None, str | None]:
        req = httpx.Request("POST", url)
        resp = httpx.Response(
            200, request=req, json=cast("dict[str, str]", {"response": "mock-user"})
        )
        return resp, None

    async def fake_call_with_retry(
        _self: SimulationRunner, _messages: list[dict[str, object]], _system_prompt: str
    ) -> str:
        return "mock-assistant"

    monkeypatch.setattr(SimulationRunner, "_request_steer", fake_request_steer)
    monkeypatch.setattr(SimulationRunner, "_call_with_retry", fake_call_with_retry)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        steer_api_key="demo-001",
    )

    config = SteerConfig(
        ages=[25],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"impatience": [1, 2]},
    )

    serial = await runner.run_async(
        config, k=2, num_exchanges=2, max_concurrency=1, batch_delay=0.0
    )
    parallel = await runner.run_async(
        config, k=2, num_exchanges=2, max_concurrency=2, batch_delay=0.0
    )

    assert len(serial) == len(parallel)

    for res in serial + parallel:
        assert len(res.conv_prefix) == (2 * 2 - 1)
        assert any(m["content"] == "mock-user" for m in res.conv_prefix if m["role"] == "user")
        assert res.response == "mock-assistant"

    def to_trait_items(result: SimulationResult) -> tuple[tuple[str, int], ...]:
        steer = result.steer
        assert steer is not None
        return tuple(sorted(steer.traits.items()))

    serial_traits = {to_trait_items(res) for res in serial}
    parallel_traits = {to_trait_items(res) for res in parallel}
    assert serial_traits == parallel_traits
