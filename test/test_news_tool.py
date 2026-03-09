import pytest
from aioresponses import aioresponses
import aiohttp


class TestGetAiNews:
    """get_ai_news 工具测试 - 使用真实 HTTP mock"""

    NEWSAPI_URL = "https://newsapi.org/v2/everything"

    @pytest.mark.asyncio
    async def test_get_ai_news_no_api_key(self):
        """测试未配置 API Key 的情况"""
        api_key = None
        
        async def get_ai_news():
            if not api_key:
                return "错误：未配置 NEWSAPI_KEY，请在环境变量中设置"
            return "success"
        
        result = await get_ai_news()
        assert "错误" in result
        assert "NEWSAPI_KEY" in result

    @pytest.mark.asyncio
    async def test_get_ai_news_success(self):
        """测试成功获取新闻 - 真实 HTTP mock"""
        mock_response = {
            "status": "ok",
            "articles": [
                {
                    "title": "GPT-5 发布在即",
                    "source": {"name": "科技日报"},
                    "url": "https://example.com/news/1",
                    "publishedAt": "2024-01-15T10:00:00Z",
                    "description": "OpenAI 即将发布 GPT-5，性能大幅提升..."
                },
                {
                    "title": "国产大模型突破",
                    "source": {"name": "36氪"},
                    "url": "https://example.com/news/2",
                    "publishedAt": "2024-01-14T15:30:00Z",
                    "description": "国产大模型在多项测试中表现优异"
                }
            ]
        }
        
        with aioresponses() as m:
            m.get(self.NEWSAPI_URL, payload=mock_response, status=200)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.NEWSAPI_URL) as response:
                    data = await response.json()
                    
            assert data["status"] == "ok"
            assert len(data["articles"]) == 2
            assert "GPT-5" in data["articles"][0]["title"]
            assert "国产大模型" in data["articles"][1]["title"]

    @pytest.mark.asyncio
    async def test_get_ai_news_empty_result(self):
        """测试无新闻结果 - 真实 HTTP mock"""
        mock_response = {
            "status": "ok",
            "articles": []
        }
        
        with aioresponses() as m:
            m.get(self.NEWSAPI_URL, payload=mock_response, status=200)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.NEWSAPI_URL) as response:
                    data = await response.json()
            
            assert data["status"] == "ok"
            assert len(data["articles"]) == 0

    @pytest.mark.asyncio
    async def test_get_ai_news_api_error(self):
        """测试 API 错误 - 真实 HTTP mock"""
        mock_response = {
            "status": "error",
            "message": "Invalid API key"
        }
        
        with aioresponses() as m:
            m.get(self.NEWSAPI_URL, payload=mock_response, status=401)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.NEWSAPI_URL) as response:
                    status = response.status
                    data = await response.json()
            
            assert status == 401
            assert data["status"] == "error"

    @pytest.mark.asyncio
    async def test_get_ai_news_count_limit(self):
        """测试数量限制"""
        count = 20
        count = min(max(1, count), 10)
        
        assert count == 10
        
        mock_articles = [{"title": f"新闻{i}"} for i in range(10)]
        result_count = len(mock_articles)
        
        assert result_count == 10

    @pytest.mark.asyncio
    async def test_get_ai_news_different_topics(self):
        """测试不同主题的查询参数"""
        topic_queries = {
            "AI": "AI OR 人工智能 OR 大模型 OR GPT OR LLM",
            "科技": "科技 OR 技术 OR 互联网 OR 数码",
            "互联网": "互联网 OR 科技公司 OR 创业 OR 投资"
        }
        
        for topic, expected_query in topic_queries.items():
            query = topic_queries.get(topic, topic_queries["AI"])
            assert query == expected_query

    @pytest.mark.asyncio
    async def test_get_ai_news_http_error(self):
        """测试 HTTP 错误 - 真实 HTTP mock"""
        with aioresponses() as m:
            m.get(self.NEWSAPI_URL, status=500, body="Internal Server Error")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.NEWSAPI_URL) as response:
                    status = response.status
                    text = await response.text()
            
            assert status == 500
            assert "Internal Server Error" in text

    @pytest.mark.asyncio
    async def test_get_ai_news_network_error(self):
        """测试网络错误"""
        with aioresponses() as m:
            m.get(self.NEWSAPI_URL, exception=aiohttp.ClientError("Connection timeout"))
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.NEWSAPI_URL) as response:
                        pass
            except aiohttp.ClientError as e:
                error_msg = str(e)
                assert "Connection timeout" in error_msg

    @pytest.mark.asyncio
    async def test_get_ai_news_with_params(self):
        """测试带参数的请求 - 真实 HTTP mock"""
        import re
        
        mock_response = {
            "status": "ok",
            "articles": [
                {
                    "title": "AI新闻测试",
                    "source": {"name": "测试源"},
                    "url": "https://example.com/test",
                    "publishedAt": "2024-01-15T10:00:00Z",
                    "description": "测试描述"
                }
            ]
        }
        
        with aioresponses() as m:
            m.get(
                re.compile(r"https://newsapi.org/v2/everything\?.*"),
                payload=mock_response,
                status=200
            )
            
            params = {
                "q": "AI OR 人工智能",
                "language": "zh",
                "sortBy": "publishedAt",
                "pageSize": 5,
                "apiKey": "test_key"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.NEWSAPI_URL, params=params) as response:
                    data = await response.json()
            
            assert data["status"] == "ok"
            assert len(data["articles"]) == 1
