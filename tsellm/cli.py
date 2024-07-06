import sqlite3
import sys
import duckdb
from argparse import ArgumentParser
from code import InteractiveConsole
from textwrap import dedent
from .core import (
    _tsellm_init,
    _prompt_model,
    _prompt_model_default,
    _embed_model,
    _embed_model_default,
)
from abc import ABC, abstractmethod, abstractproperty

from enum import Enum, auto


class DatabaseType(Enum):
    SQLITE = auto()
    DUCKDB = auto()
    UNKNOWN = auto()
    FILE_NOT_FOUND = auto()
    ERROR = auto()


class TsellmConsole(ABC, InteractiveConsole):
    _TSELLM_CONFIG_SQL = """
-- tsellm configuration table
-- need to be taken care of accross migrations and versions.

CREATE TABLE IF NOT EXISTS __tsellm (
x text
);

"""

    _functions = [
        ("prompt", 2, _prompt_model, False),
        ("prompt", 1, _prompt_model_default, False),
        ("embed", 2, _embed_model, False),
        ("embed", 1, _embed_model_default, False),
    ]

    error_class = None

    @staticmethod
    def is_sqlite(path):
        try:
            with sqlite3.connect(path) as conn:
                conn.execute("SELECT 1")
                return True
        except:
            return False

    @staticmethod
    def is_duckdb(path):
        try:
            con = duckdb.connect(path.__str__())
            con.sql("SELECT 1")
            return True
        except:
            return False

    @staticmethod
    def sniff_db(path):
        """
        Sniffs if the path is a SQLite or DuckDB database.

        Args:
            path (str): The file path to check.

        Returns:
            DatabaseType: The type of database (DatabaseType.SQLITE, DatabaseType.DUCKDB,
                          DatabaseType.UNKNOWN, DatabaseType.FILE_NOT_FOUND, DatabaseType.ERROR).
        """

        if TsellmConsole.is_sqlite(path):
            return DatabaseType.SQLITE
        if TsellmConsole.is_duckdb(path):
            return DatabaseType.DUCKDB
        return DatabaseType.UNKNOWN

    def load(self):
        self.execute(self._TSELLM_CONFIG_SQL)
        for func_name, n_args, py_func, deterministic in self._functions:
            self._con.create_function(func_name, n_args, py_func)

    @staticmethod
    def create_console(path):
        if TsellmConsole.is_duckdb(path):
            return DuckDBConsole(path)
        if TsellmConsole.is_sqlite(path):
            return SQLiteConsole(path)
        else:
            raise ValueError(f"Database type {path} not supported")

    @property
    def connection(self):
        return self._con

    @abstractmethod
    def execute(self, sql, suppress_errors=True):
        pass

    @abstractmethod
    def runsource(self, source, filename="<input>", symbol="single"):
        pass


class SQLiteConsole(TsellmConsole):
    error_class = sqlite3.Error

    def __init__(self, path):

        super().__init__()
        self._con = sqlite3.connect(path, isolation_level=None)
        self._cur = self._con.cursor()

        self.load()

    def execute(self, sql, suppress_errors=True):
        """Helper that wraps execution of SQL code.

        This is used both by the REPL and by direct execution from the CLI.

        'c' may be a cursor or a connection.
        'sql' is the SQL string to execute.
        """

        try:
            for row in self._cur.execute(sql):
                print(row)
        except self.error_class as e:
            tp = type(e).__name__
            try:
                print(f"{tp} ({e.sqlite_errorname}): {e}", file=sys.stderr)
            except AttributeError:
                print(f"{tp}: {e}", file=sys.stderr)
            if not suppress_errors:
                sys.exit(1)

    def runsource(self, source, filename="<input>", symbol="single"):
        """Override runsource, the core of the InteractiveConsole REPL.

        Return True if more input is needed; buffering is done automatically.
        Return False is input is a complete statement ready for execution.
        """
        match source:
            case ".version":
                print(f"{sqlite3.sqlite_version}")
            case ".help":
                print("Enter SQL code and press enter.")
            case ".quit":
                sys.exit(0)
            case _:
                if not sqlite3.complete_statement(source):
                    return True
                self.execute(source)
        return False


class DuckDBConsole(TsellmConsole):
    error_class = sqlite3.Error

    _functions = [
        ("prompt", 2, _prompt_model, False),
        ("embed", 2, _embed_model, False),
    ]

    def __init__(self, path):
        super().__init__()
        self._con = duckdb.connect(path)
        self._cur = self._con.cursor()

        self.load()

    def load(self):
        self.execute(self._TSELLM_CONFIG_SQL)
        for func_name, _, py_func, _ in self._functions:
            self._con.create_function(func_name, py_func)

    def execute(self, sql, suppress_errors=True):
        """Helper that wraps execution of SQL code.

        This is used both by the REPL and by direct execution from the CLI.

        'c' may be a cursor or a connection.
        'sql' is the SQL string to execute.
        """

        try:
            for row in self._con.execute(sql).fetchall():
                print(row)
        except self.error_class as e:
            tp = type(e).__name__
            try:
                print(f"{tp} ({e.sqlite_errorname}): {e}", file=sys.stderr)
            except AttributeError:
                print(f"{tp}: {e}", file=sys.stderr)
            if not suppress_errors:
                sys.exit(1)

    def runsource(self, source, filename="<input>", symbol="single"):
        """Override runsource, the core of the InteractiveConsole REPL.

        Return True if more input is needed; buffering is done automatically.
        Return False is input is a complete statement ready for execution.
        """
        match source:
            case ".version":
                print(f"{sqlite3.sqlite_version}")
            case ".help":
                print("Enter SQL code and press enter.")
            case ".quit":
                sys.exit(0)
            case _:
                if not sqlite3.complete_statement(source):
                    return True
                self.execute(source)
        return False


def make_parser():
    parser = ArgumentParser(
        description="tsellm sqlite3 CLI",
        prog="python -m tsellm",
    )
    parser.add_argument(
        "filename",
        type=str,
        default=":memory:",
        nargs="?",
        help=(
            "SQLite database to open (defaults to ':memory:'). "
            "A new database is created if the file does not previously exist."
        ),
    )
    parser.add_argument(
        "sql",
        type=str,
        nargs="?",
        help=("An SQL query to execute. " "Any returned rows are printed to stdout."),
    )

    # Create a mutually exclusive group
    group = parser.add_mutually_exclusive_group()

    # Add the SQLite argument
    group.add_argument(
        "--sqlite",
        action="store_true",
        default=False,  # Change the default to False to ensure only one can be true
        help="SQLite mode",
    )

    # Add the DuckDB argument
    group.add_argument(
        "--duckdb",
        action="store_true",
        default=False,  # Set the default to False
        help="DuckDB mode",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"SQLite version {sqlite3.sqlite_version}",
        help="Print underlying SQLite library version",
    )
    return parser


def cli(*args):
    args = make_parser().parse_args(*args)

    if args.sqlite and args.duckdb:
        raise ValueError("Only one of --sqlite and --duckdb can be specified.")

    if args.filename == ":memory:":
        db_name = "a transient in-memory database"
    else:
        db_name = repr(args.filename)

    # Prepare REPL banner and prompts.
    if sys.platform == "win32" and "idlelib.run" not in sys.modules:
        eofkey = "CTRL-Z"
    else:
        eofkey = "CTRL-D"
    banner = dedent(
        f"""
        tsellm shell, running on SQLite version {sqlite3.sqlite_version}
        Connected to {db_name}

        Each command will be run using execute() on the cursor.
        Type ".help" for more information; type ".quit" or {eofkey} to quit.
    """
    ).strip()
    sys.ps1 = "tsellm> "
    sys.ps2 = "    ... "

    console = DuckDBConsole(args.filename) if args.duckdb else SQLiteConsole(args.filename)

    try:
        if args.sql:
            # SQL statement provided on the command-line; execute it directly.
            console.execute(args.sql, suppress_errors=False)
        else:
            # No SQL provided; start the REPL.
            # console = SQLiteConsole(args.filename)
            try:
                import readline
            except ImportError:
                pass
            console.interact(banner, exitmsg="")
    finally:
        console.connection.close()

    sys.exit(0)
