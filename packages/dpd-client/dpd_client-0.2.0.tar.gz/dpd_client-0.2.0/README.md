# dpd-client

Python client and CLI for Health Canada Drug Product Database (DPD) API.

**Documentation:** https://health-products.canada.ca/api/documentation/dpd-documentation-en.html

## Quick Start

### Installation

```bash
uv sync  # Creates .venv and installs dependencies
```

### Basic Usage

**Synchronous client:**

```python
from dpd_client import DPDClient

client = DPDClient()
try:
    products = client.drug_product(din="00326925")
    for p in products:
        print(p.brand_name, p.drug_identification_number)
finally:
    client.close()
```

**Asynchronous client:**

```python
import asyncio
from dpd_client import AsyncDPDClient

async def main() -> None:
    client = AsyncDPDClient()
    try:
        products = await client.drug_product(din="00326925")
        for p in products:
            print(p.brand_name, p.drug_identification_number)
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
```

Example scripts are available in `examples/`:

```bash
uv run python examples/sync_drug_product.py
uv run python examples/async_drug_product.py
```

## Command Line Interface

After `uv run` or activating the venv:

```bash
# Drug products (defaults to JSON output)
dpd drugproduct --din 00326925

# Other endpoints
dpd company --id 10825
dpd activeingredient --id 48905
dpd form --id 10846
dpd route --id 3
dpd schedule --id 10687
dpd status --id 2049
dpd packaging --id 11685
dpd pharmaceuticalstd --id 11534
dpd therapeuticclass --id 10564
dpd veterinaryspecies --id 13755

# French language
dpd drugproduct --din 00326925 --lang fr
```

## Features

### Caching

Enable in-memory caching by passing `cache_ttl` (seconds) to the client:

```python
client = DPDClient(cache_ttl=60)  # Cache for 60 seconds
```

### Error Handling & Retries

- **Automatic retries** with exponential backoff for `429` and `5xx` responses
- **4xx errors** raise `DPDHTTPError` without retry
- **Invalid JSON** raises `DPDDecodeError`

### Available Endpoints

- `drug_product` - Drug product information
- `company` - Pharmaceutical companies
- `active_ingredient` - Active ingredients
- `form` - Dosage forms
- `route` - Administration routes
- `schedule` - Drug schedules
- `status` - Product statuses
- `packaging` - Packaging information
- `pharmaceutical_std` - Pharmaceutical standards
- `therapeutic_class` - Therapeutic classifications
- `veterinary_species` - Veterinary species

## Development

### Running Tests

```bash
uv run pytest -q
```

**Test coverage:**
- Parameter validation and list normalization
- Retry logic for transient `5xx` responses
- Caching prevents redundant requests
- Async client parity using `pytest-asyncio`
- HTTP calls mocked with `respx` (no live network calls)

### Code Quality

```bash
uv run ruff check .    # Linting
uv run mypy .          # Type checking
```

### Release Workflow

The repository includes a helper script for repeatable releases:

```bash
uv run python scripts/release.py --version 0.2.0      # run checks and build
uv run python scripts/release.py --version 0.2.0 --publish  # publish via uv
```

The script verifies a clean git tree, loads environment variables from `.env` via `python-dotenv`, runs linting/type checks/tests, builds distributions, and (optionally) uploads to PyPI using your configured credentials.

### Project Structure

```
.
├── AGENTS.md                  # Agent conventions
├── CHANGELOG.md               # Version history
├── pyproject.toml             # Project config & dependencies
├── src/dpd_client/
│   ├── __init__.py            # Public exports
│   ├── cli.py                 # CLI commands
│   ├── client.py              # Sync & async clients
│   ├── errors.py              # Exception types
│   ├── http.py                # HTTP helpers with retries/caching
│   ├── models.py              # Pydantic models
│   └── params.py              # Parameter validation
└── tests/                     # Test suite
```

### Key Files

- **`http.py`** - HTTP client with retries, backoff, and optional caching
- **`models.py`** - Pydantic v2 models with forward compatibility
- **`client.py`** - Main client classes returning lists of models
- **`params.py`** - Shared parameter builders for DRY validation
- **`errors.py`** - Custom exceptions for different error types

## Status

⚠️ **Not ready for publication** - Additional testing and validation planned.

## License

MIT License - see [LICENSE](LICENSE) file.
