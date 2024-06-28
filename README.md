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

Behind the scenes, **tsellm** is based on the beautiful [llm](https://llm.datasette.io) library,
so you can use any of its plugins:

For example, to access `gpt4all` models

```shell
llm install llm-gpt4all
# Then pick any gpt4all (it will be downloaded automatically the first time you use any model
tsellm :memory: "select prompt('What is the capital of Greece?', 'orca-mini-3b-gguf2-q4_0')"
tsellm :memory: "select prompt('What is the capital of Greece?', 'orca-2-7b')"
```

## Embeddings

```shell
llm install llm-sentence-transformers
llm sentence-transformers register all-MiniLM-L12-v2
tsellm :memory: "select embed('Hello', 'sentence-transformers/all-MiniLM-L12-v2')"
```

## Examples

Things get more interesting if you
combine models in your standard SQLite queries.

First, create a db with some data

```bash
sqlite3 prompts.db <<EOF
CREATE TABLE [prompts] (
   [p] TEXT
);
INSERT INTO prompts VALUES('hello world!');
INSERT INTO prompts VALUES('how are you?');
INSERT INTO prompts VALUES('is this real life?');
INSERT INTO prompts VALUES('1+1=?');
EOF
```

With a single query you can access get prompt 
responses from different LLMs:

```sql
tsellm prompts.db "
        select p,
        prompt(p, 'orca-2-7b'),
        prompt(p, 'orca-mini-3b-gguf2-q4_0'),
        embed(p, 'sentence-transformers/all-MiniLM-L12-v2') 
        from prompts"
```

## Interactive Shell

If you don't provide an SQL query,
you'll enter an interactive shell instead.

```shell
tsellm prompts.db
```

![til](./tsellm-demo.gif)

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

