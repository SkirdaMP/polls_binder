from io import StringIO
import os
from contextlib import contextmanager

from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv


class MultipleDotenvFoundError(Exception):
    """Error is raised when more than one dotenv file is found."""
    pass


@contextmanager
def get_connection():
    connection = pool.getconn()

    try:
        yield connection
    finally:
        pool.putconn(connection)


def _search_dotenv_in_path(dotenv_path):

    dotenv_path_content = os.listdir(dotenv_path)
    dotenv_names = list(
        filter(
            lambda f: (
                    f.lower().endswith(".env") and
                    os.path.isfile(os.path.join(dotenv_path, f))
            ),
            dotenv_path_content
        )
    )

    if len(dotenv_names) == 1:
        return dotenv_names[0]
    elif len(dotenv_names) > 1:
        if os.path.isfile(os.path.join(dotenv_path, '.env')):
            return '.env'
    else:
        return None


DATABASE_PROMPT = "Enter the DATABASE_URI value or leave empty to load from .env file: "

database_uri = input(DATABASE_PROMPT)
if not database_uri:
    env_path = _search_dotenv_in_path('.')
    with open(env_path) as f_env:
        load_dotenv(stream=StringIO(f_env.read()))
    database_uri = os.environ["DATABASE_URI"]

pool = SimpleConnectionPool(minconn=1, maxconn=10, dsn=database_uri)
