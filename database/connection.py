import os

from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# Query-string params that Prisma understands but libpq/psycopg2 rejects.
# Supabase's "ORM" connection string ships with `?pgbouncer=true`, which
# psycopg2 refuses. We strip these so the SAME URL works for both Prisma
# and the Python (SQLAlchemy/psycopg2) layer.
_PRISMA_ONLY_PARAMS = {
    "pgbouncer",
    "connection_limit",
    "pool_timeout",
    "schema",
    "sslaccept",
    "socket_timeout",
}


def _sanitize_url(url):
    parts = urlsplit(url)

    if not parts.query:
        return url

    kept = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k not in _PRISMA_ONLY_PARAMS
    ]

    return urlunsplit(parts._replace(query=urlencode(kept)))


# ============================================================
# ENV
# ============================================================
#
# Central SQLAlchemy engine factory for the whole project.
#
# The database now lives on Supabase (PostgreSQL). All modules
# import the engine from here instead of building their own
# MySQL connection string, so the connection settings (pooling,
# SSL, credentials) live in exactly one place.
#
# DATABASE_URL points at the Supabase *Session Pooler* (port 5432),
# which is IPv4, keeps prepared statements (required by pandas
# `to_sql` / `read_sql`) and is the right choice for a long-lived
# Python server. See .env.example for the exact format.
# ============================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Add your Supabase PostgreSQL "
        "connection string to the .env file (see .env.example)."
    )


_engine = None


def get_engine():
    """Return a process-wide singleton SQLAlchemy engine.

    Connection pooling is configured for a persistent server /
    batch workload talking to Supabase:
      - pool_pre_ping  : drop dead connections (pooler may recycle)
      - pool_recycle   : refresh connections before the pooler times out
      - pool_size /    : keep the footprint modest so we stay within
        max_overflow     Supabase's connection limits
    """

    global _engine

    if _engine is None:

        _engine = create_engine(
            _sanitize_url(DATABASE_URL),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=1800,
            # Supabase's pooler doesn't report client_encoding back to
            # psycopg2 ("server didn't return client encoding"). Set it
            # explicitly so psycopg2 doesn't depend on the server echo.
            connect_args={"client_encoding": "utf8"},
        )

    return _engine


def ensure_unique_transaction_id(table):
    """Enforce a UNIQUE index on a pandas-created table's "TransactionID".

    Idempotent (CREATE UNIQUE INDEX IF NOT EXISTS). Best-effort: if the table
    already holds duplicate TransactionIDs the index can't be created, so we
    log and continue rather than breaking the request — run the one-time
    de-dup SQL (see docs/database_design.md) to clean existing rows.
    """
    index_name = f"{table}_txid_unique"
    try:
        with get_engine().begin() as conn:
            conn.execute(text(
                f'CREATE UNIQUE INDEX IF NOT EXISTS "{index_name}" '
                f'ON "{table}" ("TransactionID")'
            ))
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[connection] unique index on {table} not applied: {exc}")
