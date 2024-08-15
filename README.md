# tsellm: Use LLMs in SQLite and DuckDB

[![Github](https://img.shields.io/static/v1?label=GitHub&message=Repo&logo=GitHub&color=green)](https://github.com/Florents-Tselai/tsellm)
[![PyPI](https://img.shields.io/pypi/v/tsellm.svg)](https://pypi.org/project/tsellm/)
[![Documentation Status](https://readthedocs.org/projects/tsellm/badge/?version=stable)](http://tsellm.tselai.com/en/latest/?badge=stable)
[![Linkedin](https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/florentstselai/)
[![Github Sponsors](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=pink)](https://github.com/sponsors/Florents-Tselai/)
[![pip installs](https://img.shields.io/pypi/dm/tsellm?label=pip%20installs)](https://pypi.org/project/tsellm/)
[![Tests](https://github.com/Florents-Tselai/tsellm/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/Florents-Tselai/tsellm/actions?query=workflow%3ATest)
[![codecov](https://codecov.io/gh/Florents-Tselai/tsellm/branch/main/graph/badge.svg)](https://codecov.io/gh/Florents-Tselai/tsellm)
[![License](https://img.shields.io/badge/BSD%20license-blue.svg)](https://github.com/Florents-Tselai/tsellm/blob/main/LICENSE)

**tsellm** is the easiest way to access LLMs from SQLite or DuckDB.

```shell
pip install tsellm
```

```bash
cat <<EOF | tee >(sqlite3 prompts.sqlite3) | duckdb prompts.duckdb
CREATE TABLE prompts ( p TEXT);
INSERT INTO prompts VALUES('how are you?');
INSERT INTO prompts VALUES('is this real life?');
EOF
```

```shell
llm install llm-gpt4all
```

```sql
tsellm prompts.duckdb "select prompt(p, 'orca-mini-3b-gguf2-q4_0') from prompts"
tsellm prompts.sqlite3 "select prompt(p, 'orca-2-7b') from prompts"
```

Behind the scenes, **tsellm** is based on the beautiful [llm](https://llm.datasette.io) library,
so you can use any of its plugins:

## Embeddings

```shell
llm install llm-sentence-transformers
llm sentence-transformers register all-MiniLM-L12-v2
llm install llm-embed-hazo # dummy embedding model for demonstration purposes
```

```sql
tsellm prompts.sqlite3 "select embed(p, 'sentence-transformers/all-MiniLM-L12-v2')"
```

### Embedding `JSON` Recursively

If you have `JSON` columns, you can embed these object recursively.
That is, an embedding vector of floats will replace each text occurrence in the object.

```bash
cat <<EOF | tee >(sqlite3 prompts.sqlite3) | duckdb prompts.duckdb
CREATE TABLE people(d JSON);
INSERT INTO people (d) VALUES 
('{"name": "John Doe", "age": 30, "hobbies": ["reading", "biking"]}'),
('{"name": "Jane Smith", "age": 25, "hobbies": ["painting", "traveling"]}')
EOF
```

#### SQLite

```sql
tsellm prompts.sqlite3 "select json_embed(d, 'hazo') from people"
```

*Output*
        
```
('{"name": [4.0, 3.0,..., 0.0], "age": 30, "hobbies": [[7.0, 0.0,..., 0.0], [6.0, 0.0, ..., 0.0]]}',)
('{"name": [4.0, 5.0, ,..., 0.0], "age": 25, "hobbies": [[8.0, 0.0,..., 0.0], [9.0, 0.0,..., 0.0]]}',)
```

#### DuckDB

```sql
tsellm prompts.duckdb "select json_embed(d, 'hazo') from people"
```

*Output*
        
```
('{"name": [4.0, 3.0,..., 0.0], "age": 30, "hobbies": [[7.0, 0.0,..., 0.0], [6.0, 0.0, ..., 0.0]]}',)
('{"name": [4.0, 5.0, ,..., 0.0], "age": 25, "hobbies": [[8.0, 0.0,..., 0.0], [9.0, 0.0,..., 0.0]]}',)
```

### Embeddings for binary (`BLOB`) columns

```shell
wget https://tselai.com/img/flo.jpg
sqlite3 images.sqlite3 <<EOF
CREATE TABLE images(name TEXT, type TEXT, img BLOB);
INSERT INTO images(name,type,img) VALUES('flo','jpg',readfile('flo.jpg'));
EOF
```

```shell
llm install llm-clip
```

```sql
tsellm images.sqlite3 "select embed(img, 'clip') from images"
```

## Multiple Prompts

With a single query you can easily access get prompt 
responses from different LLMs:

```sql
tsellm prompts.sqlite3 "
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

