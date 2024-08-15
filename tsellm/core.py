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


def json_recurse_apply(json_obj, f):
    if isinstance(json_obj, dict):
        # Recursively apply the function to dictionary values
        return {k: json_recurse_apply(v, f) for k, v in json_obj.items()}
    elif isinstance(json_obj, list):
        # Recursively apply the function to list elements
        return [json_recurse_apply(item, f) for item in json_obj]
    elif isinstance(json_obj, str):
        # Apply the function to string values, which returns a list of floats
        return f(json_obj)
    else:
        # Return the object as is if it's neither a dictionary, list, or string
        return json_obj


def _prompt_model(prompt: str, model: str) -> str:
    return llm.get_model(model).prompt(prompt).text()


def _prompt_model_default(prompt: str) -> str:
    return llm.get_model("markov").prompt(prompt).text()


def _embed_model(text: str, model: str) -> str:
    return json.dumps(llm.get_embedding_model(model).embed(text))


def _json_embed_model(js: str, model: str) -> str:
    return json.dumps(
        json_recurse_apply(json.loads(js), lambda v: json.loads(_embed_model(v, model)))
    )


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
