import click
from flask.cli import with_appcontext
from app import app, db_session, Base, engine

@app.cli.command("clear-db")
@click.confirmation_option(prompt="Are you sure you want to delete all data?")
@with_appcontext
def clear_db():
    """Drops and recreates all database tables."""
    db_session.remove()  # Close the current scoped session
    
    # Use the metadata object to drop and create
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database cleared and tables recreated.")