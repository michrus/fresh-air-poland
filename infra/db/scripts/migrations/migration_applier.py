"""Module defining MigrationApplier class."""

import logging
import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, exc, inspect, select, text
from sqlalchemy import Column, DateTime, Integer, String, Table, MetaData
from sqlalchemy.orm import Session

from db_connection_params import DBConnectionParameters
from migration import Migration


class MigrationApplier:
    """Orchestrates migration applying."""

    MIGRATION_NAME_PATTERN = r'([0-9]+)_(\w+).sql'

    def __init__(self,
                 db_connection_params: DBConnectionParameters,
                 changelog_table_name: str,
                 migrations_directory_path: str
                 ):
        self.user = db_connection_params.user
        self.db_connection_string = (
            f"{db_connection_params.dialect}+{db_connection_params.driver}://"
            f"{db_connection_params.user}:{db_connection_params.password}@"
            f"{db_connection_params.address}:{db_connection_params.port}/"
            f"{db_connection_params.db_name}"
        )
        self._setup_db_connection()
        self.migration_changelog = self._get_changelog_table(changelog_table_name)
        self.migrations_directory_path = migrations_directory_path

    def apply_remaining_migrations(self):
        """Applies remaining migrations, based on files and 
        records from the database migration changelog table."""

        with Session(self.engine) as session:
            applied_migrations = self._get_migrations_from_changelog(
                session=session,
            )
            all_migrations = self._get_migrations_from_directory()
            migrations_to_apply = list(all_migrations - applied_migrations)
            migrations_to_apply.sort(key=lambda m: m.number)
            if not migrations_to_apply:
                logging.getLogger().info("No migrations left to apply")
            for migration in migrations_to_apply:
                self._apply_migration(
                    migration=migration,
                    session=session,
                )
            try:
                session.commit()
            except exc.SQLAlchemyError as e:
                logging.getLogger().error(
                    "ERROR! Failed to commit changes to the database. Exception message: %s", 
                    e
                )
                raise

    def _setup_db_connection(self):
        logging.getLogger().info("Setting up connection to the database")
        try:
            self.engine = create_engine(self.db_connection_string)
            self.meta = MetaData()
            self.meta.reflect(bind=self.engine)
        except exc.SQLAlchemyError as e:
            logging.getLogger().error(
                "ERROR! Failed to set up database connection: %s", 
                e
            )
            raise
        logging.getLogger().info("Database connection set up")

    def _get_changelog_table(self, changelog_table_name):
        logging.getLogger().info("Inspecting changelog table")
        try:
            inspector = inspect(self.engine)
            table_exists = inspector.has_table(changelog_table_name)
        except exc.SQLAlchemyError as e:
            logging.getLogger().error("ERROR! Failed to inspect changelog table: %s", e)
            raise
        if not table_exists:
            logging.getLogger().info("Changelog table does not exist. Creating.")
            try:
                migration_changelog = Table(
                    changelog_table_name, self.meta,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('completed_at', DateTime, nullable=False),
                    Column('made_by', String, nullable=False),
                    Column('migration_name', String, nullable=False),
                )
                self.meta.create_all(self.engine)
            except exc.SQLAlchemyError as e:
                logging.getLogger().error("ERROR! Failed to create changelog table: %s", e)
                raise
            logging.getLogger().info("Changelog table created")
        else:
            logging.getLogger().info("Changelog table present")
            migration_changelog = self.meta.tables[changelog_table_name]
        return migration_changelog

    def _get_migrations_from_changelog(self, session: Session):
        logging.getLogger().info("Retrieving applied migrations from changelog table")
        try:
            stmt = select(self.migration_changelog.c.migration_name)
            result_rows = session.execute(stmt).all()
        except exc.SQLAlchemyError as e:
            logging.getLogger().error(
                "ERROR! Failed to retrieve migrations from changelog table: %s", 
                e
            )
            raise
        applied_migrations = set()
        for row in result_rows:
            mig = Migration(row[0])
            if mig:
                applied_migrations.add(mig)
            else:
                logging.getLogger().warning(
                    "Migration name: %s "
                    "does not fit expected pattern. Skipping.",
                    mig.full_name
                )
        logging.getLogger().info("Retrieved list of applied migrations")
        return applied_migrations

    def _get_migrations_from_directory(self):
        logging.getLogger().info(
            "Retrieving migrations list from directory: %s",
            self.migrations_directory_path
        )
        try:
            migrations = os.listdir(self.migrations_directory_path)
        except FileNotFoundError as e:
            logging.getLogger().error(
                "ERROR! Failed to retrieve migration files. Exception message: %s",
                e
            )
            raise
        all_migrations = set()
        for m in migrations:
            mig = Migration(m)
            if mig:
                all_migrations.add(mig)
            else:
                logging.getLogger().warning(
                    "Migration name: %s does not fit expected pattern. Skipping.",
                    m
                )
        logging.getLogger().info("Retrieved list of migration files")
        return all_migrations

    def _apply_migration(self, migration: Migration, session: Session):
        logging.getLogger().info("Applying migration %s", str(migration))
        applied_migration_path = Path(self.migrations_directory_path, migration.full_name)
        try:
            with open(applied_migration_path, 'rt', encoding='utf-8') as file:
                migration_sql = file.read()
                session.execute(text(migration_sql))
        except FileNotFoundError as fe:
            logging.getLogger().error(
                "ERROR! Failed to open migration file. Exception message: %s",
                fe
            )
            raise
        except exc.SQLAlchemyError as se:
            logging.getLogger().error(
                "ERROR! Failed to execute migration SQL. Exception message: %s",
                se
            )
            raise
        completed_at = datetime.now()
        try:
            insert_stmt = self.migration_changelog.insert().values(
                completed_at=completed_at,
                made_by=self.user,
                migration_name=migration.full_name,
            )
            session.execute(insert_stmt)
        except exc.SQLAlchemyError as e:
            logging.getLogger().error(
                "ERROR! Failed insert into migration changelog. Exception message: %s",
                e
            )
            raise
        logging.getLogger().info("Migration applied")
