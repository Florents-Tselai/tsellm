from sqlite_utils import Database
import pytest

import pytest
import json
import llm
from llm.plugins import pm
from typing import Optional
import sqlite_utils
from pydantic import Field


def pytest_configure(config):
    import sys

    sys._called_from_test = True


@pytest.fixture
def db_path(tmpdir):
    path = str(tmpdir / "test.db")
    return path


@pytest.fixture
def fresh_db_path(db_path):
    return db_path


@pytest.fixture
def existing_db_path(fresh_db_path):
    db = Database(fresh_db_path)
    table = db.create_table(
        "prompts", {"prompt": str, "generated_markov": str, "embedding": str}
    )

    table.insert({"prompt": "hello world!"})
    table.insert({"prompt": "how are you?"})
    table.insert({"prompt": "is this real life?"})
    table.insert({"prompt": "1+1=?"})

    return fresh_db_path
