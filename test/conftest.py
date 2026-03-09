import asyncio
import sys
import os
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "master" / "skills" / "definitions"
AGENTS_MD = PROJECT_ROOT / "prompts" / "AGENTS.md"
SOUL_MD = PROJECT_ROOT / "prompts" / "soul.md"


@pytest.fixture
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def skills_dir():
    return SKILLS_DIR


@pytest.fixture
def memory_sources():
    return [str(AGENTS_MD)]


@pytest.fixture
def default_work_dir(tmp_path):
    return str(tmp_path / "workspace")


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_backend(default_work_dir):
    from deepagents.backends import FilesystemBackend
    return FilesystemBackend(root_dir=default_work_dir)
