import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg import sql

# Load environment variables from .env
load_dotenv()

super_user = os.getenv("SUPERUSER", "postgres")
super_password = os.getenv("SUPERUSER_PASSWORD", "postgresdb")
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME", "ride_sharing_db")

load_dotenv()

print("SUPERUSER:", super_user)
print("DB_USER:", os.getenv("DB_USER"))
print("DB_NAME:", db_name)
print("DB_HOST:", os.getenv("DB_HOST"))

print(f"Creating database and user: {db_user} @ {host}:{port}/{db_name}")

if not db_user or not db_password:
    print("Error creating database: DB_USER and DB_PASSWORD must be set")
    sys.exit(1)

try:
    with psycopg.connect(
        f"postgresql://{super_user}:{super_password}@{host}:{port}/postgres",
        autocommit=True,
    ) as conn:
        role_exists = conn.execute(
            "SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = %s",
            (db_user,),
        ).fetchone()
        if not role_exists:
            conn.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                    sql.Identifier(db_user),
                    sql.Literal(db_password),
                )
            )
            print(f"Role '{db_user}' created successfully")
        else:
            print(f"Role '{db_user}' already exists")

        exists = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
        ).fetchone()
        if not exists:
            conn.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(db_name),
                    sql.Identifier(db_user),
                )
            )
            print(f"Database '{db_name}' created successfully")
        else:
            print(f"Database '{db_name}' already exists")

        conn.execute(
            sql.SQL("ALTER DATABASE {} OWNER TO {}").format(
                sql.Identifier(db_name),
                sql.Identifier(db_user),
            )
        )

    with psycopg.connect(
        f"postgresql://{super_user}:{super_password}@{host}:{port}/{db_name}",
        autocommit=True,
    ) as conn:
        conn.execute(
            sql.SQL("ALTER SCHEMA public OWNER TO {}").format(sql.Identifier(db_user))
        )
        conn.execute(
            sql.SQL("GRANT USAGE, CREATE ON SCHEMA public TO {}").format(
                sql.Identifier(db_user)
            )
        )
        print(f"Granted schema permissions on '{db_name}.public' to '{db_user}'")
except Exception as e:
    print(f"Error creating database: {e}")
    sys.exit(1)

# Configure alembic.ini with the correct database URL
db_url = f"postgresql+psycopg://{db_user}:{db_password}@{host}:{port}/{db_name}"
alembic_ini_path = Path(__file__).parent.parent / "alembic.ini"
if alembic_ini_path.exists():
    with open(alembic_ini_path) as f:
        content = f.read()

    # Replace the placeholder with the actual URL
    content = content.replace(
        "sqlalchemy.url = driver://user:pass@localhost/dbname",
        f"sqlalchemy.url = {db_url}",
    )

    with open(alembic_ini_path, "w") as f:
        f.write(content)

    print("Updated alembic.ini with database URL")
else:
    print(f"Warning: alembic.ini not found at {alembic_ini_path}")
