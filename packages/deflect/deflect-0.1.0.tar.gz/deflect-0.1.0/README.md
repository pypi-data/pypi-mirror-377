# Deflect Python SDK

Early Python SDK for the Deflect Bot Protection API (experimental).

## Installation

Install PyPi package:
```bash
pip install deflect
```

## Quick Start (Sync)
```python
from deflect import Deflect, DeflectOptions

client = Deflect(DeflectOptions(api_key="YOUR_KEY", action_id="YOUR_ACTION"))
verdict = client.get_verdict(user_session_token)
if verdict.get("verdict", {}).get("can_pass"):
    # allow
    ...
else:
    # block
    ...
```

## Quick Start (Async)
```python
import asyncio
from deflect import AsyncDeflect, DeflectOptions

async def main():
    client = AsyncDeflect(DeflectOptions(api_key="YOUR_KEY", action_id="YOUR_ACTION"))
    verdict = await client.get_verdict(user_session_token)
    print(verdict)

asyncio.run(main())
```

## Configuration
`DeflectOptions`:
- `api_key` (str, required)
- `action_id` (str, required)
- `base_url` (str, default `https://api.deflect.bot`)
- `timeout` (float seconds, default 4.0)
- `max_retries` (int, default 2)
- `client` / `async_client` (inject custom `httpx` client instances)

## Errors
Raises `DeflectError` with attributes:
- `status` (int | None)
- `body` (parsed JSON or None)

## Testing
```bash
pytest -q
```

## Roadmap
- Optional exponential backoff
- Type refinements when API spec expands
- Streaming / additional endpoints

## License
MIT
