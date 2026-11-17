DATABASE_URL = os.environ.get("DATABASE_URL", "").strip() or None  # PostgreSQL when set, SQLite otherwise
