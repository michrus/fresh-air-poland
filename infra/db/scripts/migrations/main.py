"""Script for handling database migrations."""

import argparse
import logging
import os
import sys
from pathlib import Path

from db_connection_params import DBConnectionParameters
from migration_applier import MigrationApplier


LOG_FORMATTER = \
    logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

CONSOLE_HANDLER = logging.StreamHandler(sys.stdout)
CONSOLE_HANDLER.setFormatter(LOG_FORMATTER)
rootLogger.addHandler(CONSOLE_HANDLER)


def setup_argparser():
    """Sets up script arguments."""

    # Create parser
    parser = argparse.ArgumentParser(
        description="Script for database migration management."
    )
    # Add arguments
    parser.add_argument("-dl", "--dialect", help="Database dialect", default="postgresql")
    parser.add_argument("-dv", "--driver", help="Database driver", default="psycopg2")
    parser.add_argument("-u", "--user", help="Database connection user name", required=True)
    parser.add_argument(
        "--pw-envar", 
        dest="pwenvar",
        help="Environment variable name storing database connection password",
        default="DB_CONN_PASSWORD"
    )
    parser.add_argument("-a", "--address", help="Database address", default="localhost")
    parser.add_argument("-p", "--port", type=int, help="Database port", default=5432)
    parser.add_argument("-n", "--name", help="Database name", required=True)
    parser.add_argument(
        "-m",
        "--migrations-path",
        dest="migrations_path",
        help="Path to directory with migration files",
        default=Path(Path(os.path.realpath(__file__)).parent.parent.parent, 'migrations'),
    )
    parser.add_argument(
        "--changelog-table-name",
        dest="changelog_table_name",
        help="Changelog table name",
        default="migrations_changelog",
    )
    return parser


def main():
    """Main function."""

    parser = setup_argparser()
    args = parser.parse_args()
    try:
        password = os.environ[args.pwenvar]
    except KeyError:
        rootLogger.error(
            "ERROR! Environment variable '%s' does not exist!",
            args.pwenvar
        )
        return 1
    db_connection_params = DBConnectionParameters(
        dialect=args.dialect,
        driver=args.driver,
        user=args.user,
        password=password,
        address=args.address,
        port=args.port,
        db_name=args.name,
    )
    migration_applier = MigrationApplier(
        db_connection_params=db_connection_params,
        changelog_table_name=args.changelog_table_name,
        migrations_directory_path=args.migrations_path,
    )
    migration_applier.apply_remaining_migrations()
    return 0


if __name__ == '__main__':
    sys.exit(main())
