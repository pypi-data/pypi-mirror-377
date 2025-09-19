from typing import Optional

import typer

from nlbone.adapters.db import init_sync_engine
from nlbone.config.settings import get_settings
from nlbone.interfaces.cli.init_db import init_db_command

app = typer.Typer(help="NLBone CLI")

app.add_typer(init_db_command, name="db")


@app.callback()
def common(
    env_file: Optional[str] = typer.Option(None, "--env-file", "-e", help="Path to .env file. In prod omit this."),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    settings = get_settings(env_file=env_file)
    if debug:
        pass
    init_sync_engine(echo=settings.DEBUG)


def main():
    app()


if __name__ == "__main__":
    main()
