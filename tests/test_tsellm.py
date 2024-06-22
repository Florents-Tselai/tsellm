from sqlite_utils import Database

from tsellm.cli import cli
import pytest
import datetime
from click.testing import CliRunner


def test_cli(db_path):
    db = Database(db_path)
    assert [] == db.table_names()
    table = db.create_table(
        "prompts",
        {
            "prompt": str,
            "generated": str,
            "model": str,
            "embedding": dict,
        },
    )

    assert ["prompts"] == db.table_names()

    table.insert({"prompt": "hello"})
    table.insert({"prompt": "world"})

    assert db.execute("select prompt from prompts").fetchall() == [
        ("hello",),
        ("world",),
    ]
