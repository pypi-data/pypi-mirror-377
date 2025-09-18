import importlib.resources as pkg_resources

import click
from alembic import command
from alembic.migration import MigrationContext
from flask import Flask
from sqlalchemy.sql import text

from .. import sql
from ..models import db


def register_commands(app: Flask):
    db_cli_group = app.cli.commands["db"]

    @db_cli_group.command()
    @click.option(
        "-d",
        "--directory",
        default=None,
        help=('Migration script directory (default is "migrations")'),
    )
    @click.option(
        "--tag",
        default=None,
        help=(
            'Arbitrary "tag" name - can be used by custom env.py ' "scripts"
        ),
    )
    @click.option(
        "-f",
        "--force",
        default=False,
        is_flag=True,
        help="Force database initialization (even if already initialized)",
    )
    @click.option(
        "-x",
        "--x-arg",
        multiple=True,
        help="Additional arguments consumed by custom env.py scripts",
    )
    def create(directory, tag, force, x_arg):
        """Creates all the SQLAlchemy tables and add SQL functions."""

        schema = app.config.get("DB_SCHEMA", "public")
        config = app.extensions["migrate"].migrate.get_config(
            directory, x_arg=x_arg
        )

        engine = db.get_engine()
        with engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            conn.execute(text("COMMIT"))  # commit immediately
            migration_ctx = MigrationContext.configure(conn)
            current = migration_ctx.get_current_revision()

        if current is None or force:
            db.create_all()
            with (
                pkg_resources.files(sql)
                .joinpath("dissolve_adjacent.sql")
                .open("r") as f
            ):
                db.session.execute(text(f.read()))
            with (
                pkg_resources.files(sql)
                .joinpath("tile_bbox.sql")
                .open("r") as f
            ):
                db.session.execute(text(f.read()))
            with (
                pkg_resources.files(sql)
                .joinpath("trigger_feature_make_valid.sql")
                .open("r") as f
            ):
                db.session.execute(text(f.read()))
            db.session.commit()
            command.stamp(config, revision="head", tag=tag)
        else:
            print(
                "Database already exists. You may force its creation "
                "with '--force' option (may break database).\n"
                "If wanting to upgrade it, use 'flask db upgrade' command "
                "instead."
            )

    @db_cli_group.command()
    @click.option(
        "-d",
        "--directory",
        default=None,
        help=('Migration script directory (default is "migrations")'),
    )
    @click.option(
        "-x",
        "--x-arg",
        multiple=True,
        help="Additional arguments consumed by custom env.py scripts",
    )
    def drop(directory, x_arg):
        """Drops all the SQLAlchemy tables."""

        config = app.extensions["migrate"].migrate.get_config(
            directory, x_arg=x_arg
        )

        if input("Your data will be lost. Continue? (Y/y): ")[0] in ["Y", "y"]:
            db.drop_all()
            command.stamp(config, revision=None)

    @db_cli_group.command("migrate-schema")
    @click.argument("new_schema")
    def migrate_schema(new_schema: str):
        """
        Move ORM tables (and alembic_version) to NEW_SCHEMA.

        Example:
            flask migrate-schema public deseasion
        """

        # Normalize: treat "public" as default schema
        def normalize_schema(schema: str | None) -> str:
            return schema if schema is not None else "public"

        engine = db.get_engine()
        with engine.begin() as conn:
            # 1. Ensure new schema exists (unless it's "public")
            if new_schema != "public":
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {new_schema}"))
            old_schema = normalize_schema(db.metadata.schema)

            if old_schema == new_schema:
                click.echo(
                    f"No migration necessary: schema is already {new_schema}"
                )
                return

            # 2. Move ORM tables
            for table_name in db.metadata.tables:
                fq_table = (
                    f"{old_schema}.{table_name}"
                    if old_schema != "public"
                    else table_name
                )
                fq_table_quoted = (
                    f'"{old_schema}"."{table_name}"'
                    if old_schema != "public"
                    else f'"{table_name}"'
                )
                click.echo(f"Moving {fq_table} → {new_schema}.{table_name}")
                conn.execute(
                    text(
                        f"ALTER TABLE {fq_table_quoted} "
                        f"SET SCHEMA {new_schema}"
                    )
                )

            # 3. Move alembic_version table
            version_table_old = (
                f"{db.metadata.schema}.alembic_version"
                if db.metadata.schema is not None
                and db.metadata.schema != "public"
                else "alembic_version"
            )
            res = conn.execute(
                text("SELECT to_regclass(:tbl)"),
                {"tbl": version_table_old},
            ).scalar()

            if res:
                click.echo(
                    f"Moving alembic_version → {new_schema}.alembic_version"
                )
                conn.execute(
                    text(
                        f"ALTER TABLE {version_table_old} "
                        f"SET SCHEMA {new_schema}"
                    )
                )

            click.echo("✅ Schema migration completed.")
            click.echo(
                "⚠️ Make sure to add the instance config.py file "
                f'following line: DB_SCHEMA = "{new_schema}"'
            )
