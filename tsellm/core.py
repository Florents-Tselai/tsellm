import llm

TSELLM_CONFIG_SQL = """
CREATE TABLE IF NOT EXISTS __tsellm (
x text
);

"""


def _prompt_model(prompt, model):
    return llm.get_model(model).prompt(prompt).text()


def _tsellm_init(con):
    """Entry-point for tsellm initialization."""
    con.execute(TSELLM_CONFIG_SQL)
    con.create_function("prompt", 2, _prompt_model)
