# Backend Update Summary

## Scope
- Followed `experiments/scripts/prompt.md` endpoint contract.
- Updated backend only in router, schema, and service layers.
- Did not change any files under `app/models`.

## Main Changes
- Fixed `api.py` router registration to use the real `*_router.py` files.
- Added health endpoints under `/api/v1/health`.
- Added observability endpoints for managed table tree and Grafana variables.
- Added metric threshold CRUD endpoints for metadata, profiling, and AUC thresholds.
- Added quality result endpoints for summary, typed result lists, and unresolved failures.
- Added anomaly endpoints for AUC results, SHAP results, and verify resolve/unresolve.
- Added LightGBM parameter endpoints for CRUD, JSON validation, import, and table filtering.
- Updated connection routes to match the prompt, including `PUT /connections/{connection_id}` and schema table discovery.
- Updated table routes with `PUT`, columns, and processing-hours endpoints.
- Updated rule routes with `PUT`, activate/inactive, verify result list, resolve, and unresolve.

## Cleanup
- Removed stale router imports that pointed to non-existing modules.
- Replaced invalid empty service classes with minimal valid classes.
- Fixed broken schema and service imports that prevented the app from importing.

## Verification
- `python3 -m compileall app` passes.
- `uv run python -c 'from app.main import app; print(len(app.routes))'` passes and reports `105` routes.
