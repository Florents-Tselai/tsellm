from setuptools import setup
import os

VERSION = "0.0.0a0"


def get_long_description():
    with open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
            encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="tsellm",
    description="LLM support in SQLite",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Florents Tselai",
    url="https://github.com/Florents-Tselai/tsellm",
    entry_points="""
        [console_scripts]
        tsellm=tsellm.cli:cli
    """,
    project_urls={
        "Issues": "https://github.com/Florents-Tselai/tsellm/issues",
        "CI": "https://github.com/Florents-Tselai/tsellm/actions",
        "Changelog": "https://github.com/Florents-Tselai/tsellm/releases",
    },
    license="MIT License",
    version=VERSION,
    packages=["tsellm"],
    install_requires=["llm", "setuptools", "pip"],
    extras_require={
        "test": ["pytest", "pytest-cov", "black", "ruff", "sqlite_utils"]
    },
    python_requires=">=3.7",
)
