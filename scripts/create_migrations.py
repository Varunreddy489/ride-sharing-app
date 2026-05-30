import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

super_user = os.getenv("SUPERUSER", "postgres")
super_password = os.getenv("SUPERUSER_PASSWORD", "postgresdb")
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME","ride_sharing_db")

load_dotenv()

print("SUPERUSER:", super_user)
print("DB_USER:", os.getenv("DB_USER"))
print("DB_NAME:", db_name)
print("DB_HOST:", os.getenv("DB_HOST"))

print(f"Creating database and user: {db_user} @ {host}:{port}/{db_name}")

try:
    with psycopg.connect(f"postgresql://{super_user}:{super_password}@{host}:{port}/postgres", autocommit=True) as conn:
        conn.execute(f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{db_user}') THEN
                CREATE ROLE {db_user} LOGIN PASSWORD '{db_password}';
            END IF;
        END
        $$;
    """)
        exists = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)).fetchone()
        if not exists:
            conn.execute(f"CREATE DATABASE {db_name} OWNER {db_user}")
            print(f"Database '{db_name}' created successfully")
        else:
            print(f"Database '{db_name}' already exists")
except Exception as e:
    print(f"Error creating database: {e}")
    sys.exit(1)

# Configure alembic.ini with the correct database URL
db_url = f"postgresql+psycopg://{db_user}:{db_password}@{host}:{port}/{db_name}"
alembic_ini_path = Path(__file__).parent.parent / "alembic.ini"
if alembic_ini_path.exists():
    with open(alembic_ini_path, "r") as f:
        content = f.read()
    
    # Replace the placeholder with the actual URL
    content = content.replace(
        "sqlalchemy.url = driver://user:pass@localhost/dbname",
        f"sqlalchemy.url = {db_url}"
    )
    
    with open(alembic_ini_path, "w") as f:
        f.write(content)
    
    print(f"Updated alembic.ini with database URL")
else:
    print(f"Warning: alembic.ini not found at {alembic_ini_path}")
