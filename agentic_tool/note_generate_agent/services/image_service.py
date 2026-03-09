import os
import httpx
import asyncio
import json
import re
import logging
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from llm.factory import gen_picture, get_llm

logger = logging.getLogger(__name__)

class ImageService:
    def __init__(self):
        self.system_prompt = self._load_system_prompt()
        self.prompt_converter_prompt = self._load_prompt_converter_prompt()
        self.converter_llm = get_llm()

    def _load_system_prompt(self) -> str:
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            "image_system.md"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _load_prompt_converter_prompt(self) -> str:
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            "image_prompt_system.md"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    async def _download_and_save(self, url: str, filepath: str) -> bool:
        """Download image from URL and save to local path."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    return True
                else:
                    logger.error(f"Failed to download image: {response.status_code}")
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
        return False

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
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

    async def _convert_to_image_prompt(self, page: Dict[str, Any], instruction: str, platform: str) -> Dict[str, Any]:
        """Convert page content to structured image prompt using LLM."""
        page_content = page["content"]
        page_type = page["type"]
        
        human_prompt = f"""请将以下页面内容转换为结构化的生图指令：

平台：{platform}
页面类型：{page_type}
用户原始需求：{instruction}

页面内容：
{page_content}

请严格按照 JSON 格式输出："""

        messages = [
            SystemMessage(content=self.prompt_converter_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = await self.converter_llm.ainvoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            prompt_data = self._parse_json_response(response_text)
            
            if prompt_data:
                logger.info(f"Successfully converted prompt for page {page['index']}")
                return prompt_data
            else:
                logger.warning(f"Failed to parse JSON, using raw content")
                return {"raw_content": page_content}
                
        except Exception as e:
            logger.error(f"Error converting prompt: {e}")
            return {"raw_content": page_content}

    def _build_final_prompt(self, prompt_data: Dict[str, Any], platform: str) -> str:
        """Build final prompt string for image generation model."""
        if "raw_content" in prompt_data:
            return prompt_data["raw_content"]
        
        parts = []
        
        if "image_text" in prompt_data:
            text_info = prompt_data["image_text"]
            parts.append("【图片文字内容】")
            if text_info.get("title"):
                parts.append(f"标题：{text_info['title']}")
            if text_info.get("subtitle"):
                parts.append(f"副标题：{text_info['subtitle']}")
            if text_info.get("body"):
                parts.append("正文：")
                for line in text_info["body"]:
                    parts.append(f"  - {line}")
            if text_info.get("highlight"):
                parts.append(f"重点：{text_info['highlight']}")
        
        if "background" in prompt_data:
            parts.append(f"\n【背景场景】{prompt_data['background']}")
        
        if "style" in prompt_data:
            style = prompt_data["style"]
            parts.append("\n【风格要求】")
            if style.get("type"):
                parts.append(f"风格类型：{style['type']}")
            if style.get("color_tone"):
                parts.append(f"色调：{style['color_tone']}")
            if style.get("atmosphere"):
                parts.append(f"氛围：{style['atmosphere']}")
            if style.get("aspect_ratio"):
                parts.append(f"比例：{style['aspect_ratio']}")
        
        if "composition" in prompt_data:
            parts.append(f"\n【构图】{prompt_data['composition']}")
        
        if "negative_prompt" in prompt_data:
            parts.append(f"\n【避免元素】{prompt_data['negative_prompt']}")
        
        parts.append(f"\n请生成一张符合{platform}风格的精美图片。")
        
        return "\n".join(parts)

    async def generate_and_save(self, page: Dict[str, Any], output_dir: str, instruction: str, platform: str = "小红书"):
        """Generate one image and save it."""
        page_type = page["type"]
        index = page["index"]
        
        try:
            logger.info(f"Step 1: Converting prompt for page {index} ({page_type})...")
            prompt_data = await self._convert_to_image_prompt(page, instruction, platform)
            
            final_prompt = self._build_final_prompt(prompt_data, platform)
            logger.info(f"Step 2: Generating image for page {index}...")
            logger.debug(f"Final prompt: {final_prompt[:200]}...")
            
            image_url = await gen_picture(final_prompt)
            
            if image_url:
                filename = f"{index}.png"
                filepath = os.path.join(output_dir, filename)
                
                success = await self._download_and_save(image_url, filepath)
                if success:
                    logger.info(f"Successfully saved image {index} to {filepath}")
                    return True
        except Exception as e:
            logger.error(f"Error generating image {index}: {e}")
        
        return False

    async def generate_series(self, pages: List[Dict[str, Any]], output_path: str, instruction: str, platform: str = "小红书"):
        """Generate all images for the post."""
        images_dir = os.path.join(output_path, "images")
        os.makedirs(images_dir, exist_ok=True)
        
        tasks = [self.generate_and_save(page, images_dir, instruction, platform=platform) for page in pages]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for r in results if r)
        logger.info(f"Image generation completed: {success_count}/{len(pages)} successful.")
        return results
