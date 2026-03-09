import pytest
from pathlib import Path


class TestSkillIndex:
    """技能索引测试"""

    def test_skill_discovery(self, skills_dir):
        """测试技能发现"""
        from master.skills.manager import SkillIndex
        
        index = SkillIndex(skills_root=skills_dir)
        metas = index.discover()
        
        assert len(metas) == 4, f"Expected 4 skills, found {len(metas)}"

    def test_skill_names(self, skills_dir):
        """测试技能名称"""
        from master.skills.manager import SkillIndex
        
        index = SkillIndex(skills_root=skills_dir)
        metas = index.discover()
        
        expected_names = {
            "competitor-benchmarking",
            "content-creation",
            "content-review",
            "inspiration-hunting",
        }
        
        actual_names = set(metas.keys())
        assert actual_names == expected_names, f"Skill names mismatch: {actual_names}"

    def test_skill_meta_parsing(self, skills_dir):
        """测试技能元数据解析"""
        from master.skills.manager import SkillIndex
        
        index = SkillIndex(skills_root=skills_dir)
        metas = index.discover()
        
        for name, meta in metas.items():
            assert meta.name == name
            assert len(meta.description) > 0, f"Empty description for {name}"
            assert len(meta.triggers) > 0, f"No triggers for {name}"
            assert len(meta.tools) > 0, f"No tools for {name}"

    def test_skill_trigger_matching(self, skills_dir):
        """测试触发词匹配"""
        from master.skills.manager import SkillIndex
        
        index = SkillIndex(skills_root=skills_dir)
        metas = index.discover()
        
        test_cases = [
            ("帮我写一篇咖啡笔记", "content-creation"),
            ("竞对分析一下咖啡赛道", "competitor-benchmarking"),
            ("复盘一下我的笔记数据", "content-review"),
            ("找找咖啡赛道的灵感", "inspiration-hunting"),
        ]
        
        for task, expected_skill in test_cases:
            matched = index.find_triggered_skills(task, metas)
            matched_names = [m.name for m in matched]
            assert expected_skill in matched_names, \
                f"Task '{task}' should trigger '{expected_skill}', got {matched_names}"

    def test_skill_markdown_reading(self, skills_dir):
        """测试 SKILL.md 读取"""
        from master.skills.manager import SkillIndex
        
        index = SkillIndex(skills_root=skills_dir)
        
        content = index.read_skill_markdown("content-creation")
        
        assert len(content) > 0
        assert "content-creation" in content.lower() or "内容生成" in content

    def test_build_manifest_text(self, skills_dir):
        """测试技能清单生成"""
        from master.skills.manager import SkillIndex
        
        index = SkillIndex(skills_root=skills_dir)
        metas = index.discover()
        
        manifest = index.build_manifest_text(metas)
        
        assert len(manifest) > 0
        assert "content-creation" in manifest
        assert "competitor-benchmarking" in manifest


class TestIndividualSkills:
    """单个技能验证测试"""

    def _load_skill_content(self, skills_dir, skill_name):
        skill_md = skills_dir / skill_name / "SKILL.md"
        return skill_md.read_text(encoding="utf-8")

    def test_competitor_benchmarking_skill(self, skills_dir):
        """测试竞品对标技能"""
        content = self._load_skill_content(skills_dir, "competitor-benchmarking")
        
        assert "竞品" in content or "competitor" in content.lower()
        assert "use_browser" in content
        assert "触发词" in content or "triggers" in content.lower()

    def test_content_creation_skill(self, skills_dir):
        """测试内容生成技能"""
        content = self._load_skill_content(skills_dir, "content-creation")
        
        assert "generate_note" in content
        assert "use_browser" in content
        assert "禁止瞎编" in content or "真实信息" in content

    def test_content_review_skill(self, skills_dir):
        """测试内容复盘技能"""
        content = self._load_skill_content(skills_dir, "content-review")
        
        assert "复盘" in content or "review" in content.lower()
        assert "use_browser" in content
        assert "数据" in content

    def test_inspiration_hunting_skill(self, skills_dir):
        """测试灵感收集技能"""
        content = self._load_skill_content(skills_dir, "inspiration-hunting")
        
        assert "灵感" in content or "inspiration" in content.lower()
        assert "use_browser" in content
        assert "选题" in content


class TestMemoryManager:
    """记忆管理器测试"""

    def test_memory_manager_init(self, memory_sources):
        """测试 MemoryManager 初始化"""
        from master.skills.manager import MemoryManager
        
        manager = MemoryManager(memory_paths=memory_sources)
        
        assert len(manager.memory_paths) == 1

    def test_memory_load(self, memory_sources):
        """测试记忆加载"""
        from master.skills.manager import MemoryManager
        
        manager = MemoryManager(memory_paths=memory_sources)
        content = manager.load_memories()
        
        assert len(content) > 0
        assert "Agent Memory" in content or "长期记忆" in content

    def test_add_memory_path(self, memory_sources, tmp_path):
        """测试添加记忆路径"""
        from master.skills.manager import MemoryManager
        
        manager = MemoryManager(memory_paths=memory_sources)
        initial_count = len(manager.memory_paths)
        
        new_path = tmp_path / "new_memory.md"
        new_path.write_text("test content", encoding="utf-8")
        
        manager.add_memory_path(new_path)
        
        assert len(manager.memory_paths) == initial_count + 1
