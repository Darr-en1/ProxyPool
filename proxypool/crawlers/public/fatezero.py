import json
import time

from proxypool.crawlers.base import BaseCrawler
from proxypool.schemas.proxy import Proxy

BASE_URL = "http://proxylist.fatezero.org/proxy.list"


class FatezeroCrawler(BaseCrawler):
    """
    Fatezero crawler,http://proxylist.fatezero.org
    """

    urls = [BASE_URL]

    def parse(self, html):
        """
        parse html file to get proxies
        :return:
        """

        hosts_ports = html.split("\n")
        proxy_list = []
        for addr in hosts_ports:
            if addr:
                ip_address = json.loads(addr)
                host = ip_address["host"]
                port = ip_address["port"]
                proxy_list.append(
                    Proxy(host=host, port=port, expire=int(time.time()) + 60 * 3)
                )
        return proxy_list
