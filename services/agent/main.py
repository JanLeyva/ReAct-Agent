from src.shared.llm.factory import llm
from src.services.agent.agent import RestaurantWorkflow
import asyncio


async def main():
    w = RestaurantWorkflow(timeout=10, llm=llm, verbose=False)
    result = await w.run(input="restaurants near the Sagrada Familia")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
