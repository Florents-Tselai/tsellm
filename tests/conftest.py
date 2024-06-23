from sqlite_utils import Database
import pytest

import pytest
import json
import llm
from llm.plugins import pm
from typing import Optional
import sqlite_utils
from pydantic import Field


def pytest_configure(config):
    import sys

    sys._called_from_test = True


@pytest.fixture
def user_path(tmpdir):
    dir = tmpdir / "tsellm"
    dir.mkdir()
    return dir


@pytest.fixture
def logs_db(user_path):
    return sqlite_utils.Database(str(user_path / "logs.db"))


@pytest.fixture
def user_path_with_embeddings(user_path):
    path = str(user_path / "embeddings.db")
    db = sqlite_utils.Database(path)
    collection = llm.Collection("demo", db, model_id="embed-demo")
    collection.embed("1", "hello world")
    collection.embed("2", "goodbye world")


class MockModel(llm.Model):
    model_id = "mock-echo"

    class Options(llm.Options):
        max_tokens: Optional[int] = Field(
            description="Maximum number of tokens to generate.", default=None
        )

    def __init__(self):
        self.history = []
        self._queue = []

    def enqueue(self, messages):
        assert isinstance(messages, list)
        self._queue.append(messages)

    def execute(self, prompt, stream, response, conversation):
        self.history.append((prompt, stream, response, conversation))
        while True:
            try:
                messages = self._queue.pop(0)
                yield from messages
                break
            except IndexError:
                break


class EmbedDemo(llm.EmbeddingModel):
    model_id = "embed-demo"
    batch_size = 10
    supports_binary = True

    def __init__(self):
        self.embedded_content = []

    def embed_batch(self, texts):
        if not hasattr(self, "batch_count"):
            self.batch_count = 0
        self.batch_count += 1
        for text in texts:
            self.embedded_content.append(text)
            words = text.split()[:16]
            embedding = [len(word) for word in words]
            # Pad with 0 up to 16 words
            embedding += [0] * (16 - len(embedding))
            yield embedding


class EmbedBinaryOnly(EmbedDemo):
    model_id = "embed-binary-only"
    supports_text = False
    supports_binary = True


class EmbedTextOnly(EmbedDemo):
    model_id = "embed-text-only"
    supports_text = True
    supports_binary = False


@pytest.fixture
def embed_demo():
    return EmbedDemo()


@pytest.fixture
def mock_model():
    return MockModel()


@pytest.fixture(autouse=True)
def register_embed_demo_model(embed_demo, mock_model):
    class MockModelsPlugin:
        __name__ = "MockModelsPlugin"

        @llm.hookimpl
        def register_embedding_models(self, register):
            register(embed_demo)
            register(EmbedBinaryOnly())
            register(EmbedTextOnly())

        @llm.hookimpl
        def register_models(self, register):
            register(mock_model)

    pm.register(MockModelsPlugin(), name="undo-mock-models-plugin")
    try:
        yield
    finally:
        pm.unregister(name="undo-mock-models-plugin")


@pytest.fixture
def db_path(tmpdir):
    path = str(tmpdir / "test.db")
    return path


@pytest.fixture
def fresh_db_path(db_path):
    return db_path

@pytest.fixture
def existing_db_path(fresh_db_path):
    db = Database(fresh_db_path)
    table = db.create_table(
        "prompts",
        {
            "prompt": str,
            "generated": str,
            "model": str,
            "embedding": dict,
        },
    )

    table.insert({"prompt": "hello world!"})
    table.insert({"prompt": "how are you?"})
    table.insert({"prompt": "is this real life?"})
    return fresh_db_path
