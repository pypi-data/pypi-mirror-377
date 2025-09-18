"""Ensure SimulationRunner sends only the canonical Steer API header."""

from __future__ import annotations

from openai.types.chat import ChatCompletionMessageParam

from collinear.schemas.steer import SteerConfig
from collinear.simulate.runner import SimulationRunner


class CaptureRunner(SimulationRunner):
    """Capture headers from steer batch calls."""

    def __init__(self) -> None:
        """Initialize the capture runner."""
        super().__init__(
            assistant_model_url="https://example.test",
            assistant_model_api_key="k",
            assistant_model_name="gpt-test",
            steer_api_key="steer-secret",
        )
        self.captured_headers: list[dict[str, str]] = []

    async def _call_batch_endpoint(
        self,
        payloads: list[dict[str, object]],
        *,
        headers: dict[str, str],
    ) -> list[str]:
        self.captured_headers.append(headers)
        return ["ok" for _ in payloads]

    async def _call_with_retry(
        self,
        _messages: list[ChatCompletionMessageParam],
        _system_prompt: str,
    ) -> str:
        return "assistant"


def test_steer_headers_use_api_key_only() -> None:
    """USER calls include only `API-Key` header (no `X-API-Key`)."""
    runner = CaptureRunner()

    cfg = SteerConfig(
        ages=[25],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"impatience": [1]},
    )

    runner.run(config=cfg, k=1, num_exchanges=1, batch_delay=0.0, progress=False)
    assert runner.captured_headers
    headers = runner.captured_headers[-1]
    assert headers == {"Content-Type": "application/json", "API-Key": "steer-secret"}
