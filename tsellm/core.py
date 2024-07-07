import json

import llm
from llm import cli as llm_cli

TSELLM_CONFIG_SQL = """
-- tsellm configuration table
-- need to be taken care of accross migrations and versions.

CREATE TABLE IF NOT EXISTS __tsellm (
x text
);

"""


def _prompt_model(prompt: str, model: str) -> str:
    return llm.get_model(model).prompt(prompt).text()


def _prompt_model_default(prompt: str) -> str:
    return llm.get_model("markov").prompt(prompt).text()


def _embed_model(text: str, model: str) -> str:
    return json.dumps(llm.get_embedding_model(model).embed(text))


def _embed_model_default(text: str) -> str:
    return json.dumps(
        llm.get_embedding_model(llm_cli.get_default_embedding_model()).embed(text)
    )


def _tsellm_init(con):
    """Entry-point for tsellm initialization."""
    con.execute(TSELLM_CONFIG_SQL)
    con.create_function("prompt", 2, _prompt_model)
    con.create_function("prompt", 1, _prompt_model_default)
    con.create_function("embed", 2, _embed_model)
    con.create_function("embed", 1, _embed_model_default)
