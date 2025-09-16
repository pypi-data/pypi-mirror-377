"""Timing-focused example: measure round-trip durations.

This script copies the setup from `example.py` but removes conversation
printing. Instead, it runs a number of short simulations and records how
long each conversation takes end-to-end. From that it reports:

- Average time per single round trip (one user+assistant pair)
- Approximate time for an average conversation of 6 exchanges

Notes
-----
- Here, an "exchange" means a user turn followed by an assistant turn.
  So `--exchanges 6` corresponds to 12 total turns (6 user + 6 assistant).
- We time each conversation by calling the high-level `client.simulate` with
  `k=1` and dividing the measured duration by `exchanges` to estimate the
  average round-trip. This yields a good practical approximation without
  modifying internals.

"""

from __future__ import annotations

import argparse
import logging
import os
import statistics
import time
from collections.abc import Sequence
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


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Measure conversation timing metrics")
    p.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of conversations to time (default: 5)",
    )
    p.add_argument(
        "--exchanges",
        type=int,
        default=6,
        help=(
            "User+assistant exchanges per conversation (default: 6). "
            "Each exchange is one user turn followed by one assistant turn."
        ),
    )
    p.add_argument(
        "--batch-delay",
        type=float,
        default=0.0,
        help="Delay between samples inside a single simulate call (default: 0.0)",
    )
    p.add_argument(
        "--estimate-round-trips",
        type=int,
        default=6,
        help=(
            "Report estimated duration for this many round trips/exchanges "
            "(default: 6). One round trip = user + assistant."
        ),
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce logging noise (only warnings/errors)",
    )
    return p.parse_args(argv)


def _configure_logging(quiet: bool) -> None:
    level = logging.WARNING if quiet else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("collinear").setLevel(level)


def main(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)
    _configure_logging(args.quiet)

    _load_env("OPENAI_API_KEY")
    api_key = os.environ["OPENAI_API_KEY"]

    client = Client(
        assistant_model_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        assistant_model_api_key=api_key,
        assistant_model_name=os.getenv("OPENAI_ASSISTANT_MODEL", "gpt-4o-mini"),
        steer_api_key=os.getenv("PERSONA_API_KEY", "demo-001"),
    )

    steer_config: SteerConfigInput = {
        "ages": ["young adult", "middle-aged", "senior"],
        "genders": ["man", "woman"],
        "occupations": [
            "teacher",
            "software engineer",
            "nurse",
            "retired",
            "small business owner",
        ],
        "intents": [
            "Resolve billing issue",
            "Cancel service",
            "Update plan",
            "Activate internet connectivity",
            "Device troubleshooting",
        ],
        "traits": {
            "confusion": [2],
            "impatience": [0, 3],
        },
    }

    runs = max(1, int(args.runs))
    exchanges = max(1, int(args.exchanges))

    durations: list[float] = []
    for i in range(runs):
        start = time.perf_counter()

        _ = client.simulate(
            steer_config=steer_config,
            k=1,
            num_exchanges=exchanges,
            batch_delay=float(args.batch_delay),
        )
        end = time.perf_counter()
        durations.append(end - start)

    avg_conv = statistics.fmean(durations)
    min_conv = min(durations)
    max_conv = max(durations)
    stdev_conv = statistics.pstdev(durations) if len(durations) > 1 else 0.0

    avg_round_trip = avg_conv / exchanges

    est_pairs = max(1, int(args.estimate_round_trips))
    est_duration = avg_round_trip * est_pairs

    approx_six_total_turns = avg_round_trip * 3

    print("== Timing Metrics ==")
    print(f"Runs: {runs}")
    print(f"Exchanges per conversation: {exchanges} (user+assistant pairs)")
    print(
        f"Average conversation duration: {avg_conv:.3f}s (min={min_conv:.3f}s, max={max_conv:.3f}s, stdev={stdev_conv:.3f}s)"
    )
    print(f"Average time per single round trip: {avg_round_trip:.3f}s")
    print(
        f"Estimated duration for {est_pairs} round trips (~{est_pairs * 2} turns): {est_duration:.3f}s"
    )


if __name__ == "__main__":
    main()
