"""Example: pairwise trait mixing (mix_traits=True).

This script demonstrates how to opt into mixing exactly two traits per
steer call. It mirrors the structure of example.py but passes
``mix_traits=True`` to the client.

Environment:
- OPENAI_API_KEY (required)
- OPENAI_BASE_URL (optional, default https://api.openai.com/v1)
- OPENAI_ASSISTANT_MODEL (optional, default gpt-4o-mini)
- STEER_API_KEY (optional, default demo-001)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import dotenv_values

from collinear.client import Client
from collinear.schemas.steer import SteerConfigInput

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


def _load_env(*required: str) -> None:
    values = dotenv_values(ENV_PATH)
    missing = [key for key in required if not values.get(key)]
    if missing:
        joined = ", ".join(sorted(missing))
        raise SystemExit(
            f"Missing required values in {ENV_PATH}: {joined}. Populate the file and retry."
        )
    for key, value in values.items():
        if value:
            os.environ[key] = value


def _print_header(title: str) -> None:
    line = "=" * len(title)
    print(line)
    print(title)
    print(line)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("collinear")

    _load_env("OPENAI_API_KEY")
    api_key = os.environ["OPENAI_API_KEY"]

    client = Client(
        assistant_model_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        assistant_model_api_key=api_key,
        assistant_model_name=os.getenv("OPENAI_ASSISTANT_MODEL", "gpt-4o-mini"),
        steer_api_key=os.getenv("STEER_API_KEY", "demo-001"),
    )

    steer_config: SteerConfigInput = {
        "ages": ["young adult"],
        "genders": ["woman"],
        "occupations": ["teacher"],
        "intents": ["Resolve billing issue", "Cancel service"],
        "traits": {
            "confusion": [2],
            "impatience": [0, 3],
            "skeptical": [1],
        },
    }

    simulations = client.simulate(
        steer_config=steer_config,
        k=3,
        num_exchanges=2,
        batch_delay=0.2,
        mix_traits=True,
    )

    logger.info("Received %d simulation results", len(simulations))

    for i, sim in enumerate(simulations, start=1):
        _print_header(f"Conversation {i}")
        p = sim.steer
        if p is not None:
            if p.trait is not None:
                trait_str = f"trait={p.trait} intensity={p.intensity}"
            else:
                trait_str = ", ".join(f"{k}:{v}" for k, v in p.traits.items())
                trait_str = f"traits={{ {trait_str} }}"
            print(
                "Steer:\n"
                f"age={p.age}\n"
                f"gender={p.gender}\n"
                f"occupation={p.occupation}\n"
                f"intent={p.intent}\n"
                f"{trait_str}"
            )
        print("---")
        for msg in sim.conv_prefix:
            role = str(msg.get("role", ""))
            content = str(msg.get("content", ""))
            if content:
                print(f"{role}: {content}")
        print(f"assistant: {sim.response}")
        print()


if __name__ == "__main__":
    main()
