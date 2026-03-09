import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock


class TestSkillTriggering:
    """技能触发测试"""

    @pytest.mark.asyncio
    async def test_skill_trigger_content_creation(self, skills_dir):
        """测试内容创作技能触发"""
        from master.skills.manager import SkillIndex
        
        index = SkillIndex(skills_root=skills_dir)
        metas = index.discover()
        
        task = "帮我写一篇关于咖啡的笔记"
        matched = index.find_triggered_skills(task, metas)
        
        matched_names = [m.name for m in matched]
        assert "content-creation" in matched_names

    @pytest.mark.asyncio
    async def test_skill_trigger_competitor(self, skills_dir):
        """测试竞品分析技能触发"""
        from master.skills.manager import SkillIndex
        
        index = SkillIndex(skills_root=skills_dir)
        metas = index.discover()
        
        task = "竞对分析一下咖啡赛道的账号"
        matched = index.find_triggered_skills(task, metas)
        
        matched_names = [m.name for m in matched]
        assert "competitor-benchmarking" in matched_names

    @pytest.mark.asyncio
    async def test_skill_trigger_review(self, skills_dir):
        """测试内容复盘技能触发"""
        from master.skills.manager import SkillIndex
        
        index = SkillIndex(skills_root=skills_dir)
        metas = index.discover()
        
        task = "复盘一下最近发布的笔记数据"
        matched = index.find_triggered_skills(task, metas)
        
        matched_names = [m.name for m in matched]
        assert "content-review" in matched_names

    @pytest.mark.asyncio
    async def test_skill_trigger_inspiration(self, skills_dir):
        """测试灵感收集技能触发"""
        from master.skills.manager import SkillIndex
        
        index = SkillIndex(skills_root=skills_dir)
        metas = index.discover()
        
        task = "帮我找找咖啡赛道的创作灵感"
        matched = index.find_triggered_skills(task, metas)
        
        matched_names = [m.name for m in matched]
        assert "inspiration-hunting" in matched_names


class TestAgentWorkflow:
    """Agent 工作流测试"""

    @pytest.mark.asyncio
    async def test_agent_stream_response(self, default_work_dir):
        """测试 Agent 流式响应"""
        from master.controller import CoreController
        
        with patch('master.controller.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_get_llm.return_value = mock_llm
            
            with patch('master.controller.create_deep_agent') as mock_create_agent:
                mock_agent = MagicMock()
                
                async def mock_astream(*args, **kwargs):
                    yield {"model": {"messages": [MagicMock(content="Test")]}}
                
                mock_agent.astream = mock_astream
                mock_create_agent.return_value = mock_agent
                
                controller = CoreController(
                    uid="test_user",
                    default_work_dir=default_work_dir,
                )
                
                assert controller.agent is not None

    @pytest.mark.asyncio
    async def test_error_handling(self, default_work_dir):
        """测试错误处理"""
        from master.controller import CoreController
        
        with patch('master.controller.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_get_llm.return_value = mock_llm
            
            with patch('master.controller.create_deep_agent') as mock_create_agent:
                mock_agent = MagicMock()
                
                async def mock_astream(*args, **kwargs):
                    raise Exception("Test error")
                    yield {}
                
                mock_agent.astream = mock_astream
                mock_create_agent.return_value = mock_agent
                
                controller = CoreController(
                    uid="test_user",
                    default_work_dir=default_work_dir,
                )
                
                results = []
                async for chunk in controller.run("test brief"):
                    results.append(chunk)
                
                assert len(results) > 0
                assert "Test error" in results[0]


class TestContextVariables:
    """上下文变量测试"""

    def test_work_dir_context_var(self):
        """测试工作目录上下文变量"""
        import contextvars
        from master.controller import current_work_dir_cv
        
        assert current_work_dir_cv.get() == "./workspace"
        
        token = current_work_dir_cv.set("/tmp/test")
        assert current_work_dir_cv.get() == "/tmp/test"
        
        current_work_dir_cv.reset(token)
        assert current_work_dir_cv.get() == "./workspace"


class TestMiddlewareIntegration:
    """中间件集成测试"""

    def test_create_agent_with_skills_and_memory(self, default_work_dir):
        """测试 create_deep_agent 使用 skills 和 memory 参数"""
        from master.controller import CoreController
        from unittest.mock import MagicMock
        
        with patch('master.controller.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_get_llm.return_value = mock_llm
            
            with patch('master.controller.create_deep_agent') as mock_create_agent:
                mock_agent = MagicMock()
                mock_create_agent.return_value = mock_agent
                
                controller = CoreController(
                    uid="test_user",
                    default_work_dir=default_work_dir,
                )
                
                mock_create_agent.assert_called_once()
                
                call_kwargs = mock_create_agent.call_args.kwargs
                assert 'skills' in call_kwargs
                assert 'memory' in call_kwargs
                assert 'middleware' not in call_kwargs

    def test_backend_configuration(self, default_work_dir):
        """测试 Backend 配置"""
        from master.controller import CoreController
        from unittest.mock import MagicMock
        
        with patch('master.controller.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_get_llm.return_value = mock_llm
            
            with patch('master.controller.create_deep_agent') as mock_create_agent:
                mock_agent = MagicMock()
                mock_create_agent.return_value = mock_agent
                
                controller = CoreController(
                    uid="test_user",
                    default_work_dir=default_work_dir,
                )
                
                assert controller.default_work_dir == default_work_dir
