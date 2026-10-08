# Move-In Day Cart Tracker

A full-stack web app for tracking the moving carts that residents borrow on university move-in day.

Resident assistants (RAs) see which carts are free, check one out to a resident (name, phone, room number, and when it is due back), and mark it returned. An admin page, protected by a shared password, lets staff add, edit, and remove carts, edit or close active checkouts, and set the site's timezone.

- **Frontend:** https://movein-cart-management.vercel.app
- **API:** https://cart-management-967g.onrender.com (interactive docs at [`/docs`](https://cart-management-967g.onrender.com/docs))

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy 2](https://www.sqlalchemy.org/), Pydantic v2 |
| Database | PostgreSQL on [Neon](https://neon.tech/) (SQLite for tests) |
| Auth | Shared admin password exchanged for a JWT (PyJWT) |
| Frontend | React 19, React Router 7, Vite |
| Testing | pytest with FastAPI's `TestClient` |
| CI/CD | GitHub Actions runs the tests on every push to `main`, then triggers a Render deploy |
| Hosting | Render (API), Vercel (frontend) |

All timestamps are stored in UTC and converted to and from the site timezone that the admin sets.

## Setup

You need Python 3.12, Node.js, and a PostgreSQL database (a free Neon project works).

### Backend

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in the repository root:

```
DATABASE_URL=postgresql://user:password@host/dbname
ADMIN_PASSWORD=your-admin-password
ADMIN_JWT_SECRET=a-long-random-secret
```

Then start the API, which creates its tables on first run:

```bash
uvicorn app.main:app --reload
```

It serves on http://localhost:8000, with interactive docs at http://localhost:8000/docs.

### Frontend

Create `frontend/.env`:

```
VITE_API_URL=http://localhost:8000
```

Then:

```bash
cd frontend
npm install
npm run dev
```

The app runs on http://localhost:5173, the origin the API's CORS settings allow for local development.

### Tests

```bash
pytest tests/ -v
```

The tests use their own SQLite database (set in `tests/conftest.py`), so they need no `.env` and no network access.

## Project structure

```
cart-api/
├── app/                        # FastAPI backend
│   ├── main.py                 # App setup, CORS, router registration
│   ├── database.py             # Engine, session factory, get_db dependency
│   ├── models.py               # SQLAlchemy models: Cart, Session (a checkout), Setting
│   ├── schemas.py              # Pydantic request and response models
│   ├── auth.py                 # Admin login and the require_admin JWT check
│   ├── timezones.py            # Site timezone lookup and UTC conversion
│   └── routers/
│       ├── carts.py            # Public: list carts, check out, return
│       ├── admin.py            # Admin-only: manage carts, sessions, and settings
│       └── settings.py         # Public: read site settings
├── frontend/                   # React + Vite single-page app
│   ├── vercel.json             # Rewrites every path to index.html so deep links work
│   └── src/
│       ├── App.jsx             # Routes: /, /checkout/:cartId, /admin/login, /admin
│       ├── auth.js             # Admin token storage (localStorage)
│       ├── sessions.js         # Overdue check for a checkout
│       ├── time.js             # Formatting and input conversion in the site timezone
│       └── components/         # CartList, CheckoutForm, Admin* pages, RequireAdmin guard
├── tests/
│   └── test_carts.py           # API tests against an isolated SQLite database
├── .github/workflows/test.yml  # CI: test, then deploy to Render
└── requirements.txt            # Python dependencies
```
