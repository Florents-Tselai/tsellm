from sqlite_utils import Database
import llm
from tsellm.cli import cli


def test_tsellm_cli(db_path):
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

    cli([db_path, "UPDATE prompts SET generated=prompt(prompt)"])

    assert db.execute("select prompt, generated from prompts").fetchall() == [
        ("hello", "hellohello"),
        ("world", "worldworld"),
    ]
