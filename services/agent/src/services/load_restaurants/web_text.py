# 3rd party
from crawl4ai import AsyncWebCrawler


async def scrap_url(url: str) -> str:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
        )
        return result.markdown
