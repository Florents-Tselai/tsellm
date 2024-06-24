# tsellm: Use LLMs in your SQLite queries

<p align="center">
<a href="https://pypi.org/project/tsellm/"><img src="https://img.shields.io/pypi/v/tsellm?label=PyPI"></a>
<a href="https://pypi.org/project/tsellm/"><img alt="installs" src="https://img.shields.io/pypi/dm/tsellm?label=pip%20installs"></a>
<a href="https://github.com/Florents-Tselai/tsellm/actions/workflows/test.yml?branch=mainline"><img src="https://github.com/Florents-Tselai/tsellm/actions/workflows/test.yml/badge.svg"></a>
<a href="https://codecov.io/gh/Florents-Tselai/tsellm"><img src="https://codecov.io/gh/Florents-Tselai/tsellm/branch/main/graph/badge.svg"></a>  
<a href="https://opensource.org/licenses/BSD license"><img src="https://img.shields.io/badge/BSD license-blue.svg"></a>

**tsellm** is the easiest way to access LLMs through your SQLite database.


```shell
pip install tsellm
```

You can then use LLMs in your SQL queries.
You can supply your queries through a simple CLI.
```shell
tsellm my.sqlite3 "select prompt(p, 'orca-2-7b') from my_table"
```

You can also enter an interactive REPL shell and try things out.

```shell
tsellm my.sqlite3
```

![til](./tsellm-demo.gif)

## Examples

Let's create a simple SQLite database with some data.

```bash
sqlite3 prompts.db <<EOF
CREATE TABLE [prompts] (
   [prompt] TEXT
);
INSERT INTO prompts VALUES('hello world!');
INSERT INTO prompts VALUES('how are you?');
INSERT INTO prompts VALUES('is this real life?');
INSERT INTO prompts VALUES('1+1=?');
EOF
```

### CLI

You can use any of the [llm plugins](https://llm.datasette.io/en/stable/plugins/directory.html)

You can execute LLM-powered SQL queries directly in the CLI, like so:

First, let's install a dummy plugin.

```shell
llm install llm-markov
```
```shell
tsellm prompts.db "select prompt(prompt, 'markov') from prompts"
```
Now let's try a more complex one, 

```shell
llm install llm-gpt4all
```

```shell
tsellm prompts.db "select prompt(prompt, 'orca-2-7b') from prompts"
```

### Interactive Shell

You can enter an interactive REPL-style shell to manipulate your database.

```shell
tsellm prompts.db
```

There you can do queries the normal way:
```sql
ALTER TABLE prompts ADD COLUMN orca;
UPDATE PROMPTS SET orca=prompt(prompt, 'orca-2-7b');
```


## Installation

```bash
pip install tsellm
```

## How

**tsellm** relies on the following facts:

* SQLite is bundled with the standard Python library (`import sqlite3`)
* Python 3.12 ships with a [SQLite interactive shell](https://docs.python.org/3/library/sqlite3.html#command-line-interface)
* one can create Python-written user-defined functions to be used in SQLite 
  queries (see [create_function](https://github.com/simonw/llm))
* [Simon Willison](https://github.com/simonw/) has gone through the process of 
  creating the beautiful [llm](https://github.com/simonw/llm) Python 
  library and CLI

## Development

```bash
pip install -e '.[test]'
pytest
```

