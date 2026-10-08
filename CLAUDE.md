# CLAUDE.md

Move-In Day Cart Tracker: FastAPI + SQLAlchemy API on Render, PostgreSQL on Neon, React + Vite SPA on Vercel. See `README.md` for the overview, setup, and project structure.

## Commands

- Backend: `source venv/bin/activate && uvicorn app.main:app --reload`
- Tests: `pytest tests/ -v` (SQLite only; `tests/conftest.py` sets `DATABASE_URL`, so no `.env` or network needed)
- Frontend (from `frontend/`): `npm run dev`, `npm run build`, `npm run lint`

## Conventions

- **Time:** store every timestamp as naive UTC via `utc_now()`, never a DB default. A typed time with no offset is wall-clock in the site timezone (`Setting` table, default `America/Chicago`); a time with an offset is an exact instant. Responses serialize with `Z`. Frontend formats through `frontend/src/time.js`.
- **Auth:** the admin router applies `require_admin` at router level; login lives on the separate public `login_router`. `RequireAdmin` in the frontend only hides the page; the API is the real gate.
- **Public vs. admin API:** the public API is list, checkout, and return. Creating, editing, and deleting carts is admin-only (`/api/admin/carts`). Return and admin force-return share `close_session()` in `app/routers/carts.py`.
- **"Session"** in `app/models.py` is a cart checkout, not a SQLAlchemy or login session.
- **Schema changes:** tables come from `Base.metadata.create_all` in the `lifespan` startup hook in `app/main.py`, with no migrations. A column change to an existing table needs a manual change on Neon.
- **Tests:** SQLite via `app.dependency_overrides[get_db]`; admin env vars set with `monkeypatch`. Add a test for every new endpoint and failure path.
- **Frontend:** plain CSS, no component library. API calls use `import.meta.env.VITE_API_URL`.

## Git workflow

- One branch per issue (`feat/...`, `fix/...`, `docs/...`), then a pull request into `main`. CI runs tests on push to `main`, then deploys to Render.
- Pull request descriptions follow `.github/PULL_REQUEST_TEMPLATE.md`: at most three lines per section, and never restate the diff.
