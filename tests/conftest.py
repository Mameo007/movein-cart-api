import os

# pytest loads this file before the test modules, so this runs before app.database
# reads DATABASE_URL. load_dotenv() doesn't override variables that are already set,
# so a local .env can't point the tests at Neon either.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
