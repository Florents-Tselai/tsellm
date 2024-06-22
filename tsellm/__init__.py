def _prompt(p):
    return p * 2


TSELLM_CONFIG_SQL = """
CREATE TABLE IF NOT EXISTS __tsellm (
data
);

"""


def _tsellm_init(con):
    """Entry-point for tsellm initialization."""
    con.execute(TSELLM_CONFIG_SQL)
    con.create_function("prompt", 1, _prompt)
