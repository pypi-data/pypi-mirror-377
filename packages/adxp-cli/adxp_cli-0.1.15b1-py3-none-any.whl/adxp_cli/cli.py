import click
from adxp_cli.agent.cli import agent
from adxp_cli.auth.cli import auth
from adxp_cli.model.cli import model
from adxp_cli.finetuning.cli import finetuning


@click.group()
def cli():
    """Command-line interface for AIP server management."""
    pass


cli.add_command(auth)
cli.add_command(agent)
cli.add_command(model)
cli.add_command(finetuning)


if __name__ == "__main__":
    cli()
