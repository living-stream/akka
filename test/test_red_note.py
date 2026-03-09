import asyncio
import logging
import sys
import os

# Add current directory to path so we can import the new package
sys.path.append(os.getcwd())

from agentic_tool.note_generate_agent.agent import ainvoke

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    instruction ="云南的瑰夏和埃塞的瑰夏风味区别"
    output_path = "output/test_guixia"
    
    print(f"Starting test for instruction: {instruction}")
    result = await ainvoke(instruction, output_path)
    
    if result["status"] == "success":
        print("\nGeneration Successful!")
        print(f"Output Path: {result['output_path']}")
        print(f"Pages Generated: {result['pages_count']}")
        print(f"Primary Title: {result['titles'][0]}")
    else:
        print("\nGeneration Failed!")
        print(f"Error: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(main())
