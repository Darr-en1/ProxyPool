import time
from random import choice
from typing import List

from loguru import logger
from redis.asyncio import ConnectionPool, Redis

from proxypool.exceptions import PoolEmptyException
from proxypool.schemas.proxy import Proxy
from proxypool.setting import REDIS_CONNECTION_STRING, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB, REDIS_KEY, \
    DEDUCTION_EXPIRATION_TIME
from proxypool.utils.proxy import is_valid_proxy, convert_proxies, convert_proxy


class RedisClient(object):
    """
    redis connection client of proxypool
    """

    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB,
                 connection_string=REDIS_CONNECTION_STRING, **kwargs):
        """
        init redis client
        :param host: redis host
        :param port: redis port
        :param password: redis password
        :param connection_string: redis connection_string
        """
        # if set connection_string, just use it
        if connection_string:
            pool = ConnectionPool.from_url(connection_string, decode_responses=True, **kwargs)

        else:
            pool = ConnectionPool(
                host=host, port=port, password=password, db=db, decode_responses=True, **kwargs)
        self.db: Redis = Redis(connection_pool=pool)

    async def add(self, proxy: Proxy, deduction=DEDUCTION_EXPIRATION_TIME) -> int:
        """
        add proxy and set it to init expire
        :param proxy: proxy, ip:port
        :param deduction: Deduction of expiration time
        :return:
            0 exist
            1 not exist
        """
        if not is_valid_proxy(f'{proxy.host}:{proxy.port}'):
            logger.info(f'invalid proxy {proxy}, throw it')
            return
        return await self.db.zadd(REDIS_KEY, {proxy.string(): proxy.expire - deduction})

    async def batch_add(self, proxy_list: List[Proxy], deduction=DEDUCTION_EXPIRATION_TIME) -> int:
        """
        batch add proxy and set it to init expire
        :param proxy_list: List[Proxy], ip:port
        :param deduction: Deduction of expiration time
        :return:
            0 all exist
            n  n do not exist
        """
        valid_proxy_list = []
        for proxy in proxy_list:
            if not is_valid_proxy(f'{proxy.host}:{proxy.port}'):
                logger.info(f'invalid proxy {proxy}, throw it')
            valid_proxy_list.append(proxy)
        if valid_proxy_list:
            return await self.db.zadd(REDIS_KEY,
                                      {proxy.string(): proxy.expire - deduction for proxy in valid_proxy_list})

    async def random(self) -> Proxy:
        """
        get random proxy
        firstly try to get proxy with max score
        if not exists, try to get proxy by rank
        if not exists, raise error
        :return: proxy, like 8.8.8.8:8
        """
        # try to get proxy with max score
        proxies = await self.db.zrangebyscore(REDIS_KEY, int(time.time()), '+inf', withscores=True)
        if len(proxies):
            return convert_proxy(choice(proxies))
        raise PoolEmptyException

    async def delete(self, proxy: Proxy) -> int:
        """
        delete proxy, if small
        :param proxy: proxy
        :return: new score
        """
        logger.info(f'{proxy.string()} remove')
        await self.db.zrem(REDIS_KEY, proxy.string())

    async def exists(self, proxy: Proxy) -> bool:
        """
        if proxy exists
        :param proxy: proxy
        :return: if exists, bool
        """
        return not await self.db.zscore(REDIS_KEY, proxy.string()) is None

    async def count(self) -> int:
        """
        get count of proxies
        :return: count, int
        """
        return await self.db.zcount(REDIS_KEY, int(time.time()), '+inf')

    async def all(self) -> List[Proxy]:
        """
        get all proxies
        :return: list of proxies
        """
        data = await self.db.zrangebyscore(REDIS_KEY, int(time.time()), '+inf', withscores=True)
        return convert_proxies(data)