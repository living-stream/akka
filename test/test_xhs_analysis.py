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
    task = "分析我的账号运营情况，并对比同赛道的 2-3 个热门账号，最后给我一份详细的诊断报告和改进意见。"
    
    print(f"Starting XHS Comprehensive Analysis test...")
    result = await ainvoke(task)
    
    print("\nAnalysis Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
