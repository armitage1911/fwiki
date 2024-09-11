import click
import psycopg
from flask import current_app
from .__init__ import DSN


def init_db():
    with current_app.open_resource('schema.sql') as f:
        with psycopg.connect(DSN) as conn:
            with conn.cursor() as cur:
                cur.execute(f.read().decode('utf8'))


def attach_id_to_pid(id, pid):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE pages SET pid = (%s) WHERE id = (%s)', (pid, id)
                )


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Database has been initialized.')


# TODO
# Сделать рефакторинг
@click.command('attach_id_to_pid')
def attach_id_to_pid_cmd():
    """
    Функция позволит назначить id статьи к родительскому pid для формирования
    общего списка.
    """
    id = int(input('Type id here: '))
    pid = int(input('Type pid here: '))
    attach_id_to_pid(id, pid)
    click.echo('Done.')


def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(attach_id_to_pid_cmd)
