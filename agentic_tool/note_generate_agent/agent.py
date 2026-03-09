import os
import asyncio
import logging
from typing import Dict, Any

from .services.outline_service import OutlineService
from .services.content_service import ContentService
from .services.image_service import ImageService

logger = logging.getLogger(__name__)

async def ainvoke(instruction: str, output_path: str, platform: str = "小红书") -> Dict[str, Any]:
    """
    全自动生成图文帖子：大纲 -> 文案 -> 图片
    
    Args:
        instruction: 用户指令（例如："帮我写一个关于手冲咖啡入门的帖子"）
        output_path: 产出物的保存路径（相对路径）
        platform: 目标平台，默认为"小红书"
        
    Returns:
        包含生成结果信息的字典
    """
    try:
        # 0. 准备输出目录
        abs_output_path = os.path.abspath(output_path)
        os.makedirs(abs_output_path, exist_ok=True)
        logger.info(f"Starting Note generation for {platform} in: {abs_output_path}")

        # 初始化服务
        outline_svc = OutlineService()
        content_svc = ContentService()
        image_svc = ImageService()

        # 1. 生成大纲
        logger.info(f"Step 1: Generating outline for {platform}...")
        outline_result = await outline_svc.generate(instruction, platform=platform)
        outline_text = outline_result["outline_text"]
        pages = outline_result["pages"]
        
        # 保存大纲文件
        with open(os.path.join(abs_output_path, "outline.md"), "w", encoding="utf-8") as f:
            f.write(outline_text)
        logger.info("Outline saved to outline.md")

        # 2. 生成文案 (标题、正文、标签)
        logger.info(f"Step 2: Generating copywriting for {platform}...")
        content_result = await content_svc.generate(instruction, outline_text, platform=platform)
        
        # 保存文案文件
        copywriting_content = (
            "# 推荐标题\n" + "\n".join([f"- {t}" for t in content_result["titles"]]) + "\n\n"
            "# 正文文案\n" + content_result["copywriting"]
        )
        with open(os.path.join(abs_output_path, "copywriting.md"), "w", encoding="utf-8") as f:
            f.write(copywriting_content)
        logger.info("Copywriting saved to copywriting.md")

        # 3. 生成图片系列
        logger.info(f"Step 3: Generating image series for {platform}...")
        # 注意：这里会并发生成所有图片
        await image_svc.generate_series(pages, abs_output_path, instruction, platform=platform)
        logger.info("Image series generation finished.")

        return {
            "status": "success",
            "output_path": abs_output_path,
            "pages_count": len(pages),
            "titles": content_result["titles"]
        }

    except Exception as e:
        logger.error(f"Note generation failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
