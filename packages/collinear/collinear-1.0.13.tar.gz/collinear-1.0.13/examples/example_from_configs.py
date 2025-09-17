"""Run a single simulation from a selected JSON config.

Discovers files matching `config_*.json` at the repo root, prompts you to
pick one, logs the normalized config, and runs exactly one simulation
with two exchanges.

Run: uv run python example_from_configs.py
Env: OPENAI_API_KEY (required); optional OPENAI_BASE_URL, OPENAI_ASSISTANT_MODEL, STEER_API_KEY
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

from collinear.client import Client
from collinear.schemas.steer import SteerConfig

ROOT = Path(__file__).resolve().parent
REPO_ENV = ROOT.parent / ".env"
CONFIG_DIR = ROOT / "example_configs"
DEFAULT_K = 1
DEFAULT_EXCHANGES = 2
CONFIG_FILE = "config_airline.json"


def _short(text: str, width: int = 160) -> str:
    return text if len(text) <= width else text[: width - 1] + "…"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _normalize(cfg: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-serializable view of the normalized config.

    Uses SteerConfig.from_input to apply defaulting and trait level coercion.
    """
    sc = SteerConfig.from_input(cfg)
    data = asdict(sc)

    return data


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger("collinear")

    env_values = dotenv_values(REPO_ENV)
    api_key = env_values.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(f"OPENAI_API_KEY is required in {REPO_ENV}")
    os.environ["OPENAI_API_KEY"] = api_key

    client = Client(
        assistant_model_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        assistant_model_api_key=api_key,
        assistant_model_name=os.getenv("OPENAI_ASSISTANT_MODEL", "gpt-4o-mini"),
        steer_api_key=os.getenv("STEER_API_KEY", "demo-001"),
    )

    choice = CONFIG_DIR / CONFIG_FILE
    if not choice.exists():
        raise SystemExit(f"Config file not found: {choice}")

    domain = choice.stem.removeprefix("config_")
    raw = _load(choice)
    steer_config = raw

    logger.info(
        "[%s] normalized steer_config =\n%s",
        domain,
        json.dumps(_normalize(raw), indent=2),
    )

    results = client.simulate(
        steer_config=steer_config,
        k=DEFAULT_K,
        num_exchanges=DEFAULT_EXCHANGES,
        batch_delay=0.5,
        mix_traits=False,
    )

    print(f"\nDomain: {domain} | Simulations: {len(results)}\n")
    for i, r in enumerate(results, 1):
        if not r.steer:
            continue
        traits_str = ", ".join(f"{k}:{v}" for k, v in r.steer.traits.items())
        print(f"{i:02d}. intent={r.steer.intent} | traits={{ {traits_str} }}")
        print(f"    assistant: {_short(r.response)}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
