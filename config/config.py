import os
import re
import yaml
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    provider: str = "openai"
    api_key: str | None = None
    base_url: str | None = None
    model: str = "gpt-4o"


class AgentBayConfig(BaseModel):
    api_key: str | None = None


class BrowserConfig(BaseModel):
    provider: str = "local"
    headless: bool = False
    disable_security: bool = True
    user_data_dir: str = "./browser_data"


class AgentConfig(BaseModel):
    max_steps: int = 60


class Config(BaseModel):
    llm: Optional[LLMConfig] = None
    agent_bay: Optional[AgentBayConfig] = None
    browser: Optional[BrowserConfig] = None
    agent: Optional[AgentConfig] = None
    newsapi: str | None = None

    def __init__(self, **data):
        super().__init__(**data)
        self._load_yaml_config()
        self._resolve_env_vars()
        self._apply_env_overrides()

    def _load_yaml_config(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        yaml_path = os.path.join(base_dir, "config.yaml")
        
        if not os.path.exists(yaml_path):
            example_path = os.path.join(os.path.dirname(base_dir), "config.example.yaml")
            if os.path.exists(example_path):
                yaml_path = example_path
            else:
                return
        
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)
                if not yaml_data:
                    return
                
                if "llm" in yaml_data:
                    self.llm = LLMConfig(**yaml_data["llm"])
                if "agent_bay" in yaml_data:
                    self.agent_bay = AgentBayConfig(**yaml_data["agent_bay"])
                if "browser" in yaml_data:
                    self.browser = BrowserConfig(**yaml_data["browser"])
                if "agent" in yaml_data:
                    self.agent = AgentConfig(**yaml_data["agent"])
                if "newsapi" in yaml_data:
                    self.newsapi = yaml_data["newsapi"]
        except Exception as e:
            print(f"Warning: Failed to load config.yaml: {e}")

    def _resolve_env_vars(self):
        pattern = re.compile(r'\$\{([^}]+)\}')
        
        def resolve_value(value):
            if isinstance(value, str):
                matches = pattern.findall(value)
                for match in matches:
                    env_value = os.getenv(match, "")
                    value = value.replace(f"${{{match}}}", env_value)
                return value if value else None
            return value
        
        if self.llm:
            self.llm.api_key = resolve_value(self.llm.api_key)
            self.llm.base_url = resolve_value(self.llm.base_url)
        
        if self.agent_bay:
            self.agent_bay.api_key = resolve_value(self.agent_bay.api_key)
        
        if self.newsapi:
            self.newsapi = resolve_value(self.newsapi)

    def _apply_env_overrides(self):
        if os.getenv("OPENAI_API_KEY"):
            if not self.llm:
                self.llm = LLMConfig()
            self.llm.api_key = os.getenv("OPENAI_API_KEY")
        
        if os.getenv("OPENAI_BASE_URL"):
            if not self.llm:
                self.llm = LLMConfig()
            self.llm.base_url = os.getenv("OPENAI_BASE_URL")
        
        if os.getenv("OPENAI_MODEL"):
            if not self.llm:
                self.llm = LLMConfig()
            self.llm.model = os.getenv("OPENAI_MODEL")
        
        if os.getenv("AGENTBAY_API_KEY"):
            if not self.agent_bay:
                self.agent_bay = AgentBayConfig()
            self.agent_bay.api_key = os.getenv("AGENTBAY_API_KEY")
        
        if os.getenv("NEWSAPI_KEY"):
            self.newsapi = os.getenv("NEWSAPI_KEY")

    @property
    def browser_provider(self) -> str:
        if self.browser:
            return self.browser.provider
        return os.getenv("BROWSER_PROVIDER", "local")

    @property
    def headless(self) -> bool:
        if self.browser:
            return self.browser.headless
        return os.getenv("BROWSER_HEADLESS", "false").lower() == "true"

    @property
    def disable_security(self) -> bool:
        if self.browser:
            return self.browser.disable_security
        return True

    @property
    def user_data_dir(self) -> str:
        if self.browser and self.browser.user_data_dir:
            return self.browser.user_data_dir
        return os.path.join(os.getcwd(), "browser_data")

    @property
    def max_steps(self) -> int:
        if self.agent:
            return self.agent.max_steps
        return int(os.getenv("MAX_STEPS", "60"))

    @property
    def cdp_port(self) -> int:
        return 9222

    @property
    def cdp_url(self) -> str:
        return f"http://127.0.0.1:{self.cdp_port}"

    def validate_browser_config(self):
        """验证浏览器配置的正确性"""
        provider = self.browser_provider
        
        if provider == "agent_bay":
            if not self.agent_bay or not self.agent_bay.api_key:
                raise ValueError(
                    "AgentBay API Key is required when browser.provider is 'agent_bay'. "
                    "Please set AGENTBAY_API_KEY environment variable or configure agent_bay.api_key in config.yaml"
                )
        elif provider == "local":
            pass
        else:
            raise ValueError(
                f"Invalid browser provider: {provider}. "
                "Valid options are: 'local' or 'agent_bay'"
            )


config = Config()
