"""Unit tests for steer configuration helpers."""

from __future__ import annotations

import pytest

from collinear.schemas.steer import SteerConfig


def test_combinations_count_and_contents() -> None:
    """Generate all combinations and validate counts and fields."""
    config = SteerConfig(
        ages=[25, 30],
        genders=["female"],
        occupations=["engineer"],
        intents=["billing"],
        traits={"impatience": [1], "skeptical": [1]},
        tasks=["telecom"],
    )

    combos = config.combinations()

    expected_count = 2 * 1 * 1 * 1 * (1 + 1)
    assert len(combos) == expected_count

    assert {c.age for c in combos} == {25, 30}
    assert {c.trait for c in combos} == {"impatience", "skeptical"}
    assert {c.task for c in combos} == {"telecom"}

    assert all(c.intensity is not None for c in combos)
    assert {c.intensity for c in combos} == {1}


def test_invalid_trait_intensity_raises() -> None:
    """Out-of-range trait intensities should fail fast."""
    data = {
        "traits": {
            "impatience": [3],
        }
    }

    with pytest.raises(ValueError, match="Trait 'impatience' has intensity 3 outside"):
        SteerConfig.from_input(data)


def test_non_integer_trait_intensity_raises() -> None:
    """Non-integer intensities raise a helpful error."""
    data = {
        "traits": {
            "impatience": ["high"],
        }
    }

    with pytest.raises(TypeError, match="non-integer intensity"):
        SteerConfig.from_input(data)


def test_from_input_collects_task_fields() -> None:
    """Single and plural task keys are normalized into the config."""
    data = {
        "traits": {"impatience": [0]},
        "task": "telecom",
        "tasks": ["retail", ""],
    }

    cfg = SteerConfig.from_input(data)
    assert cfg.tasks == ["retail", "telecom"]
