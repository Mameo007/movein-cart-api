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
- **Docs:** use the terms in `docs/requirements/project-glossary.md` (say "checkout" in prose, not "session"). Check `docs/requirements/business-rules.md` before changing behavior and update it in the same PR. Before building an issue, read its design in `docs/design/` and any `OPEN-ISSUES.md` entry it depends on; record a new unanswered question there instead of guessing.
- **Schema changes:** tables come from `Base.metadata.create_all` in the `lifespan` startup hook in `app/main.py`, with no migrations. A column change to an existing table needs a manual change on Neon.
- **Tests:** SQLite via `app.dependency_overrides[get_db]`; admin env vars set with `monkeypatch`. Add a test for every new endpoint and failure path.
- **Frontend:** plain CSS, no component library. API calls use `import.meta.env.VITE_API_URL`.

## Writing

These apply to every piece of text in the repo: docs, comments, UI strings, API errors, tests, and commits. Follow them in new and edited text; don't reword untouched lines just to comply.

- **Words:** plain words, short sentences, active voice. One term per concept, from `docs/requirements/project-glossary.md`: "checkout", not "session", in anything a person reads (docs, UI, error messages). The `Session` class and `/sessions` URLs keep their names.
- **Names:** see [Naming](#naming) below.
- **Comments and docstrings:** a comment says why, not what (`# Sessions point at the cart, so they have to go first`). Docstrings are one line in the present tense starting with a verb ("Ends a session from the admin side..."). Router sections use `# --- NAME ---` banners.
- **API errors** (`HTTPException` `detail`): sentence case, no trailing period, the subject first ("Cart not found", "Cart is checked out -- return it first"). Same wording for the same failure across endpoints.
- **UI text:** Title Case for buttons, headings, and placeholders ("Mark Returned", "First Name"). Sentence case with a period for messages ("No carts are currently checked out."). Show the API's `detail` rather than writing a second message for the same error.
- **Docs:** sentence-case headings, except arc42's numbered titles in `architectural-design.md`. Cite rules and issues by ID (`BR-...`, `OI-...`) instead of restating them. Code names and paths in backticks. Dates as `YYYY-MM-DD`, never "today" or "last week".
- **Punctuation:** ASCII only in code and messages; write a dash as `--`. No em dashes in docs: use a colon, a comma, or two sentences.
- **Commits:** one imperative subject line that stands alone in the history ("Keep the tests off the production database"), with a body that explains why when it isn't obvious.

### Naming

Match the existing pattern for the kind of thing you're naming. Data keeps one spelling end to end: a column `due_at` is `due_at` in the schema, the JSON, and the frontend's `session.due_at`, never `dueAt`.

**Backend (Python)**

| Thing | Style | Example |
|---|---|---|
| Module | `snake_case.py`, a noun | `timezones.py`, `routers/carts.py` |
| Function, variable | `snake_case` | `get_site_timezone`, `cart_number` |
| Route handler | `verb_resource[_field]` | `checkout_cart`, `update_session_due_at`, `force_return_session` |
| Helper used in one module | leading underscore | `_to_response`, `_get_cart_or_404` |
| Predicate | `is_` / `verify_` | `is_valid_timezone`, `verify_password` |
| Constant | `UPPER_SNAKE` | `DEFAULT_TIMEZONE`, `TOKEN_TTL_HOURS` |
| SQLAlchemy model | singular `PascalCase` | `Cart`, `Setting` |
| Table | plural `snake_case` | `carts`, `settings` |
| Column | `snake_case`; timestamps `<event>_at`, foreign keys `<entity>_id` | `checked_out_at`, `cart_id` |
| Pydantic request | `<Entity>Create`, `<Entity><Field>Update` | `CartCreate`, `SessionDueUpdate` |
| Pydantic response | `<Entity>Response` | `CartResponse`, `ActiveSessionResponse` |
| Common locals | `db` for the DB session, `data` for the request body, `db_<entity>` for a loaded row | `db_cart`, `db_session` |
| `Session` model in routers | imported as `SessionModel` | `from ..models import Session as SessionModel` |
| Status value | `UPPER_SNAKE` string | `AVAILABLE`, `IN_USE` |
| Test | `test_<subject>_<behavior>` | `test_admin_sessions_requires_token` |
| Test helper or fixture | a noun for what it returns | `admin_headers`, `checked_out_session` |

**API**

| Thing | Style | Example |
|---|---|---|
| Path | lowercase plural nouns; admin routes under `/api/admin` | `/api/carts`, `/api/admin/sessions` |
| Path parameter | `{<entity>_id}` | `{cart_id}` |
| Action that isn't create/update/delete | `POST` to a verb sub-path | `/api/carts/{cart_id}/checkout` |
| JSON field, query parameter | `snake_case` | `due_at`, `?status=returned` |
| Query parameter value | lowercase | `active`, `true` |
| Environment variable | `UPPER_SNAKE`; `VITE_` prefix if the frontend reads it | `ADMIN_JWT_SECRET`, `VITE_API_URL` |

**Frontend (JavaScript)**

| Thing | Style | Example |
|---|---|---|
| Component | `PascalCase`, in a file of the same name; admin pages start with `Admin` | `CheckoutForm.jsx`, `AdminSessions.jsx` |
| Non-component module | lowercase noun, `camelCase` if more than one word | `time.js`, `auth.js` |
| Function, variable | `camelCase`, functions start with a verb | `formatTime`, `toInputValue`, `adminFetch` |
| Event handler | `handle<Action>` | `handleSubmit`, `handleQuickExtend` |
| Callback prop | `on<Event>` | `onChange` |
| State | `[thing, setThing]` | `[timezone, setTimezone]` |
| Predicate | `is<Condition>` | `isOverdue` |
| Module constant | `UPPER_SNAKE` | `CLOCK_TICK_MS`, `STATUS_LABELS` |
| CSS class (none yet; styles are inline) | `kebab-case` | `cart-row` |
| `localStorage` key | `snake_case` | `admin_token` |

**Repo**

| Thing | Style | Example |
|---|---|---|
| Branch | `<type>/kebab-case` | `fix/test-db-isolation` |
| Doc file | `kebab-case.md`; `README.md`, `CLAUDE.md`, `OPEN-ISSUES.md` stay upper case | `business-rules.md` |
| Doc identifier | `<PREFIX>-kebab-slug`, open issues numbered | `BR-overdue-definition`, `OI-7` |

## Git workflow

- One branch per issue (`feat/...`, `fix/...`, `docs/...`), then a pull request into `main`. CI runs tests on push to `main`, then deploys to Render.
- Pull request descriptions follow `.github/PULL_REQUEST_TEMPLATE.md`: at most three lines per section, and never restate the diff.
