<!-- .github/copilot-instructions.md — guidance for AI coding agents working on this repo -->

# Copilot / AI Agent Instructions — studyDB

Purpose: give an AI agent the minimal, practical context to be productive in this FastAPI + SQLAlchemy codebase.

- Project type: FastAPI web app (Jinja2 server-side templates) backed by SQLAlchemy models (Postgres-oriented). Key entry: `app.py`.
- Main folders: `routes/` (API + page handlers), `models/` (DB engine & models), `core/` (mappings, permissions), `templates/` and `static/`.

Quick architecture summary
- `app.py` composes the application (includes routers from `routes/*`, mounts `static/`, and configures Jinja2 templates).
- DB layer: `models/database.py` creates `engine`, `SessionLocal`, and `get_db()` dependency; it also adapts `postgresql://` => `postgresql+psycopg://` for psycopg3.
- Schema: `models/tables.py` contains declarative models and relationships. Table names are snake_case (e.g. `product`, `orders_item`).
- Permissions: `core/permissions.py` defines `PermissionCode` enum and role-groupings; enforcement happens via `dependencies.require_permission()`.
- UI mapping: `core/mapping.py` maps technical names → Russian labels used in templates.

Developer workflows (how to run & debug)
- Install deps: `pip install -r requirements.txt` (use the project's Python environment).
- Dev server (PowerShell example):
  ```powershell
  $env:ENVIRONMENT = "development"
  $env:DEBUG = "True"
  python .\app.py
  ```
  or run `uvicorn app:app --reload --host 0.0.0.0 --port 8000` (the file `app.py` already calls `uvicorn.run()` when executed directly).
- Debugging tips:
  - Enable SQL logging by setting `DEBUG=True` (models.database sets `echo` accordingly).
  - The interactive OpenAPI UI is available at `/api/docs` only when `DEBUG` is true.
  - Health endpoints useful for checks: `/health`, `/api/db-check`, `/api/check-tables`, and `/api/config` (the latter is development-only).
- Database init: temporary helper endpoint `/api/init-db` calls `models.database.create_tables()` — use only in development.

Project-specific patterns & gotchas
- DB sessions: use the `get_db()` dependency. It yields a SQLAlchemy Session and must be closed after use.
- Query styles mixed: code uses `select()` + `db.scalar(...)` (preferred in this repo) and some legacy `db.query(Model)` patterns (e.g. `routes/dashboard.py`). Follow the existing style in the module you modify.
- Example select pattern (auth):
  - `employee = db.scalar(select(Employee).filter(Employee.login == form_data.username, Employee.password_hash == form_data.password, Employee.is_active == True))`
  - Note: passwords are currently compared in plaintext — do not silently change authentication behaviour without updating other parts and tests.
- Permissions and current user:
  - `dependencies.get_current_user()` is a temporary stub that returns the `admin` user or first active user. Real JWT auth is TODO.
  - `dependencies.require_permission(permission_code)` wraps endpoint dependencies and queries the DB to verify that `current_user.role_id` has that permission.
  - When adding protected endpoints, use `Depends(require_permission(PermissionCode.X))` like `routes/dashboard.py`.
- Templates & static files:
  - Templates live in `templates/` and use the `Jinja2Templates` instance configured in `app.py` and in specific routers (e.g. `routes/dashboard.py`).
  - Static files are served from `/static` via `app.mount()` in `app.py`.

Integration points & external deps
- Relies on a Postgres-compatible DB. Set `DATABASE_URL` in environment (e.g. `postgresql://user:pass@host:5432/dbname`). `models/database.py` will convert the scheme for psycopg3.
- Environment variables: `DATABASE_URL`, `DEBUG`, `ENVIRONMENT`, `PORT`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALGORITHM`.

Where to make common changes
- Add new API routes: create a file under `routes/`, define an `APIRouter`, then add `app.include_router(...)` in `app.py` (or update imports already present).
- Add/modify models: update `models/tables.py` and use `Base.metadata.create_all()` manually (or via `/api/init-db` in development).
- Add translations/labels for templates: update `core/mapping.py`.

Safety notes & high-signal TODOs (do not change silently)
- Authentication is incomplete:
  - `get_current_user()` is a stub (no JWT verification). Replacing this with JWT must preserve existing endpoints that rely on the returned `Employee` object.
  - Passwords are stored/compared in plaintext in current code — treat any auth changes as security-sensitive.
- Database creation endpoint `/api/init-db` and `create_tables()` are development helpers — do not enable or call in production.

Examples (copyable)
- Quick query pattern used here:
  ```py
  from sqlalchemy import select
  employee = db.scalar(select(Employee).where(Employee.login == login_value))
  ```
- Protect endpoint with a permission:
  ```py
  from dependencies import require_permission
  from core.permissions import PermissionCode

  @router.get('/secret')
  async def secret(current_user = Depends(require_permission(PermissionCode.REPORTS_VIEW))):
      return {'ok': True}
  ```

If something is missing
- I created this file from repo sources. If you have internal run scripts, CI config, or migration tooling not present in the repo, tell me and I will merge those details in.

Next step: ask here what area you'd like me to expand (auth, DB migrations, adding CI, or tests).
