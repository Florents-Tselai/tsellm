from setuptools import setup
import os
from tsellm import __version__


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="tsellm",
    description=__version__.__description__,
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Florents Tselai",
    author_email="florents@tselai.com",
    url="https://github.com/Florents-Tselai/tsellm",
    entry_points="""
        [console_scripts]
        tsellm=tsellm.cli:cli
    """,
    project_urls={
        "Issues": "https://github.com/Florents-Tselai/tsellm/issues",
        "CI": "https://github.com/Florents-Tselai/tsellm/actions",
        "Changelog": "https://github.com/Florents-Tselai/tsellm/releases",
        "Documentation": "https://tsellm.tselai.com/en/stable/",
        "Source code": "https://github.com/Florents-Tselai/tsellm",
    },
    license="BSD License",
    version=__version__.__version__,
    packages=["tsellm"],
    install_requires=["llm", "setuptools", "pip", "duckdb"],
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
            "black",
            "ruff",
            "sqlite_utils",
            "llm-markov",
            "llm-embed-hazo==0.2.1",
        ]
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Database",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
