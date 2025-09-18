"""Tests for pairwise trait mixing (mix_traits=True)."""

from __future__ import annotations

from typing import cast

import pytest
from openai.types.chat import ChatCompletionMessageParam

from collinear.schemas.steer import SteerConfig
from collinear.simulate.runner import SimulationRunner


class CaptureRunner(SimulationRunner):
    """Capture steer payloads for mixed trait tests."""

    def __init__(self) -> None:
        """Initialize the capture runner."""
        super().__init__(
            assistant_model_url="https://example.test",
            assistant_model_api_key="k",
            assistant_model_name="gpt-test",
            steer_api_key="demo-001",
        )
        self.captured_payloads: list[list[dict[str, object]]] = []

    async def _call_batch_endpoint(
        self,
        payloads: list[dict[str, object]],
        *,
        headers: dict[str, str],
    ) -> list[str]:
        _ = headers
        self.captured_payloads.append(payloads)
        return ["ok" for _ in payloads]

    async def _call_with_retry(
        self,
        _messages: list[ChatCompletionMessageParam],
        _system_prompt: str,
    ) -> str:
        return "assistant"


def _make_runner() -> CaptureRunner:
    return CaptureRunner()


def test_mixed_combinations_count_and_contents() -> None:
    """When mix_traits=True, generate pairwise combinations of intensities."""
    cfg = SteerConfig(
        ages=[25, 30],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing", "cancel"],
        traits={
            "confusion": [2],
            "impatience": [0, 2],
            "skeptical": [1],
        },
    )

    combos = cfg.combinations(mix_traits=True)

    base = 2 * 1 * 1 * 2
    pair_intensity_products = 5
    assert len(combos) == base * pair_intensity_products

    pair_size = 2
    assert all(len(c.traits) == pair_size for c in combos)


def test_mixed_payload_sends_two_traits() -> None:
    """Runner payload contains exactly two traits when mix_traits=True."""
    runner = _make_runner()
    cfg = SteerConfig(
        ages=[25],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"confusion": [2], "impatience": [0, 2]},
        locations=["US"],
        languages=["English"],
        tasks=["telecom"],
    )

    runner.run(config=cfg, k=1, num_exchanges=1, batch_delay=0.0, mix_traits=True, progress=False)
    assert runner.captured_payloads
    payload = runner.captured_payloads[-1][0]

    td = cast("dict[str, int]", payload["trait_dict"])
    assert set(td.keys()) == {"confusion", "impatience"}

    expected_confusion_levels = set(cfg.traits["confusion"])
    expected_impatience_levels = set(cfg.traits["impatience"])
    assert td["confusion"] in expected_confusion_levels
    assert td["impatience"] in expected_impatience_levels


def test_mixing_requires_two_traits() -> None:
    """mix_traits=True requires at least two distinct traits."""
    cfg = SteerConfig(
        ages=[25],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"confusion": [2]},
    )
    with pytest.raises(ValueError, match="at least two traits"):
        _ = cfg.combinations(mix_traits=True)
