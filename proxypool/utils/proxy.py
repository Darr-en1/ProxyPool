from proxypool.schemas import Proxy


def is_valid_proxy(data):
    """
    check this string is within proxy format
    """
    if data.__contains__(':'):
        ip = data.split(':')[0]
        port = data.split(':')[1]
        return is_ip_valid(ip) and is_port_valid(port)
    else:
        return is_ip_valid(data)


def is_ip_valid(ip):
    """
    check this string is within ip format
    """
    a = ip.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True


def is_port_valid(port):
    return port.isdigit()


def convert_proxies(data):
    """
    convert list of tuple(proxy,expire) to valid proxies
    :param data:
    :return:
    """
    if not data:
        return []
    result = []
    for proxy_tuple in data:
        if proxy := convert_proxy(proxy_tuple):
            result.append(proxy)
    return result


def convert_proxy(data):
    """
    convert tuple(proxy,expire) to valid proxy
    :param data:
    :return:
    """
    if not data:
        return
    (proxy, expire) = data
    # skip invalid item
    proxy = proxy.strip()
    if not is_valid_proxy(proxy):
        return
    host, port = proxy.split(':')
    return Proxy(host=host, port=int(port), expire=int(expire))
