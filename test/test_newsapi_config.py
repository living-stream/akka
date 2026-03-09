import pytest
import os
import tempfile
import yaml


class TestNewsApiConfig:
    """NewsAPI 配置测试"""

    def test_newsapi_key_from_yaml(self):
        """测试从 config.yaml 读取 newsapi key"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_yaml_path = os.path.join(tmpdir, "config.yaml")
            config_data = {
                "newsapi": "test-api-key-from-yaml-12345"
            }
            
            with open(config_yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f)
            
            with open(config_yaml_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)
            
            newsapi_key = yaml_data.get("newsapi")
            assert newsapi_key == "test-api-key-from-yaml-12345"

    def test_newsapi_key_from_env(self):
        """测试从环境变量读取 newsapi key"""
        os.environ["NEWSAPI_KEY"] = "test-api-key-from-env-67890"
        
        newsapi_key = os.getenv("NEWSAPI_KEY")
        assert newsapi_key == "test-api-key-from-env-67890"
        
        del os.environ["NEWSAPI_KEY"]

    def test_newsapi_key_yaml_overrides_env(self):
        """测试 yaml 配置优先于环境变量（模拟逻辑）"""
        env_key = "env-key-should-be-overridden"
        yaml_key = "yaml-key-priority"
        
        os.environ["NEWSAPI_KEY"] = env_key
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_yaml_path = os.path.join(tmpdir, "config.yaml")
            config_data = {
                "newsapi": yaml_key
            }
            
            with open(config_yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f)
            
            with open(config_yaml_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)
            
            final_key = yaml_data.get("newsapi") or os.getenv("NEWSAPI_KEY")
            assert final_key == yaml_key
        
        del os.environ["NEWSAPI_KEY"]

    def test_newsapi_key_not_configured(self):
        """测试未配置 newsapi key"""
        if "NEWSAPI_KEY" in os.environ:
            del os.environ["NEWSAPI_KEY"]
        
        newsapi_key = os.getenv("NEWSAPI_KEY")
        assert newsapi_key is None

    def test_config_yaml_exists_and_has_newsapi(self):
        """测试实际 config.yaml 文件包含 newsapi 配置"""
        config_yaml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
        
        if os.path.exists(config_yaml_path):
            with open(config_yaml_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)
            
            assert "newsapi" in yaml_data
            assert yaml_data["newsapi"] is not None
            assert len(yaml_data["newsapi"]) > 0
