import uvicorn
from fastapi import FastAPI

from proxypool.setting import API_HOST, API_PORT, API_THREADED, IS_DEV
from proxypool.storages.redis import RedisClient

app = FastAPI()

if IS_DEV:
    app.debug = True


def build_conn():
    redis = None

    def inner():
        nonlocal redis
        if not redis:
            redis = RedisClient()
        return redis

    return inner


get_conn = build_conn()


@app.get('/ping')
async def index():
    """
    ping pong
    :return:
    """
    return 'pong'


@app.get('/random')
async def get_proxy():
    """
    get a random proxy
    :return: get a random proxy
    """
    conn = get_conn()
    proxy = await conn.random()
    return proxy.string()


@app.get('/all')
async def get_proxy_all():
    """
    get a random proxy
    :return: get a random proxy
    """
    conn = get_conn()
    proxies = await conn.all()
    return proxies


@app.get('/count')
async def get_count():
    """
    get the count of proxies
    :return: count, int
    """
    conn = get_conn()
    return int(await conn.count())


if __name__ == '__main__':
    uvicorn.run(app=app, host=API_HOST, port=API_PORT, reload=True, workers=API_THREADED)
