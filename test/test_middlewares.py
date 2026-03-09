import pytest
from pathlib import Path


class TestMemoryMiddleware:
    """MemoryMiddleware 单元测试"""

    def test_memory_middleware_init(self, mock_backend, memory_sources):
        """测试 MemoryMiddleware 初始化"""
        from deepagents.middleware import MemoryMiddleware
        
        middleware = MemoryMiddleware(
            backend=mock_backend,
            sources=memory_sources,
        )
        
        assert middleware is not None
        assert len(middleware.sources) == 1

    def test_memory_sources_exist(self, memory_sources):
        """测试记忆文件存在"""
        for source in memory_sources:
            path = Path(source)
            assert path.exists(), f"Memory source not found: {source}"

    def test_memory_content_not_empty(self, memory_sources):
        """测试记忆文件内容非空"""
        for source in memory_sources:
            path = Path(source)
            content = path.read_text(encoding="utf-8")
            assert len(content) > 0, f"Memory source is empty: {source}"


class TestSkillsMiddleware:
    """SkillsMiddleware 单元测试"""

    def test_skills_middleware_init(self, mock_backend, skills_dir):
        """测试 SkillsMiddleware 初始化"""
        from deepagents.middleware import SkillsMiddleware
        
        middleware = SkillsMiddleware(
            backend=mock_backend,
            sources=[str(skills_dir)],
        )
        
        assert middleware is not None

    def test_skills_dir_exists(self, skills_dir):
        """测试技能目录存在"""
        assert skills_dir.exists(), f"Skills directory not found: {skills_dir}"
        assert skills_dir.is_dir(), f"Skills path is not a directory: {skills_dir}"

    def test_skills_subdirs_exist(self, skills_dir):
        """测试技能子目录存在"""
        expected_skills = [
            "competitor-benchmarking",
            "content-creation",
            "content-review",
            "inspiration-hunting",
        ]
        
        for skill_name in expected_skills:
            skill_dir = skills_dir / skill_name
            assert skill_dir.exists(), f"Skill directory not found: {skill_name}"
            skill_md = skill_dir / "SKILL.md"
            assert skill_md.exists(), f"SKILL.md not found in {skill_name}"


class TestFilesystemMiddleware:
    """FilesystemMiddleware 单元测试"""

    def test_filesystem_middleware_init(self, mock_backend):
        """测试 FilesystemMiddleware 初始化"""
        from deepagents.middleware import FilesystemMiddleware
        
        middleware = FilesystemMiddleware(
            backend=mock_backend,
            tool_token_limit_before_evict=20000,
        )
        
        assert middleware is not None

    def test_filesystem_eviction_threshold(self, mock_backend):
        """测试驱逐阈值配置"""
        from deepagents.middleware import FilesystemMiddleware
        
        threshold = 20000
        middleware = FilesystemMiddleware(
            backend=mock_backend,
            tool_token_limit_before_evict=threshold,
        )
        
        assert middleware._tool_token_limit_before_evict == threshold


class TestSummarizationMiddleware:
    """SummarizationMiddleware 单元测试"""

    def test_summarization_middleware_init(self, mock_backend):
        """测试 SummarizationMiddleware 初始化"""
        from deepagents.middleware import SummarizationMiddleware
        from unittest.mock import MagicMock
        
        mock_model = MagicMock()
        
        middleware = SummarizationMiddleware(
            model=mock_model,
            backend=mock_backend,
        )
        
        assert middleware is not None
