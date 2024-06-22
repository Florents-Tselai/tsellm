<p align="center">

<p align="center">
   <img width="50%" height="40%" src="" alt="Logo">
  </p>

  <h1 align="center">tsellm</h1>
  <p align="center">
  <strong>SQLite with LLM Superpowers</strong>
    <br> <br />
    <a href="#how"><strong> How </strong></a> |
    <a href="#installation"><strong> Installation </strong></a> |
    <a href="#usage"><strong> Usage </strong></a> |
    <a href="#roadmap"><strong> Roadmap </strong></a> 

   </p>
<p align="center">

<p align="center">
<a href="https://pypi.org/project/tsellm/"><img src="https://img.shields.io/pypi/v/tsellm?label=PyPI"></a>
<a href="https://github.com/Florents-Tselai/tsellm/actions/workflows/test.yml?branch=mainline"><img src="https://github.com/Florents-Tselai/tsellm/actions/workflows/test.yml/badge.svg"></a>
<a href="https://codecov.io/gh/Florents-Tselai/tsellm"><img src="https://codecov.io/gh/Florents-Tselai/tsellm/branch/main/graph/badge.svg"></a>  
<a href="https://opensource.org/licenses/BSD license"><img src="https://img.shields.io/badge/BSD license.0-blue.svg"></a>
<a href="https://github.com/Florents-Tselai/tsellm/releases"><img src="https://img.shields.io/github/v/release/Florents-Tselai/tsellm?include_prereleases&label=changelog"></a>

**tsellm** is SQLite wrapper with LLM superpowers.
It's available as Python package and as a SQLite shell wrapper.

## How

**tsellm** relies on three facts:

* SQLite is bundled with the standard Python library (`import sqlite3`)
* one can create Python-written user-defined functions to be used in SQLite 
  queries (see [create_function](https://github.com/simonw/llm))
* [Simon Willison](https://github.com/simonw/) has gone through the process of 
  creating the beautiful [llm](https://github.com/simonw/llm) Python 
  library and CLI

With that in mind, one can bring the whole `llm` library into SQLite.
**tsellm** attempts to do just that

## Installation

## Usage

```bash
pip install tsellm
```

### Development

```bash
pip install -e '.[test]'
pytest
```

