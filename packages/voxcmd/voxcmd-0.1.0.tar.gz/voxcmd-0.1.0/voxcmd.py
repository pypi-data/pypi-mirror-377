import click

@click.group()
def cli():
    """A powerful CLI tool called voxcmd."""
    pass

@cli.command()
@click.argument('name')
@click.option('--times', default=1, help='Number of times to greet.')
def hello(name, times):
    """Greets a person."""
    for _ in range(times):
        click.echo(f"Hello, {name}!")

@cli.command()
def goodbye():
    """Says goodbye."""
    click.echo("Goodbye!")

if __name__ == '__main__':
    cli()