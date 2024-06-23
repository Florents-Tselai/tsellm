from sqlite_utils import Database
from tsellm.cli import cli


def test_cli_prompt_mock(existing_db_path):
    db = Database(existing_db_path)

    assert db.execute("select prompt from prompts").fetchall() == [
        ("hello world!",),
        ("how are you?",),
        ("is this real life?",),
    ]

    cli([existing_db_path, "UPDATE prompts SET generated=prompt(prompt, 'markov')"])

    for prompt, generated in db.execute("select prompt, generated from prompts").fetchall():
        words = generated.strip().split()
        # Every word should be one of the original prompt (see https://github.com/simonw/llm-markov/blob/657ca504bcf9f0bfc1c6ee5fe838cde9a8976381/tests/test_llm_markov.py#L20)
        prompt_words = prompt.split()
        for word in words:
            assert word in prompt_words
