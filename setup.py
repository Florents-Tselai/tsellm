from tsellm import __version__
from setuptools import setup, Command
import os
import shutil
import glob


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Paths to clean
        files_to_remove = ["*.jpg", "*.sqlite3", "*.duckdb"]
        dirs_to_clean = ["build", "dist", "*.egg-info"]

        for pattern in files_to_remove:
            for file in glob.glob(pattern):
                try:
                    os.remove(file)
                    print(f"Removed file: {file}")
                except Exception as e:
                    print(f"Could not remove {file}: {e}")

        for pattern in dirs_to_clean:
            for dir in glob.glob(pattern):
                try:
                    shutil.rmtree(dir)
                    print(f"Removed directory: {dir}")
                except Exception as e:
                    print(f"Could not remove {dir}: {e}")


setup(
    name="tsellm",
    description=__version__.__description__,
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Florents Tselai",
    url="https://github.com/Florents-Tselai/tsellm",
    entry_points="""
        [console_scripts]
        tsellm=tsellm.cli:cli
    """,
    cmdclass={
        "clean": CleanCommand,
    },
    project_urls={
        "Issues": "https://github.com/Florents-Tselai/tsellm/issues",
        "CI": "https://github.com/Florents-Tselai/tsellm/actions",
        "Changelog": "https://github.com/Florents-Tselai/tsellm/releases",
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
)
