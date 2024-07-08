import sqlite3
import tempfile
import unittest
from pathlib import Path
from test.support import captured_stdout, captured_stderr, captured_stdin
from test.support.os_helper import TESTFN, unlink

import duckdb
import llm.cli
from llm import cli as llm_cli

from tsellm.__version__ import __version__
from tsellm.cli import cli, TsellmConsole, SQLiteConsole, DuckDBConsole, DBSniffer


def new_tempfile():
    return Path(tempfile.mkdtemp()) / "test"


def new_sqlite_file():
    f = new_tempfile()
    with sqlite3.connect(f) as db:
        db.execute("CREATE TABLE my(x text)")
    return f


def new_duckdb_file():
    f = new_tempfile()
    con = duckdb.connect(f.__str__())
    con.sql("CREATE TABLE my(x text)")
    return f


class TestDBSniffer(unittest.TestCase):
    def setUp(self):
        self.sqlite_fp = new_sqlite_file()
        self.duckdb_fp = new_duckdb_file()

    def test_sniff_sqlite(self):
        sqlite_sni = DBSniffer(self.sqlite_fp)
        self.assertTrue(sqlite_sni.is_sqlite)
        self.assertFalse(sqlite_sni.is_duckdb)

    def test_snif_duckdb(self):
        duckdb_sni = DBSniffer(self.duckdb_fp)
        self.assertFalse(duckdb_sni.is_sqlite)
        self.assertTrue(duckdb_sni.is_duckdb)


class TsellmConsoleTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        llm_cli.set_default_model("markov")
        llm_cli.set_default_embedding_model("hazo")

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

    def test_console_factory_sqlite(self):
        s = new_sqlite_file()
        obj = TsellmConsole.create_console(s)
        self.assertIsInstance(obj, SQLiteConsole)

        d = new_duckdb_file()
        self.assertTrue(TsellmConsole.create_console(d))
        obj = TsellmConsole.create_console(d)
        self.assertIsInstance(obj, DuckDBConsole)

    def test_cli_help(self):
        out = self.expect_success("-h")
        self.assertIn("usage: python -m tsellm", out)

    def test_cli_version(self):
        out = self.expect_success("-v")
        self.assertIn(__version__, out)

    def test_choose_db(self):
        self.expect_failure("--sqlite", "--duckdb")

    MEMORY_DB_MSG = "Connected to :memory:"
    PS1 = "tsellm> "
    PS2 = "... "

    def run_cli(self, *args, commands=()):
        with (
            captured_stdin() as stdin,
            captured_stdout() as stdout,
            captured_stderr() as stderr,
            self.assertRaises(SystemExit) as cm,
        ):
            for cmd in commands:
                stdin.write(cmd + "\n")
            stdin.seek(0)
            cli(args)

        out = stdout.getvalue()
        err = stderr.getvalue()
        self.assertEqual(
            cm.exception.code, 0, f"Unexpected failure: {args=}\n{out}\n{err}"
        )
        return out, err

    def test_interact(self):
        out, err = self.run_cli()
        self.assertIn(self.MEMORY_DB_MSG, err)
        self.assertIn(self.MEMORY_DB_MSG, err)
        self.assertTrue(out.endswith(self.PS1))
        self.assertEqual(out.count(self.PS1), 1)
        self.assertEqual(out.count(self.PS2), 0)

    def test_interact_quit(self):
        out, err = self.run_cli(commands=(".quit",))
        self.assertIn(self.MEMORY_DB_MSG, err)
        self.assertTrue(out.endswith(self.PS1))
        self.assertEqual(out.count(self.PS1), 1)
        self.assertEqual(out.count(self.PS2), 0)

    def test_interact_version(self):
        out, err = self.run_cli(commands=(".version",))
        self.assertIn(self.MEMORY_DB_MSG, err)
        self.assertIn(sqlite3.sqlite_version + "\n", out)
        self.assertTrue(out.endswith(self.PS1))
        self.assertEqual(out.count(self.PS1), 2)
        self.assertEqual(out.count(self.PS2), 0)
        self.assertIn(sqlite3.sqlite_version, out)

    def test_interact_valid_sql(self):
        out, err = self.run_cli(commands=("SELECT 1;",))
        self.assertIn(self.MEMORY_DB_MSG, err)
        self.assertIn("(1,)\n", out)
        self.assertTrue(out.endswith(self.PS1))
        self.assertEqual(out.count(self.PS1), 2)
        self.assertEqual(out.count(self.PS2), 0)

    def test_interact_incomplete_multiline_sql(self):
        out, err = self.run_cli(commands=("SELECT 1",))
        self.assertIn(self.MEMORY_DB_MSG, err)
        self.assertTrue(out.endswith(self.PS2))
        self.assertEqual(out.count(self.PS1), 1)
        self.assertEqual(out.count(self.PS2), 1)

    def test_interact_valid_multiline_sql(self):
        out, err = self.run_cli(commands=("SELECT 1\n;",))
        self.assertIn(self.MEMORY_DB_MSG, err)
        self.assertIn(self.PS2, out)
        self.assertIn("(1,)\n", out)
        self.assertTrue(out.endswith(self.PS1))
        self.assertEqual(out.count(self.PS1), 2)
        self.assertEqual(out.count(self.PS2), 1)


class InMemorySQLiteTest(TsellmConsoleTest):
    path_args = None

    def setUp(self):
        super().setUp()
        self.path_args = (
            "--sqlite",
            ":memory:",
        )

    def test_cli_execute_sql(self):
        out = self.expect_success(*self.path_args, "select 1")
        self.assertIn("(1,)", out)

    def test_cli_execute_too_much_sql(self):
        stderr = self.expect_failure(*self.path_args, "select 1; select 2")
        err = "ProgrammingError: You can only execute one statement at a time"
        self.assertIn(err, stderr)

    def test_cli_execute_incomplete_sql(self):
        stderr = self.expect_failure(*self.path_args, "sel")
        self.assertIn("OperationalError (SQLITE_ERROR)", stderr)

    def assertMarkovResult(self, prompt, generated):
        # Every word should be one of the original prompt (see https://github.com/simonw/llm-markov/blob/657ca504bcf9f0bfc1c6ee5fe838cde9a8976381/tests/test_llm_markov.py#L20)
        for w in prompt.split(" "):
            self.assertIn(w, generated)

    def test_prompt_markov(self):
        out = self.expect_success(
            *self.path_args, "select prompt('hello world', 'markov')"
        )
        self.assertMarkovResult("hello world", out)

    def test_prompt_default_markov(self):
        self.assertEqual(llm_cli.get_default_model(), "markov")
        out = self.expect_success(*self.path_args, "select prompt('hello world')")
        self.assertMarkovResult("hello world", out)

    def test_embed_hazo(self):
        out = self.expect_success(
            *self.path_args, "select embed('hello world', 'hazo')"
        )
        self.assertEqual(
            "('[5.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]',)\n",
            out,
        )

    def test_embed_hazo_binary(self):
        self.assertTrue(llm.get_embedding_model("hazo").supports_binary)
        self.expect_success(*self.path_args, "select embed(randomblob(16), 'hazo')")

    def test_embed_default_hazo(self):
        self.assertEqual(llm_cli.get_default_embedding_model(), "hazo")
        out = self.expect_success(*self.path_args, "select embed('hello world')")
        self.assertEqual(
            "('[5.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]',)\n",
            out,
        )


class DefaultInMemorySQLiteTest(InMemorySQLiteTest):
    """--sqlite is omitted and should be the default, so all test cases remain the same"""

    def setUp(self):
        super().setUp()
        self.path_args = (":memory:",)


class DiskSQLiteTest(InMemorySQLiteTest):
    db_fp = None
    path_args = ()

    def setUp(self):
        super().setUp()
        self.db_fp = str(new_sqlite_file())
        self.path_args = (
            "--sqlite",
            self.db_fp,
        )

    def test_embed_default_hazo_leaves_valid_db_behind(self):
        # This should probably be called for all test cases
        super().test_embed_default_hazo()
        self.assertTrue(DBSniffer(self.db_fp).is_sqlite)


class InMemoryDuckDBTest(InMemorySQLiteTest):
    def setUp(self):
        super().setUp()
        self.path_args = (
            "--duckdb",
            ":memory:",
        )

    def test_duckdb_execute(self):
        out = self.expect_success(*self.path_args, "select 'Hello World!'")
        self.assertIn("('Hello World!',)", out)

    def test_cli_execute_incomplete_sql(self):
        pass

    def test_cli_execute_too_much_sql(self):
        pass

    def test_embed_default_hazo(self):
        # See https://github.com/Florents-Tselai/tsellm/issues/24
        pass

    def test_prompt_default_markov(self):
        # See https://github.com/Florents-Tselai/tsellm/issues/24
        pass

    def test_embed_hazo_binary(self):
        # See https://github.com/Florents-Tselai/tsellm/issues/25
        pass


class DiskDuckDBTest(InMemoryDuckDBTest):
    db_fp = None
    path_args = ()

    def setUp(self):
        super().setUp()
        self.db_fp = str(new_duckdb_file())
        self.path_args = (self.db_fp,)

    def test_duckdb_is_picked_up(self):
        # https://github.com/Florents-Tselai/tsellm/issues/28
        super().test_cli_execute_sql()


if __name__ == "__main__":
    unittest.main()
