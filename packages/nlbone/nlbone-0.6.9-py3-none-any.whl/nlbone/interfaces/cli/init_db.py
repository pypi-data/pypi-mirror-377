import typer

from nlbone.adapters.db import Base, init_sync_engine, sync_ping

init_db_command = typer.Typer(help="Database utilities")


@init_db_command.command("init")
def init_db(drop: bool = typer.Option(False, "--drop", help="Drop all tables before create")):
    """Create (and optionally drop) DB schema."""
    engine = init_sync_engine()
    if drop:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    typer.echo("✅ DB schema initialized.")


@init_db_command.command("ping")
def ping():
    """Health check."""
    sync_ping()
    typer.echo("✅ DB connection OK")


@init_db_command.command("migrate")
def migrate():
    """Placeholder for migration trigger (Alembic, etc.)."""
    typer.echo("ℹ️  Hook your migration tool here.")
