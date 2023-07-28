import asyncio

import click
import uvicorn
from loguru import logger

from proxypool.processors.getter import Getter
from proxypool.processors.tester import Tester
from proxypool.setting import (
    API_HOST,
    API_PORT,
    APP_DEBUG,
    CYCLE_GETTER,
    CYCLE_TESTER,
    ENABLE_GETTER,
    ENABLE_SERVER,
    ENABLE_TESTER,
    IS_PROD,
    WORKERS,
)

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version="1.0.0")
def cli():
    """
    enter
    """
    pass


@cli.command()
@click.option(
    "--cycle",
    default=CYCLE_TESTER,
    required=True,
    type=click.IntRange(10, 30),
    help="Tester 运行周期，即间隔多久运行一次测试",
    show_default=True,
)
def run_tester(cycle):
    """
    run tester
    测试代理可用性
    """
    if not ENABLE_TESTER:
        logger.info("tester not enabled, exit")
        return
    tester = Tester()

    async def inner():
        loop = 0
        while True:
            logger.debug(f"getter loop {loop} start...")
            await tester.run()
            loop += 1
            await asyncio.sleep(cycle)

    asyncio.run(inner())


@cli.command()
@click.option(
    "--cycle",
    default=CYCLE_GETTER,
    required=True,
    type=click.IntRange(30, 180),
    help="Getter 运行周期，即间隔多久运行一次代理获取",
    show_default=True,
)
def run_getter(cycle):
    """
    run getter
    获取代理
    """
    if not ENABLE_GETTER:
        logger.info("getter not enabled, exit")
        return
    getter = Getter()

    async def inner():
        loop = 0
        while True:
            logger.debug(f"getter loop {loop} start...")
            await getter.run()
            loop += 1
            await asyncio.sleep(cycle)

    asyncio.run(inner())


@cli.command()
def run_server():
    """
    run server for api
    启动代理服务器
    """
    if not ENABLE_SERVER:
        logger.info("server not enabled, exit")
        return
    if IS_PROD:
        uvicorn.run(
            "proxypool.processors.server:app",
            host=API_HOST,
            port=API_PORT,
            workers=WORKERS,
        )
    else:
        uvicorn.run(
            app="proxypool.processors.server:app",
            host=API_HOST,
            port=API_PORT,
            reload=APP_DEBUG,
        )
