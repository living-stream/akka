import os
import re
from pathlib import Path
from typing import List, Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from llm.factory import get_llm
from agentic_tool.browser_use_agent.context import current_uid_cv

class OutlineService:
    def __init__(self):
        self.llm = get_llm()
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            "outline_system.md"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            base_prompt = f.read()
        
        uid = current_uid_cv.get()
        if uid:
            project_root = Path(__file__).parent.parent.parent.parent
            soul_file = project_root / "users" / uid / "soul.md"
            if soul_file.exists():
                soul_content = soul_file.read_text(encoding="utf-8")
                base_prompt = f"{base_prompt}\n\n# 用户人设\n\n{soul_content}"
        
        return base_prompt

    def parse_outline(self, outline_text: str) -> List[Dict[str, Any]]:
        """Parse the outline text into structured pages."""
        # Split by <page> tag
        pages_raw = re.split(r'<page>', outline_text, flags=re.IGNORECASE)
        pages = []

        for index, page_text in enumerate(pages_raw):
            page_text = page_text.strip()
            if not page_text:
                continue

            # Default type
            page_type = "content"
            
            # Extract type from [Type]
            type_match = re.match(r"\[(.*?)\]", page_text)
            if type_match:
                type_cn = type_match.group(1).strip()
                type_mapping = {
                    "封面": "cover",
                    "内容": "content",
                    "总结": "summary",
                }
                page_type = type_mapping.get(type_cn, "content")
                # Remove the type tag from content if desired, 
                # but RedInk keeps it for better image generation context.

            pages.append({
                "index": index,
                "type": page_type,
                "content": page_text
            })

        return pages

    async def generate(self, instruction: str, platform: str = "小红书") -> Dict[str, Any]:
        """Generate outline using LLM."""
        # Inject platform into system prompt
        formatted_system_prompt = self.system_prompt.replace("{platform}", platform)
        
        human_prompt = f"用户的要求以及说明：{instruction}\n\n请直接输出大纲内容："
        
        messages = [
            SystemMessage(content=formatted_system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        if hasattr(response, 'content'):
            outline_text = response.content
        elif hasattr(response, 'completion'):
            outline_text = response.completion
        else:
            outline_text = str(response)
        
        pages = self.parse_outline(outline_text)
        
        return {
            "outline_text": outline_text,
            "pages": pages
        }
