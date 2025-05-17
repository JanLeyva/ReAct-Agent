import asyncio
from crawl4ai import AsyncWebCrawler
import polars as pl
from loguru import logger

async def main(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
        )
        return result.markdown

if __name__ == "__main__":
    # read current data
    data = pl.read_parquet("/Users/janleyvamassague/Documents/agnostic-agent/docs/data/250515_places.parquet")
    # filter out rows with empty markdown
    logger.info(f"Scraping {len(data)} URLs")

    descriptions = []
    for url in data.select("website").iter_rows():

        if url[0]:
            url = url[0]
            logger.info(f"Scraping: {url}")
            # run the scraper
            try:
                result = asyncio.run(main(url))
            except Exception as e:
                logger.info(f"Error scraping {url}: {e}")
                continue

            # save the result
        else:
            result = None
        # save the result
        descriptions.append(result)
    
    data.insert_column(0, pl.Series("web_text", descriptions))
    data.write_parquet("web_text_places.parquet")
    breakpoint()
