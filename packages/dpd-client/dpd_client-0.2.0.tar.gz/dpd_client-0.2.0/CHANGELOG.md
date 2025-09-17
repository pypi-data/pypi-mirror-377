# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-09-16
- API endpoints are snakecase
- add docs 
- test standardization for all endpoints 

## [0.1.1] - 2025-09-16
- Add all remaining DPD endpoints: form, packaging, pharmaceuticalstd, route, schedule, status, therapeuticclass, veterinaryspecies.
- Add Typer CLI subcommands for each endpoint.
- Add in-memory caching with `cache_ttl` option to sync and async clients.
- Expand tests: async client parity, error handling (404, JSON decode), retry behavior, caching.
- Improve README with CLI examples.

## [0.1.0] - 2025-09-16
- Initial scaffolding using `uv`.
- Implement core HTTP layer with retries and JSON parsing.
- Implement models and client methods for: drugproduct, company, activeingredient.
- Add initial CLI and basic unit tests.
