import asyncio
import logging
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from master.controller import CoreController

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    # Allow overriding browser provider via env var
    browser_provider = "agent_bay"
    
    # uid is now required, work_dir is auto-created per user
    controller = CoreController(uid="test_user", browser_provider="agent_bay")
    
    print("\n" + "="*50)
    print("TEST: User Isolation + Conversation History")
    print("="*50)
    
    print(f"User directory: {controller.user_dir}")
    print(f"Working directory: {controller.default_work_dir}")
    
    brief = "帮我创建一个定时任务，明天12点发一篇关于手冲咖啡的帖子。"
    
    print(f"\nTesting Brief: {brief}")
    
    print("\nResult:")
    async for chunk in controller.run(brief):
        print(chunk, end="", flush=True)
    print("\n===================")

    # Cleanup
    await controller.close()

if __name__ == "__main__":
    asyncio.run(main())
