import click
from flask.cli import with_appcontext
from app import db
from app.models import Critter, Configure

@click.command('add-critter')
@click.argument('name')
@click.option('--pest', is_flag=True, help='Specify if the critter is a pest.')
@with_appcontext
def add_critter(name, pest):
    """Add a new critter to the database."""
    critter = Critter(name=name, is_pest=pest)
    db.session.add(critter)
    db.session.commit()
    click.echo(f"Added critter {name} (Pest: {pest})")

@click.command('add-device')
@click.argument('name')
@click.option('--threshold', default=60, help='Alert threshold in seconds.')
@with_appcontext
def add_device(name, threshold):
    """Add a new device to the database with default config values."""
    critters = ['grasshopper', 'snail', 'rabbits', 'ladybug', 'butterfly', 'bee']
    for critter in critters:
        # Check if critter exists before adding a new configuration
        existing_critter = Critter.query.filter_by(name=critter).first()
        if not existing_critter:
            click.echo(f"Critter '{critter}' does not exist. Please add the critter first.")
            continue
        
        # Add or update the configuration for the critter
        config = Configure.query.filter_by(critter_name=critter).first()
        if config:
            config.cooldown_time = threshold
        else:
            config = Configure(critter_name=critter, cooldown_time=threshold)
            db.session.add(config)
    
    db.session.commit()
    click.echo(f"Added device {name} with default threshold {threshold} seconds for critters")

def register_commands(app):
    app.cli.add_command(add_critter)
    app.cli.add_command(add_device)

