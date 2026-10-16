import os

# pytest loads this file before the test modules, so this runs before app.database
# reads DATABASE_URL. load_dotenv() doesn't override variables that are already set,
# so a local .env can't point the tests at Neon either.
# CI sets TEST_DATABASE_URL to a throwaway Postgres; everywhere else it's SQLite.
test_database_url = os.environ.get("TEST_DATABASE_URL", "sqlite:///./test.db")

# The tests drop every table after each test, so a Neon URL here would wipe real data
if "neon.tech" in test_database_url:
    raise RuntimeError("TEST_DATABASE_URL points at Neon -- tests need a throwaway database")

os.environ["DATABASE_URL"] = test_database_url
