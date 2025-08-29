import os
from alembic.config import Config
from alembic import command

def run_migrations():
    # Get the absolute path to the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to alembic.ini
    alembic_ini_path = os.path.join(script_dir, 'alembic.ini')

    # Create an Alembic configuration object
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("script_location", os.path.join(script_dir, "migrations/alembic"))


    # Run the 'upgrade head' command
    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    run_migrations()
