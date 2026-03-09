import pytest
import asyncio
import logging
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from master.controller import CoreController

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class TestCoreControllerInit:
    """控制器初始化测试"""

    def test_controller_init(self, default_work_dir):
        """测试控制器初始化"""
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
                
                assert controller.uid == "test_user"
                assert controller.default_work_dir == default_work_dir
                assert len(controller.tools) == 2

    def test_create_agent_parameters(self, default_work_dir):
        """测试 create_deep_agent 参数"""
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
                assert len(call_kwargs['skills']) == 1
                assert len(call_kwargs['memory']) == 1  # 只有 AGENTS.md

    def test_system_prompt_build(self, default_work_dir):
        """测试系统提示构建"""
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
                
                prompt = controller._build_base_system_prompt()
                
                assert default_work_dir in prompt
                assert "Soul" in prompt or "AlgoBarista" in prompt

    def test_tools_registration(self, default_work_dir):
        """测试工具注册"""
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
                
                tool_names = [t.name for t in controller.tools]
                assert "generate_note" in tool_names
                assert "use_browser" in tool_names


class TestCoreControllerRun:
    """控制器运行测试"""

    @pytest.mark.asyncio
    async def test_run_with_brief(self, default_work_dir):
        """测试运行 brief"""
        with patch('master.controller.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_get_llm.return_value = mock_llm
            
            with patch('master.controller.create_deep_agent') as mock_create_agent:
                mock_agent = MagicMock()
                
                async def mock_astream(*args, **kwargs):
                    yield {"model": {"messages": [MagicMock(content="Test response")]}}
                
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

    @pytest.mark.asyncio
    async def test_error_handling(self, default_work_dir):
        """测试错误处理"""
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

    @pytest.mark.asyncio
    async def test_close(self, default_work_dir):
        """测试关闭"""
        with patch('master.controller.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_get_llm.return_value = mock_llm
            
            with patch('master.controller.create_deep_agent') as mock_create_agent:
                mock_agent = MagicMock()
                mock_create_agent.return_value = mock_agent
                
                with patch('master.controller.BrowserManager') as mock_browser_manager:
                    mock_browser_instance = MagicMock()
                    mock_browser_instance.close = AsyncMock()
                    mock_browser_manager.get_instance.return_value = mock_browser_instance
                    
                    controller = CoreController(
                        uid="test_user",
                        default_work_dir=default_work_dir,
                    )
                    
                    await controller.close()
                    
                    mock_browser_instance.close.assert_called_once()


class TestTools:
    """工具测试"""

    @pytest.mark.asyncio
    async def test_generate_note_tool(self, default_work_dir):
        """测试 generate_note 工具"""
        from master.controller import generate_note, current_work_dir_cv
        
        current_work_dir_cv.set(default_work_dir)
        
        with patch('master.controller.note_ainvoke', new_callable=AsyncMock) as mock_note:
            mock_note.return_value = None
            
            result = await generate_note.ainvoke({
                "platform": "小红书",
                "instruction": "写一篇咖啡笔记",
            })
            
            assert "successfully" in result.lower() or "成功" in result

    @pytest.mark.asyncio
    async def test_use_browser_tool(self):
        """测试 use_browser 工具"""
        from master.controller import use_browser
        
        with patch('master.controller.BrowserManager') as mock_browser_manager:
            mock_instance = MagicMock()
            mock_wrapper = MagicMock()
            mock_wrapper.stop = AsyncMock()
            mock_instance.create_new_session = AsyncMock(return_value=(MagicMock(), mock_wrapper))
            mock_browser_manager.get_instance.return_value = mock_instance
            
            with patch('master.controller.ainvoke', new_callable=AsyncMock) as mock_ainvoke:
                mock_ainvoke.return_value = "Test result"
                
                result = await use_browser.ainvoke({
                    "instruction": "搜索咖啡",
                })
                
                assert "completed" in result.lower() or "完成" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
