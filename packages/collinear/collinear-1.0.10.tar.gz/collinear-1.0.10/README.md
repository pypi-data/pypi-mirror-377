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
    "ages": ["young adult"],
    "genders": ["woman"],
    "occupations": ["teacher"],
    "intents": ["Resolve billing issue"],
    "traits": {"impatience": [0.0, 2.5, 4.0]},
}

results = client.simulate(
    steer_config,
    k=1,
    num_exchanges=2,
    steer_temperature=0.7,
    steer_max_tokens=256,
)

assessment = client.assess(results)
for row in assessment.evaluation_result:
    for score in row.values():
        print("score=", score.score, "rationale=", score.rationale)
```
