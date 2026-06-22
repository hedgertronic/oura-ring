# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1]

### Changed
- Updated README and package metadata to match the GitHub About description.

## [1.0.0]

### Added
- OAuth2 support via `OuraAuth` (authorization-code flow): build the
  authorize URL, exchange the code for tokens, and refresh tokens. Verified
  end-to-end against Oura's live endpoints, including single-use refresh-token
  rotation.
- OAuth token revocation via `OuraAuth.revoke_token(...)`.
- New endpoints: `get_daily_resilience`, `get_daily_cardiovascular_age`,
  `get_vo2_max`, and `get_ring_battery_level` (19 endpoints total).
- `latest` support for heart rate and ring battery time-series routes.
- `py.typed` marker — the package now ships its inline type annotations (PEP 561).
- `oura_ring.__version__`.
- GitHub Actions CI across Python 3.12–3.14 (ruff, mypy, pytest with coverage).
- Test suite (mocked HTTP, no live calls): 100% coverage.

### Changed
- `OuraClient` now accepts an OAuth2 `access_token`; the legacy
  `personal_access_token` is still accepted (positionally or by keyword) for
  backward compatibility.
- Packaged as the `oura_ring/` package (`client.py`, `auth.py`); the public
  import path `from oura_ring import OuraClient` is unchanged.
- Migrated tooling from Poetry to uv + PEP 621; replaced flake8/black/isort/
  pylint/pyupgrade with ruff.
- Minimum supported Python is now 3.12; CI runs against 3.12–3.14.

### Fixed
- `get_enhanced_tag(document_id=...)` previously called the paginated helper and
  raised `KeyError` on the single-document response; it now uses a single request.
- `get_heart_rate` / `get_ring_battery_level` no longer raise `TypeError` when one
  of the datetime bounds is timezone-aware and the other defaults to naive.
- `get_ring_configuration()` no longer sends unsupported date filters on the list
  route.
- Ring battery and heart rate examples now match the current OpenAPI response
  fields.

### Notes
- Personal access tokens were deprecated by Oura in December 2025; new ones can no
  longer be created, though previously-issued tokens may still work. New
  integrations should use OAuth2.
- Non-goals for this release (deliberate, to keep the client simple): automatic
  token refresh / 429 retry (the client raises; use `OuraAuth.refresh_token`
  to rotate), the `fields` query param, and the webhook subscription API.
