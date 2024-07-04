import sqlite3
import sys

from argparse import ArgumentParser
from code import InteractiveConsole
from textwrap import dedent
from .core import _tsellm_init
from abc import ABC, abstractmethod, abstractproperty


class TsellmConsole(ABC, InteractiveConsole):
    error_class = None

    def __init__(self, path):
        super().__init__()
        self._con = sqlite3.connect(path, isolation_level=None)
        self._cur = self._con.cursor()

        _tsellm_init(self._con)

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


def cli(*args):
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
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"SQLite version {sqlite3.sqlite_version}",
        help="Print underlying SQLite library version",
    )
    args = parser.parse_args(*args)

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

    console = SQLiteConsole(args.filename)
    try:
        if args.sql:
            # SQL statement provided on the command-line; execute it directly.
            console.execute(args.sql, suppress_errors=False)
        else:
            # No SQL provided; start the REPL.
            console = SQLiteConsole(args.filename)
            try:
                import readline
            except ImportError:
                pass
            console.interact(banner, exitmsg="")
    finally:
        console.connection.close()

    sys.exit(0)
