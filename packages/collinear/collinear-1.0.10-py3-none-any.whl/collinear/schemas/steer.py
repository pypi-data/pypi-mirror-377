"""Steer configuration schemas."""

from collections.abc import Iterable
from collections.abc import Mapping
from contextlib import suppress
from dataclasses import field
from enum import Enum
from itertools import combinations
from itertools import product
from typing import TypedDict
from typing import cast

from openai.types.chat import ChatCompletionMessageParam
from pydantic.dataclasses import dataclass

MIN_INTENSITY: float = 0.0
MAX_INTENSITY: float = 5.0
MIN_MIXED_TRAITS: int = 2


class Role(Enum):
    """Conversation role for a single turn."""

    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class SteerCombination:
    """Type definition for steer combinations.

    Each combination represents one concrete steer sample. The canonical
    representation stores ``traits`` as a mapping from trait name to its
    intensity. For backward compatibility, ``trait`` and ``intensity``
    properties expose the singular values when exactly one trait is used,
    else return ``None``.
    """

    age: str | None
    gender: str | None
    occupation: str | None
    intent: str | None
    traits: dict[str, float]
    location: str | None
    language: str | None

    @property
    def trait(self) -> str | None:
        """Return the single trait name if exactly one; else ``None``."""
        if len(self.traits) == 1:
            return next(iter(self.traits))
        return None

    @property
    def intensity(self) -> float | None:
        """Return the single trait intensity if exactly one; else ``None``."""
        if len(self.traits) == 1:
            return next(iter(self.traits.values()))
        return None


@dataclass
class SimulationResult:
    """Type definition for simulation results."""

    conv_prefix: list[ChatCompletionMessageParam]
    response: str
    steer: SteerCombination | None = None


@dataclass
class SteerConfig:
    """Configuration for steer generation.

    ``traits`` maps each trait name to a list of intensity levels (floats in [0, 5]).
    The generator emits one combination per intensity value for each trait.
    """

    ages: list[str] = field(default_factory=list)
    genders: list[str] = field(default_factory=list)
    occupations: list[str] = field(default_factory=list)
    intents: list[str] = field(default_factory=list)
    traits: dict[str, list[float]] = field(default_factory=dict)
    locations: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)

    @classmethod
    def from_input(cls, data: Mapping[str, object]) -> "SteerConfig":
        """Construct a SteerConfig from a potentially sparse mapping.

        - Missing axes default to empty lists (neutral in product).
        - Trait levels are coerced to float and filtered to [MIN_INTENSITY, MAX_INTENSITY].
        - Only the exact keys ``languages`` and ``locations`` are supported.
        """
        if not isinstance(data, Mapping):
            raise TypeError("from_input expects a mapping-like object")

        ages = SteerConfigFactory.get_str_list(data, "ages")
        genders = SteerConfigFactory.get_str_list(data, "genders")
        occupations = SteerConfigFactory.get_str_list(data, "occupations")
        intents = SteerConfigFactory.get_str_list(data, "intents")
        locations = SteerConfigFactory.get_str_list(data, "locations")
        languages = SteerConfigFactory.get_str_list(data, "languages")
        traits = SteerConfigFactory.get_traits(data)

        return cls(
            ages=ages,
            genders=genders,
            occupations=occupations,
            intents=intents,
            traits=traits,
            locations=locations,
            languages=languages,
        )

    def combinations(self, *, mix_traits: bool = False) -> list[SteerCombination]:
        """Generate all steer combinations from this config.

        - Default (``mix_traits=False``): one trait per combination, identical to
          the previous behavior.
        - Mixed (``mix_traits=True``): exactly two distinct traits are combined
          per combination. For each unordered trait pair (t1, t2), the Cartesian
          product of their intensity lists is used to form ``trait_dict`` values
          ``{t1: l1, t2: l2}``.

        Returns combinations in deterministic order based on input ordering.
        """
        ages = (
            cast("list[str | None]", self.ages) if self.ages else cast("list[str | None]", [None])
        )
        genders = (
            cast("list[str | None]", self.genders)
            if self.genders
            else cast("list[str | None]", [None])
        )
        occupations = (
            cast("list[str | None]", self.occupations)
            if self.occupations
            else cast("list[str | None]", [None])
        )
        intents = (
            cast("list[str | None]", self.intents)
            if self.intents
            else cast("list[str | None]", [None])
        )
        locations = (
            cast("list[str | None]", self.locations)
            if self.locations
            else cast("list[str | None]", [None])
        )
        languages = (
            cast("list[str | None]", self.languages)
            if self.languages
            else cast("list[str | None]", [None])
        )

        base = list(product(ages, genders, occupations, intents, locations, languages))

        levels_map = _normalize_trait_levels_map(self.traits)

        if not mix_traits:
            single_pairs = [
                (trait, level) for trait, levels in levels_map.items() for level in levels
            ]

            def _build_single(
                item: tuple[
                    tuple[
                        str | None,
                        str | None,
                        str | None,
                        str | None,
                        str | None,
                        str | None,
                    ],
                    tuple[str, float],
                ],
            ) -> SteerCombination:
                (age, gender, occupation, intent, location, language), (trait, level) = item
                return SteerCombination(
                    age=age,
                    gender=gender,
                    occupation=occupation,
                    intent=intent,
                    traits={trait: level},
                    location=location,
                    language=language,
                )

            return list(map(_build_single, product(base, single_pairs)))

        trait_names = [t for t, lvls in levels_map.items() if lvls]
        if len(trait_names) < MIN_MIXED_TRAITS:
            raise ValueError("mix_traits=True requires at least two traits with levels.")

        trait_pairs = list(combinations(trait_names, 2))

        pair_levels: list[tuple[str, float, str, float]] = []
        for t1, t2 in trait_pairs:
            pair_levels.extend((t1, l1, t2, l2) for l1 in levels_map[t1] for l2 in levels_map[t2])

        def _build_mixed(
            item: tuple[
                tuple[
                    str | None,
                    str | None,
                    str | None,
                    str | None,
                    str | None,
                    str | None,
                ],
                tuple[str, float, str, float],
            ],
        ) -> SteerCombination:
            (age, gender, occupation, intent, location, language), (t1, l1, t2, l2) = item
            return SteerCombination(
                age=age,
                gender=gender,
                occupation=occupation,
                intent=intent,
                traits={t1: l1, t2: l2},
                location=location,
                language=language,
            )

        return list(map(_build_mixed, product(base, pair_levels)))


class SteerConfigInput(TypedDict, total=False):
    """TypedDict describing the expected SteerConfig input shape.

    All keys are optional. When omitted or empty, axes are treated as neutral
    elements (i.e., they do not multiply combinations). An empty ``traits``
    mapping results in zero combinations in single-trait mode.
    """

    ages: list[str]
    genders: list[str]
    occupations: list[str]
    intents: list[str]
    traits: dict[str, list[float]]
    locations: list[str]
    languages: list[str]


def _as_float(value: float) -> float | None:
    """Best-effort conversion to float; returns None on failure."""
    with suppress(ValueError, TypeError):
        return float(value)
    return None


def _normalize_trait_levels(
    traits: dict[str, list[float]],
) -> Iterable[tuple[str, float]]:
    """Return an iterator over valid ``(trait, level)`` pairs.

    Levels are included only if convertible to ``float`` and within the inclusive
    range ``[MIN_INTENSITY, MAX_INTENSITY]``.
    """
    return (
        (trait, f)
        for trait, levels in traits.items()
        for f in (_as_float(lvl) for lvl in levels)
        if f is not None and MIN_INTENSITY <= f <= MAX_INTENSITY
    )


def _normalize_trait_levels_map(traits: dict[str, list[float]]) -> dict[str, list[float]]:
    """Return an ordered mapping of trait -> list[float] with validated levels.

    Preserves insertion order of both trait names and their intensity lists,
    including only values convertible to float within [MIN_INTENSITY, MAX_INTENSITY].
    """
    result: dict[str, list[float]] = {}
    for trait, levels in traits.items():
        vals: list[float] = []
        for lvl in levels:
            f = _as_float(lvl)
            if f is not None and MIN_INTENSITY <= f <= MAX_INTENSITY:
                vals.append(f)
        result[trait] = vals
    return result


@dataclass
class SteerConfigFactory:
    """Helper factory to construct a validated SteerConfig from loose input."""

    @staticmethod
    def get_str_list(data: Mapping[str, object], key: str) -> list[str]:
        """Return ``data[key]`` if it is a list[str]; else []."""
        value = data.get(key)
        if isinstance(value, list) and all(isinstance(x, str) for x in value):
            return list(value)
        return []

    @staticmethod
    def get_traits(data: Mapping[str, object]) -> dict[str, list[float]]:
        """Return normalized trait->levels mapping from a loose input mapping."""
        raw = data.get("traits")
        if not isinstance(raw, dict):
            return {}

        traits: dict[str, list[float]] = {}
        for k, v in raw.items():
            if not isinstance(k, str):
                continue
            if not isinstance(v, list):
                continue

            traits[k] = v
        return _normalize_trait_levels_map(traits)
