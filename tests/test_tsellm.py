import llm.cli
from sqlite_utils import Database
from tsellm.cli import cli
import unittest
from test.support import captured_stdout, captured_stderr, captured_stdin, os_helper
from test.support.os_helper import TESTFN, unlink
from llm import models
import sqlite3
from llm import cli as llm_cli


class CommandLineInterface(unittest.TestCase):

    def _do_test(self, *args, expect_success=True):
        with (
            captured_stdout() as out,
            captured_stderr() as err,
            self.assertRaises(SystemExit) as cm,
        ):
            cli(args)
        return out.getvalue(), err.getvalue(), cm.exception.code

    def expect_success(self, *args):
        out, err, code = self._do_test(*args)
        self.assertEqual(code, 0, "\n".join([f"Unexpected failure: {args=}", out, err]))

        # This makes DeprecationWarning and other warnings cause a failure.
        # Let's not be that harsh yet.
        # See https://github.com/Florents-Tselai/llm/tree/fix-utc-warning-312
        # self.assertEqual(err, "")
        return out

    def expect_failure(self, *args):
        out, err, code = self._do_test(*args, expect_success=False)
        self.assertNotEqual(
            code, 0, "\n".join([f"Unexpected failure: {args=}", out, err])
        )
        self.assertEqual(out, "")
        return err

    def test_cli_help(self):
        out = self.expect_success("-h")
        self.assertIn("usage: python -m tsellm", out)

    def test_cli_version(self):
        out = self.expect_success("-v")
        self.assertIn(sqlite3.sqlite_version, out)

    def test_cli_execute_sql(self):
        out = self.expect_success(":memory:", "select 1")
        self.assertIn("(1,)", out)

    def test_cli_execute_too_much_sql(self):
        stderr = self.expect_failure(":memory:", "select 1; select 2")
        err = "ProgrammingError: You can only execute one statement at a time"
        self.assertIn(err, stderr)

    def test_cli_execute_incomplete_sql(self):
        stderr = self.expect_failure(":memory:", "sel")
        self.assertIn("OperationalError (SQLITE_ERROR)", stderr)

    def test_cli_on_disk_db(self):
        self.addCleanup(unlink, TESTFN)
        out = self.expect_success(TESTFN, "create table t(t)")
        self.assertEqual(out, "")
        out = self.expect_success(TESTFN, "select count(t) from t")
        self.assertIn("(0,)", out)


class SQLiteLLMFunction(CommandLineInterface):

    def setUp(self):
        super().setUp()
        llm_cli.set_default_model("markov")
        llm_cli.set_default_embedding_model("hazo")

    def assertMarkovResult(self, prompt, generated):
        # Every word should be one of the original prompt (see https://github.com/simonw/llm-markov/blob/657ca504bcf9f0bfc1c6ee5fe838cde9a8976381/tests/test_llm_markov.py#L20)
        for w in prompt.split(" "):
            self.assertIn(w, generated)

    def test_prompt_markov(self):
        out = self.expect_success(":memory:", "select prompt('hello world', 'markov')")
        self.assertMarkovResult("hello world", out)

    def test_prompt_default_markov(self):
        self.assertEqual(llm_cli.get_default_model(), "markov")
        out = self.expect_success(":memory:", "select prompt('hello world')")
        self.assertMarkovResult("hello world", out)

    def test_embed_hazo(self):
        out = self.expect_success(":memory:", "select embed('hello world', 'hazo')")
        self.assertEqual(
            "('[5.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]',)\n",
            out,
        )

    def test_embed_default_hazo(self):
        self.assertEqual(llm_cli.get_default_embedding_model(), "hazo")
        out = self.expect_success(":memory:", "select embed('hello world')")
        self.assertEqual(
            "('[5.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]',)\n",
            out,
        )


if __name__ == "__main__":
    unittest.main()
