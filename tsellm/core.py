import llm
import json

TSELLM_CONFIG_SQL = """
-- tsellm configuration table
-- need to be taken care of accross migrations and versions.

CREATE TABLE IF NOT EXISTS __tsellm (
x text
);

"""


def _prompt_model(prompt, model):
    return llm.get_model(model).prompt(prompt).text()


def _embed_model(text, model):
    return json.dumps(llm.get_embedding_model(model).embed(text))


def _tsellm_init(con):
    """Entry-point for tsellm initialization."""
    con.execute(TSELLM_CONFIG_SQL)
    con.create_function("prompt", 2, _prompt_model)
    con.create_function("embed", 2, _embed_model)
