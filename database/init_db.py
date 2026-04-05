"""
Database initialization script for Smart City Platform.
Creates all tables, views, and indexes from schema.sql.
"""
import sys
import os
from pathlib import Path

# Allow running as standalone script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import DATABASE_URL


def get_schema_path() -> Path:
    return Path(__file__).parent / "schema.sql"


def main():
    """Initialize the database schema."""
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    except ImportError:
        print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
        sys.exit(1)

    schema_path = get_schema_path()
    if not schema_path.exists():
        print(f"ERROR: Schema file not found: {schema_path}")
        sys.exit(1)

    schema_sql = schema_path.read_text(encoding="utf-8")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        print("Connected to PostgreSQL.")
        print("Executing schema...")
        cur.execute(schema_sql)
        print("✓ Tables created.")

        # Verify tables
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"✓ Tables in database: {', '.join(tables)}")

        cur.close()
        conn.close()
        print("✓ Database initialization complete!")

    except Exception as e:
        print(f"ERROR initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
