import json
import re
from pathlib import Path
from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from llm.factory import get_llm
from agentic_tool.browser_use_agent.context import current_uid_cv

from agentic_tool.note_generate_agent.prompts.content_system import CONTENT_SYSTEM_PROMPT


class ContentService:
    def __init__(self):
        self.llm = get_llm()
        self._base_prompt = CONTENT_SYSTEM_PROMPT
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        base_prompt = self._base_prompt
        uid = current_uid_cv.get()
        if uid:
            project_root = Path(__file__).parent.parent.parent.parent
            soul_file = project_root / "users" / uid / "soul.md"
            if soul_file.exists():
                soul_content = soul_file.read_text(encoding="utf-8")
                base_prompt = f"{base_prompt}\n\n# 用户人设\n\n{soul_content}"
        return base_prompt

    def _parse_json(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            match = re.search(r'(\{[\s\S]*\})', text)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
        return {}

    async def generate(self, instruction: str, outline_text: str, platform: str = "小红书") -> Dict[str, Any]:
        formatted_system_prompt = self.system_prompt.replace("{platform}", platform)
        
        human_prompt = (
            f"用户主题：{instruction}\n\n"
            f"内容大纲：\n{outline_text}\n\n"
            "请严格按照要求的 JSON 格式输出文案："
        )
        
        messages = [
            SystemMessage(content=formatted_system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        if hasattr(response, 'content'):
            response_text = response.content
        elif hasattr(response, 'completion'):
            response_text = response.completion
        else:
            response_text = str(response)
        
        content_data = self._parse_json(response_text)
        
        titles = content_data.get("titles", [])
        if platform == "小红书":
            titles = [self._validate_xiaohongshu_title(t) for t in titles]
        
        return {
            "titles": titles,
            "copywriting": content_data.get("copywriting", ""),
        }

    def _validate_xiaohongshu_title(self, title: str) -> str:
        if len(title) > 20:
            return title[:20]
        return title
