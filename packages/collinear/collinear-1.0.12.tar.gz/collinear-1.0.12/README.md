# Collinear Python SDK

Persona‑driven chat simulation for OpenAI‑compatible endpoints.

Requires Python 3.10+.

## Install (uv)

```bash
uv venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv add collinear
uv sync
```

## Quickstart

```python
import os
from collinear.client import Client

client = Client(
    assistant_model_url="https://api.openai.com/v1",
    assistant_model_api_key=os.environ["OPENAI_API_KEY"],
    assistant_model_name="gpt-4o-mini",
    steer_api_key=os.environ.get("STEER_API_KEY", "demo-001"),
)

steer_config = {
    "ages": [29],
    "genders": ["woman"],
    "occupations": ["teacher"],
    "intents": ["Resolve billing issue"],
    "traits": {"impatience": [0, 1, 2]},
    "locations": ["United States"],
    "languages": ["English"],
    "tasks": ["telecom support"],
}

results = client.simulate(
    steer_config,
    k=1,
    num_exchanges=2,
    steer_temperature=0.7,
    steer_max_tokens=256,
    # max_concurrency defaults to 1 (uses /steer per request). Increase above 1 to
    # opt into /steer_batch with automatic grouping up to 8 concurrent samples.
    max_concurrency=1,
)

assessment = client.assess(results)
for row in assessment.evaluation_result:
    for score in row.values():
        print("score=", score.score, "rationale=", score.rationale)
```
