"""Steer configuration schemas."""

from collections.abc import Iterable
from collections.abc import Mapping
from contextlib import suppress
from dataclasses import field
from enum import Enum
from itertools import combinations
from itertools import product
from typing import SupportsInt
from typing import TypedDict

from openai.types.chat import ChatCompletionMessageParam
from pydantic.dataclasses import dataclass

MIN_INTENSITY: int = -2
MAX_INTENSITY: int = 2
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

    age: int | None
    gender: str | None
    occupation: str | None
    intent: str | None
    traits: dict[str, int]
    location: str | None
    language: str | None
    task: str | None

    @property
    def trait(self) -> str | None:
        """Return the single trait name if exactly one; else ``None``."""
        if len(self.traits) == 1:
            return next(iter(self.traits))
        return None

    @property
    def intensity(self) -> int | None:
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

    ``traits`` maps each trait name to a list of integer intensity levels in
    ``[-2, 2]``. The generator emits one combination per intensity value for each
    trait.
    """

    ages: list[int] = field(default_factory=list)
    genders: list[str] = field(default_factory=list)
    occupations: list[str] = field(default_factory=list)
    intents: list[str] = field(default_factory=list)
    traits: dict[str, list[int]] = field(default_factory=dict)
    locations: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    tasks: list[str] = field(default_factory=list)

    @classmethod
    def from_input(cls, data: Mapping[str, object]) -> "SteerConfig":
        """Construct a SteerConfig from a potentially sparse mapping.

        - Missing axes default to empty lists (neutral in product).
        - Trait levels must be integers within ``[MIN_INTENSITY, MAX_INTENSITY]``;
          values outside the range raise ``ValueError``.
        - Only the exact keys ``languages`` and ``locations`` are supported.
        """
        if not isinstance(data, Mapping):
            raise TypeError("from_input expects a mapping-like object")

        ages = SteerConfigFactory.get_int_list(data, "ages")
        genders = SteerConfigFactory.get_str_list(data, "genders")
        occupations = SteerConfigFactory.get_str_list(data, "occupations")
        intents = SteerConfigFactory.get_str_list(data, "intents")
        locations = SteerConfigFactory.get_str_list(data, "locations")
        languages = SteerConfigFactory.get_str_list(data, "languages")
        tasks = SteerConfigFactory.get_tasks(data)
        traits = SteerConfigFactory.get_traits(data)

        return cls(
            ages=ages,
            genders=genders,
            occupations=occupations,
            intents=intents,
            traits=traits,
            locations=locations,
            languages=languages,
            tasks=tasks,
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
        ages: list[int | None] = list(self.ages) if self.ages else [None]
        genders: list[str | None] = list(self.genders) if self.genders else [None]
        occupations: list[str | None] = list(self.occupations) if self.occupations else [None]
        intents: list[str | None] = list(self.intents) if self.intents else [None]
        locations: list[str | None] = list(self.locations) if self.locations else [None]
        languages: list[str | None] = list(self.languages) if self.languages else [None]
        tasks: list[str | None] = list(self.tasks) if self.tasks else [None]

        base = list(product(ages, genders, occupations, intents, locations, languages, tasks))

        levels_map = _normalize_trait_levels_map(self.traits)

        if not mix_traits:
            single_pairs = [
                (trait, level) for trait, levels in levels_map.items() for level in levels
            ]

            def _build_single(
                item: tuple[
                    tuple[
                        int | None,
                        str | None,
                        str | None,
                        str | None,
                        str | None,
                        str | None,
                        str | None,
                    ],
                    tuple[str, int],
                ],
            ) -> SteerCombination:
                (
                    (
                        age,
                        gender,
                        occupation,
                        intent,
                        location,
                        language,
                        task,
                    ),
                    (trait, level),
                ) = item
                return SteerCombination(
                    age=age,
                    gender=gender,
                    occupation=occupation,
                    intent=intent,
                    traits={trait: level},
                    location=location,
                    language=language,
                    task=task,
                )

            return list(map(_build_single, product(base, single_pairs)))

        trait_names = [t for t, lvls in levels_map.items() if lvls]
        if len(trait_names) < MIN_MIXED_TRAITS:
            raise ValueError("mix_traits=True requires at least two traits with levels.")

        trait_pairs = list(combinations(trait_names, 2))

        pair_levels: list[tuple[str, int, str, int]] = []
        for t1, t2 in trait_pairs:
            pair_levels.extend((t1, l1, t2, l2) for l1 in levels_map[t1] for l2 in levels_map[t2])

        def _build_mixed(
            item: tuple[
                tuple[
                    int | None,
                    str | None,
                    str | None,
                    str | None,
                    str | None,
                    str | None,
                    str | None,
                ],
                tuple[str, int, str, int],
            ],
        ) -> SteerCombination:
            (
                (
                    age,
                    gender,
                    occupation,
                    intent,
                    location,
                    language,
                    task,
                ),
                (t1, l1, t2, l2),
            ) = item
            return SteerCombination(
                age=age,
                gender=gender,
                occupation=occupation,
                intent=intent,
                traits={t1: l1, t2: l2},
                location=location,
                language=language,
                task=task,
            )

        return list(map(_build_mixed, product(base, pair_levels)))


class SteerConfigInput(TypedDict, total=False):
    """TypedDict describing the expected SteerConfig input shape.

    All keys are optional. When omitted or empty, axes are treated as neutral
    elements (i.e., they do not multiply combinations). An empty ``traits``
    mapping results in zero combinations in single-trait mode.
    """

    ages: list[int]
    genders: list[str]
    occupations: list[str]
    intents: list[str]
    traits: dict[str, list[int]]
    locations: list[str]
    languages: list[str]
    task: str
    tasks: list[str]


def _coerce_trait_intensity(trait: str, value: object) -> int:
    """Return a validated intensity or raise ``ValueError``."""
    iv: int

    if isinstance(value, bool):
        iv = int(value)
    elif isinstance(value, int):
        iv = value
    elif isinstance(value, str):
        try:
            iv = int(value)
        except ValueError as exc:
            msg = (
                f"Trait '{trait}' has non-integer intensity {value!r}; expected "
                f"integer in [{MIN_INTENSITY}, {MAX_INTENSITY}]."
            )
            raise TypeError(msg) from exc
    elif isinstance(value, SupportsInt):
        iv = int(value)
    else:
        msg = (
            f"Trait '{trait}' has non-integer intensity {value!r}; expected "
            f"integer in [{MIN_INTENSITY}, {MAX_INTENSITY}]."
        )
        raise TypeError(msg)

    if iv < MIN_INTENSITY or iv > MAX_INTENSITY:
        msg = f"Trait '{trait}' has intensity {iv} outside [{MIN_INTENSITY}, {MAX_INTENSITY}]."
        raise ValueError(msg)

    return iv


def _normalize_trait_levels(
    traits: dict[str, list[int]],
) -> Iterable[tuple[str, int]]:
    """Return an iterator over valid ``(trait, level)`` pairs.

    Levels are included only if convertible to ``int`` and within the inclusive
    range ``[MIN_INTENSITY, MAX_INTENSITY]``.
    """
    return (
        (trait, _coerce_trait_intensity(trait, lvl))
        for trait, levels in traits.items()
        for lvl in levels
    )


def _normalize_trait_levels_map(traits: dict[str, list[int]]) -> dict[str, list[int]]:
    """Return an ordered mapping of trait -> list[int] with validated levels.

    Preserves insertion order of both trait names and their intensity lists,
    including only values convertible to ``int`` within ``[MIN_INTENSITY, MAX_INTENSITY]``.
    """
    result: dict[str, list[int]] = {}
    for trait, levels in traits.items():
        vals: list[int] = []
        for lvl in levels:
            iv = _coerce_trait_intensity(trait, lvl)
            vals.append(iv)
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
    def get_int_list(data: Mapping[str, object], key: str) -> list[int]:
        """Return ``data[key]`` as ``list[int]`` when coercible; else []."""
        value = data.get(key)
        if not isinstance(value, list):
            return []

        ints: list[int] = []
        for item in value:
            with suppress(ValueError, TypeError):
                ints.append(int(item))
        return ints

    @staticmethod
    def get_tasks(data: Mapping[str, object]) -> list[str]:
        """Return normalized list of tasks (singular/plural) from ``data``."""
        tasks: list[str] = []

        raw_tasks = data.get("tasks")
        if isinstance(raw_tasks, list):
            for item in raw_tasks:
                if isinstance(item, (str, bytes)):
                    stripped = str(item).strip()
                    if stripped:
                        tasks.append(stripped)

        raw_task = data.get("task")
        if isinstance(raw_task, (str, bytes)):
            stripped = str(raw_task).strip()
            if stripped:
                tasks.append(stripped)

        return tasks

    @staticmethod
    def get_traits(data: Mapping[str, object]) -> dict[str, list[int]]:
        """Return normalized trait->levels mapping from a loose input mapping."""
        raw = data.get("traits")
        if not isinstance(raw, dict):
            return {}

        traits: dict[str, list[int]] = {}
        for k, v in raw.items():
            if not isinstance(k, str):
                continue
            if not isinstance(v, list):
                continue

            traits[k] = v
        return _normalize_trait_levels_map(traits)
