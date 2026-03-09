import pytest
import asyncio


class TestNewsCrawler:
    """新闻爬取测试"""

    @pytest.mark.asyncio
    async def test_get_ai_news_real(self):
        """测试真实的 get_ai_news 工具"""
        import sys
        sys.path.insert(0, '/Users/misery/Documents/trae_projects/auto_ven')
        
        from master.controller import get_ai_news
        
        result = await get_ai_news.ainvoke({"count": 3, "topic": "AI"})
        
        print(f"\n获取新闻结果:\n{result}")
        
        assert "新闻" in result or "失败" in result
        assert "###" in result
        assert "来源" in result
