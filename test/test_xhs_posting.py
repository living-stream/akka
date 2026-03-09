import asyncio
import logging
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from agentic_tool.browser_use_agent.agent import ainvoke

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    # Use the coffee post output path provided by user
    folder_path = "/Users/misery/Documents/trae_projects/auto_ven/output/test_guixia"
    task = "请使用提供的资源文件夹在小红书上发布一篇笔记。你需要完整执行所有操作：读取资源、上传图片、填写标题和正文、最后点击『发布』按钮。确认发布成功后告诉我。"
    
    print(f"Starting XHS FULL AUTO posting test with folder: {folder_path}")
    result = await ainvoke(task, folder_path=folder_path)
    
    print("\nTest Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
