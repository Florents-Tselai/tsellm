from sqlite_utils import Database
from sqlite_utils.utils import sqlite3
import pytest


def pytest_configure(config):
    import sys

    sys._called_from_test = True


@pytest.fixture
def fresh_db():
    return Database(memory=True)


@pytest.fixture
def existing_db(db_path):
    database = Database(db_path)
    database.executescript(
        """
        CREATE TABLE foo (text TEXT);
        INSERT INTO foo (text) values ("one");
        INSERT INTO foo (text) values ("two");
        INSERT INTO foo (text) values ("three");
    """
    )
    return database


@pytest.fixture
def db_path(tmpdir):
    path = str(tmpdir / "test.db")
    db = sqlite3.connect(path)
    return path
