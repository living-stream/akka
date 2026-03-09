"""测试 browser_steps ContextVar 传递"""
import pytest
import asyncio
import contextvars
from agentic_tool.browser_use_agent.context import browser_steps_cv


@pytest.mark.asyncio
async def test_browser_steps_contextvar():
    """测试 browser_steps_cv 在异步上下文中的传递"""
    
    browser_steps_cv.set([])
    
    ctx = contextvars.copy_context()
    
    def update_steps_in_context():
        steps = browser_steps_cv.get() or []
        steps.append({"step": 1, "goal": "test"})
        browser_steps_cv.set(steps)
        return steps
    
    result = ctx.run(update_steps_in_context)
    
    assert len(result) == 1
    assert result[0]["step"] == 1
    
    steps_after = browser_steps_cv.get()
    assert steps_after == []
    
    browser_steps_cv.set(result)
    steps_final = browser_steps_cv.get()
    assert len(steps_final) == 1


@pytest.mark.asyncio
async def test_browser_steps_multiple_updates():
    """测试多次更新 browser_steps_cv"""
    
    browser_steps_cv.set([])
    ctx = contextvars.copy_context()
    
    def add_step(step_num, goal):
        steps = browser_steps_cv.get() or []
        steps.append({"step": step_num, "goal": goal})
        browser_steps_cv.set(steps)
        return steps
    
    ctx.run(add_step, 1, "first")
    ctx.run(add_step, 2, "second")
    ctx.run(add_step, 3, "third")
    
    final_steps = ctx.run(browser_steps_cv.get)
    assert len(final_steps) == 3
    assert final_steps[0]["step"] == 1
    assert final_steps[2]["goal"] == "third"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
