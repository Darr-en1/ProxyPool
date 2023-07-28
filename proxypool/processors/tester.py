import asyncio
from asyncio import TimeoutError

import aiohttp
from aiohttp import (
    ClientHttpProxyError,
    ClientOSError,
    ClientProxyConnectionError,
    ServerDisconnectedError,
)
from loguru import logger

from proxypool.schemas import Proxy
from proxypool.setting import (
    MAX_WORKERS,
    TEST_ANONYMOUS,
    TEST_TIMEOUT,
    TEST_URL,
    TEST_VALID_STATUS,
)
from proxypool.storages.redis import RedisClient

EXCEPTIONS = (
    ClientProxyConnectionError,
    ConnectionRefusedError,
    TimeoutError,
    ServerDisconnectedError,
    ClientOSError,
    ClientHttpProxyError,
    AssertionError,
)


class Tester:
    """
    tester for testing proxies in queue
    """

    def __init__(self):
        """
        init redis
        """
        self.redis = RedisClient()
        self.loop = asyncio.get_event_loop()

    async def test(self, proxy: Proxy, sem: asyncio.Semaphore) -> None:
        """
        test single proxy
        :param proxy: Proxy object
        :return:
        """
        async with sem:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                try:
                    logger.debug(f"testing {proxy.string()}")
                    # if TEST_ANONYMOUS is True, make sure that
                    # the proxy has the effect of hiding the real IP
                    if TEST_ANONYMOUS:
                        url = "https://httpbin.org/ip"
                        async with session.get(url, timeout=TEST_TIMEOUT) as response:
                            resp_json = await response.json()
                            origin_ip = resp_json["origin"]
                        async with session.get(
                            url, proxy=f"http://{proxy.string()}", timeout=TEST_TIMEOUT
                        ) as response:
                            resp_json = await response.json()
                            anonymous_ip = resp_json["origin"]
                        assert origin_ip != anonymous_ip
                        assert proxy.host == anonymous_ip
                    async with session.get(
                        TEST_URL,
                        proxy=f"http://{proxy.string()}",
                        timeout=TEST_TIMEOUT,
                        allow_redirects=False,
                    ) as response:
                        if response.status in TEST_VALID_STATUS:
                            logger.debug(f"proxy {proxy.string()} is valid")
                        else:
                            await self.redis.delete(proxy)
                            logger.debug(f"proxy {proxy.string()} is invalid, delete")
                except EXCEPTIONS:
                    await self.redis.delete(proxy)
                    logger.debug(f"proxy {proxy.string()} is invalid, delete")

    @logger.catch
    async def run(self):
        """
        test main method
        :return:
        """
        # event loop of aiohttp
        logger.info("stating tester...")
        semaphore = asyncio.Semaphore(MAX_WORKERS)
        proxies = await self.redis.all()
        logger.debug(f"testing proxies , count {len(proxies)}")
        if proxies:
            tasks = [
                asyncio.create_task(self.test(proxy, semaphore)) for proxy in proxies
            ]
            await asyncio.wait(tasks)

        await self.redis.expired_delete()
