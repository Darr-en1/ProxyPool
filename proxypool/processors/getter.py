from typing import List, Type

from loguru import logger

from proxypool.crawlers import BaseCrawler, classes
from proxypool.setting import PROXY_NUMBER_MAX
from proxypool.storages.redis import RedisClient


class Getter:
    """
    getter of proxypool
    """

    def __init__(self):
        """
        init db and crawlers
        """
        self.redis = RedisClient()
        self.crawlers_cls = classes
        self.crawlers = [crawler_cls() for crawler_cls in self.crawlers_cls]

    async def is_full(self):
        """
        if proxypool if full
        return: bool
        """
        return await self.redis.count() >= PROXY_NUMBER_MAX

    @logger.catch
    async def run(self):
        """
        run crawlers to get proxy
        :return:
        """
        if await self.is_full():
            return
        for crawler in self.crawlers:
            logger.info(f"crawler {crawler} to get proxy")
            async for proxy_list in crawler:
                new_proxy_number = await self.redis.batch_add(proxy_list)
                logger.info(
                    f"batch_add {proxy_list=} number of new proxy: {new_proxy_number=}"
                )
