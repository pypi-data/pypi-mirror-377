"""Tests verifying Steer API payload shape and configurables."""

from __future__ import annotations

from typing import cast

from openai.types.chat import ChatCompletionMessageParam

from collinear.schemas.steer import SteerConfig
from collinear.simulate.runner import SimulationRunner

DEFAULT_STEER_TEMP = 0.7
DEFAULT_STEER_MAX = 256
DEFAULT_STEER_SEED = -1
OVERRIDE_STEER_TEMP = 0.33
OVERRIDE_STEER_MAX = 128
OVERRIDE_SEED = 42


class CaptureRunner(SimulationRunner):
    """Runner that captures steer payloads while avoiding network calls."""

    def __init__(self) -> None:
        """Initialize the capture runner."""
        super().__init__(
            assistant_model_url="https://example.test",
            assistant_model_api_key="k",
            assistant_model_name="gpt-test",
            steer_api_key="demo-001",
        )
        self.captured_headers: list[dict[str, str]] = []
        self.captured_payloads: list[list[dict[str, object]]] = []

    async def _call_batch_endpoint(
        self,
        payloads: list[dict[str, object]],
        *,
        headers: dict[str, str],
    ) -> list[str]:
        self.captured_headers.append(headers)
        self.captured_payloads.append(payloads)
        return ["ok" for _ in payloads]

    async def _call_with_retry(
        self,
        _messages: list[ChatCompletionMessageParam],
        _system_prompt: str,
    ) -> str:
        return "assistant"


def _payload_from_run(cfg: SteerConfig, runner: CaptureRunner | None = None) -> dict[str, object]:
    runner = runner or CaptureRunner()
    runner.run(config=cfg, k=1, num_exchanges=1, batch_delay=0.0, progress=False)
    assert runner.captured_payloads, "expected payload to be captured"
    return runner.captured_payloads[-1][0]


def test_steer_payload_uses_trait_dict_and_defaults() -> None:
    """Default payload uses trait_dict, temperature=0.7, max_tokens=256."""
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

    payload = _payload_from_run(cfg)

    assert payload["trait_dict"] == {"impatience": 1}
    assert payload["temperature"] == DEFAULT_STEER_TEMP
    assert payload["max_tokens"] == DEFAULT_STEER_MAX
    assert payload["seed"] == DEFAULT_STEER_SEED
    assert payload["messages"] == []

    user_characteristics = cast("dict[str, object]", payload["user_characteristics"])
    assert user_characteristics == {
        "age": 30,
        "gender": "female",
        "occupation": "engineer",
        "intent": "billing",
        "location": "San Francisco",
        "language": "English",
        "task": "telecom",
    }


def test_steer_payload_respects_overrides() -> None:
    """Overridden runner settings propagate into the payload."""
    runner = CaptureRunner()
    runner.steer_temperature = OVERRIDE_STEER_TEMP
    runner.steer_max_tokens = OVERRIDE_STEER_MAX
    runner.steer_seed = OVERRIDE_SEED

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

    payload = _payload_from_run(cfg, runner)

    assert payload["trait_dict"] == {"skeptical": 2}
    assert payload["temperature"] == OVERRIDE_STEER_TEMP
    assert payload["max_tokens"] == OVERRIDE_STEER_MAX
    assert payload["seed"] == OVERRIDE_SEED

    user_characteristics = cast("dict[str, object]", payload["user_characteristics"])
    assert user_characteristics["task"] == "telecom"


def test_payload_omits_missing_user_characteristics() -> None:
    """Absent user characteristics produce an empty dict."""
    cfg = SteerConfig(traits={"impatience": [0]})

    payload = _payload_from_run(cfg)

    assert payload["trait_dict"] == {"impatience": 0}
    assert payload["messages"] == []
    assert payload["user_characteristics"] == {}
