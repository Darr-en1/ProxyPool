import asyncio
import logging
from typing import List

from aiohttp_retry import RetryClient
from fake_headers import Headers
from loguru import logger
from tenacity import before_log, retry, stop_after_attempt, wait_random

from proxypool.schemas import Proxy
from proxypool.setting import GET_TIMEOUT, RAISE_FOR_STATUS, RETRIES, RETRY_OPTION


class BaseCrawler:
    urls: List[str] = []

    # reraise True 返回原本异常
    @retry(
        stop=stop_after_attempt(RETRIES),
        reraise=True,
        wait=wait_random(min=1, max=3),
        before=before_log(logger, logging.DEBUG),
    )
    async def fetch(self, url, **kwargs):
        headers = Headers(headers=True).generate()
        kwargs.setdefault("timeout", GET_TIMEOUT)
        kwargs.setdefault("verify_ssl", False)
        kwargs.setdefault("headers", headers)
        async with RetryClient(
            raise_for_status=RAISE_FOR_STATUS, retry_options=RETRY_OPTION
        ) as client:
            async with client.get(url=url, **kwargs) as response:
                if response.status == 200:
                    return await response.text()

    def start_urls(self):
        return self.urls

    def parse(self, html: str) -> List[Proxy]:
        raise NotImplementedError

    def process(self, html: str) -> List[Proxy]:
        """
        used for parse html
        """
        return self.parse(html)

    async def crawl(self, url):
        """
        crawl main method
        """
        try:
            logger.info(f"fetching {url}")
            html = await self.fetch(url)
            if not html:
                return []
            proxy_list = self.process(html)
            logger.info(f"fetched proxy {proxy_list} from {url}")
            return proxy_list
        except asyncio.exceptions.TimeoutError:
            logger.error(
                f"crawler {self} crawled proxy unsuccessfully, "
                "please check if target url is valid or network issue"
            )
            return []

    def __aiter__(self):
        self.crawl_cursor = 0
        return self

    async def __anext__(self) -> List[Proxy]:
        if len(self.urls) == 0:
            self.urls = self.start_urls()
        if len(self.urls) == self.crawl_cursor:
            raise StopAsyncIteration
        url = self.urls[self.crawl_cursor]
        self.crawl_cursor += 1
        return await self.crawl(url)
