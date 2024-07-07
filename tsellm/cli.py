import sqlite3
import sys
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from code import InteractiveConsole
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from textwrap import dedent
from typing import Union

import duckdb

from . import __version__
from .core import (
    _prompt_model,
    _prompt_model_default,
    _embed_model,
    _embed_model_default,
)


class DatabaseType(Enum):
    SQLITE = auto()
    DUCKDB = auto()
    UNKNOWN = auto()
    FILE_NOT_FOUND = auto()
    ERROR = auto()


sys.ps1 = "tsellm> "
sys.ps2 = "    ... "


class TsellmConsoleMixin(InteractiveConsole):
    def is_sqlite(self, path):
        try:
            with sqlite3.connect(path) as conn:
                conn.execute("SELECT 1")
                return True
        except:
            return False

    def is_duckdb(self, path):
        try:
            con = duckdb.connect(path.__str__())
            con.sql("SELECT 1")
            return True
        except:
            return False

    def sniff_db(self, path):
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


@dataclass
class TsellmConsole(InteractiveConsole, ABC):
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
    db_type: str = field(init=False)
    connection: Union[sqlite3.Connection, duckdb.DuckDBPyConnection] = field(init=False)

    @property
    def tsellm_version(self) -> str:
        return __version__.__version__

    @property
    def eofkey(self):
        if sys.platform == "win32" and "idlelib.run" not in sys.modules:
            return "CTRL-Z"
        else:
            return "CTRL-D"

    @property
    def db_name(self):
        return self.path

    @property
    def banner(self) -> str:
        return dedent(
            f"""
        tsellm shell version {self.tsellm_version}, running on {self.db_type} version {self.db_version}
        Connected to {self.db_name}

        Each command will be run using execute() on the cursor.
        Type ".help" for more information; type ".quit" or {self.eofkey} to quit.
        """
        ).strip()

    @property
    @abstractmethod
    def db_version(self) -> str:
        pass

    @property
    @abstractmethod
    def is_valid_db(self) -> bool:
        pass

    @abstractmethod
    def complete_statement(self, source) -> bool:
        pass

    @property
    def version(self):
        return " ".join([
            "tsellm version",
            self.tsellm_version,
            self.db_type,
            "version",
            self.db_version]
        )

    def load(self):
        self.execute(self._TSELLM_CONFIG_SQL)
        for func_name, n_args, py_func, deterministic in self._functions:
            self.connection.create_function(func_name, n_args, py_func)

    @staticmethod
    def create_console(path):
        if TsellmConsoleMixin().is_duckdb(path):
            return DuckDBConsole(path)
        if TsellmConsoleMixin().is_sqlite(path):
            return SQLiteConsole(path)
        else:
            raise ValueError(f"Database type {path} not supported")

    @abstractmethod
    def execute(self, sql, suppress_errors=True):
        pass

    def runsource(self, source, filename="<input>", symbol="single"):
        """Override runsource, the core of the InteractiveConsole REPL.

        Return True if more input is needed; buffering is done automatically.
        Return False is input is a complete statement ready for execution.
        """
        match source:
            case ".version":
                print(f"{self.version}")
            case ".help":
                print("Enter SQL code and press enter.")
            case ".quit":
                sys.exit(0)
            case _:
                if not self.complete_statement(source):
                    return True
                self.execute(source)
        return False

    @abstractmethod
    def connect(self):
        pass

    def __post_init__(self):
        super().__init__()
        self.connect()
        self._cur = self.connection.cursor()
        self.load()


@dataclass
class SQLiteConsole(TsellmConsole):
    db_type = "SQLite"

    def connect(self):
        self.connection = sqlite3.connect(self.path, isolation_level=None)

    path: Union[Path, str, sqlite3.Connection, duckdb.DuckDBPyConnection]
    error_class = sqlite3.Error

    def complete_statement(self, source) -> bool:
        return sqlite3.complete_statement(source)

    @property
    def is_valid_db(self) -> bool:
        pass

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

    @property
    def db_version(self):
        return sqlite3.sqlite_version


@dataclass
class DuckDBConsole(TsellmConsole):
    db_type = "DuckDB"
    path: Union[Path, str, sqlite3.Connection, duckdb.DuckDBPyConnection]

    def complete_statement(self, source) -> bool:
        return sqlite3.complete_statement(source)

    @property
    def is_valid_db(self) -> bool:
        pass

    error_class = sqlite3.Error

    _functions = [
        ("prompt", 2, _prompt_model, False),
        ("embed", 2, _embed_model, False),
    ]

    def connect(self):
        self.connection = duckdb.connect(self.path)

    def load(self):
        self.execute(self._TSELLM_CONFIG_SQL)
        for func_name, _, py_func, _ in self._functions:
            self.connection.create_function(func_name, py_func)

    @property
    def db_version(self):
        return duckdb.__version__

    def execute(self, sql, suppress_errors=True):
        """Helper that wraps execution of SQL code.

        This is used both by the REPL and by direct execution from the CLI.

        'c' may be a cursor or a connection.
        'sql' is the SQL string to execute.
        """

        try:
            for row in self.connection.execute(sql).fetchall():
                print(row)
        except self.error_class as e:
            tp = type(e).__name__
            try:
                print(f"{tp} ({e.sqlite_errorname}): {e}", file=sys.stderr)
            except AttributeError:
                print(f"{tp}: {e}", file=sys.stderr)
            if not suppress_errors:
                sys.exit(1)


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
            "SQLite/DuckDB database to open (defaults to SQLite ':memory:'). "
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
        version=f"tsellm version {__version__.__version__}",
        help="Print underlying SQLite library version",
    )
    return parser


def cli(*args):
    args = make_parser().parse_args(*args)

    if args.sqlite and args.duckdb:
        raise ValueError("Only one of --sqlite and --duckdb can be specified.")

    if (not args.sqlite) and (not args.duckdb) and args.filename == ":memory:":
        args.sqlite = True
        args.duckdb = False

    console = (
        DuckDBConsole(args.filename) if args.duckdb else SQLiteConsole(args.filename)
    )

    try:
        if args.sql:
            # SQL statement provided on the command-line; execute it directly.
            console.execute(args.sql, suppress_errors=False)
        else:
            try:
                import readline
            except ImportError:
                pass
            console.interact(console.banner, exitmsg="")
    finally:
        console.connection.close()

    sys.exit(0)
