from controller import CoreController
import asyncio

async def main():
    controller = CoreController()
    brief = "创作一篇关于'周末手冲咖啡时光'的笔记保存到 ./output/weekend_coffee，然后把它发布出去。"
    async for chunk in controller.run(brief):
        print(chunk)

if __name__ == "__main__":
    asyncio.run(main())
