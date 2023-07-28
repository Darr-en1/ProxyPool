# ProxyPool

该项目主要针对企业级代理池设计实现，基于 [https://github.com/Python3WebSpider/ProxyPool](https://github.com/Python3WebSpider/ProxyPool)，作者  [崔庆才](https://cuiqingcai.com/) ，是我非常喜欢的一个技术大拿，他所著作的书籍《python3网络爬虫》真的既详细又有深度，非常推荐。

该项目源码地址：[https://github.com/Darr-en1/ProxyPool](https://github.com/Darr-en1/ProxyPool)

项目文章: [代理池构建](http://darr-en1.top/)

**项目优势：**

- **项目对原有项目进行了重构，使用async异步编程，引入fastapi，整个服务的性能得到显著提升**
- **依赖管理使用poetry，可以管理直接依賴和间接依赖，可以区分多环境依赖**
- **通过black、isort、mypy实现严格的代码规范，保证统一的代码风格，并通过pre-commit确保代码的质量和一致性**

## 功能

简易高效的代理池，提供如下功能：

- 定时抓取代理，简易可扩展。
- 使用 Redis 对代理进行存储并记录过期时间。
- 定时测试和筛选，剔除不可用代理，留下可用代理。
- 提供代理 API，随机取用测试通过的可用代理。

## 运行

### 环境

常规方式要求有 Python 环境、Redis 环境，具体要求如下：

- Python>=3.11
- Redis

然后 pip 安装依赖即可：

```shell script
pip install -r requirements.txt
```

### 配置redis

设置 Redis 的环境变量有两种方式，一种是分别设置 host、port、password，另一种是设置连接字符串，设置方法分别如下：

设置 host、port、password，如果 password 为空可以设置为空字符串，示例如下：

```shell
export PROXYPOOL_REDIS_HOST='localhost'
export PROXYPOOL_REDIS_PORT=6379
export PROXYPOOL_REDIS_PASSWORD=''
export PROXYPOOL_REDIS_DB=0
```

或者只设置连接字符串：

```shell
export PROXYPOOL_REDIS_CONNECTION_STRING='redis://localhost'
```

###  项目执行

查看执行命令

```shell script
python run.py  -h
```

运行结果类似如下：

```
Usage: run.py [OPTIONS] COMMAND [ARGS]...

  enter

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  run-getter  run getter 获取代理
  run-server  run server for api 启动代理服务器
  run-tester  run tester 测试代理可用性
```

三个服务分别是

- Getter：代理获取模块
- Server：代理服务器
- Tester：代理检测模块

这时候访问 [http://0.0.0.0:5555/docs#/](http://0.0.0.0:5555/docs#/) 即查看API详情。

## 使用

成功运行之后可以通过 [http://localhost:5555/random](http://localhost:5555/random) 获取一个随机可用代理。

可以用程序对接实现，下面的示例展示了获取代理并爬取网页的过程：

```python
import requests

proxypool_url = 'http://127.0.0.1:5555/random'
target_url = 'http://httpbin.org/get'


def get_random_proxy():
    """
    get random proxy from proxypool
    :return: proxy
    """
    return requests.get(proxypool_url).text.strip()


def crawl(url, proxy):
    """
    use proxy to crawl page
    :param url: page url
    :param proxy: proxy, such as 8.8.8.8:8888
    :return: html
    """
    proxies = {'http': 'http://' + proxy}
    return requests.get(url, proxies=proxies).text


def main():
    """
    main method, entry point
    :return: none
    """
    proxy = get_random_proxy()
    print('get random proxy', proxy)
    html = crawl(target_url, proxy)
    print(html)


if __name__ == '__main__':
    main()
```

运行结果如下：

```
get random proxy 116.196.115.209:8080
{
  "args": {},
  "headers": {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Host": "httpbin.org",
    "User-Agent": "python-requests/2.22.0",
    "X-Amzn-Trace-Id": "Root=1-5e4d7140-662d9053c0a2e513c7278364"
  },
  "origin": "116.196.115.209",
  "url": "https://httpbin.org/get"
}
```

可以看到成功获取了代理，并请求 httpbin.org 验证了代理的可用性。

## 可配置项

代理池可以通过设置环境变量来配置一些参数。

### 开关

- ENABLE_TESTER：允许 Tester 启动，默认 true
- ENABLE_GETTER：允许 Getter 启动，默认 true
- ENABLE_SERVER：运行 Server 启动，默认 true

### 环境

- APP_ENV：运行环境，可以设置 dev、test、prod，即开发、测试、生产环境，默认 dev

### Redis 连接

- PROXYPOOL_REDIS_HOST / REDIS_HOST：Redis 的 Host，其中 PROXYPOOL_REDIS_HOST 会覆盖 REDIS_HOST 的值。
- PROXYPOOL_REDIS_PORT / REDIS_PORT：Redis 的端口，其中 PROXYPOOL_REDIS_PORT 会覆盖 REDIS_PORT 的值。
- PROXYPOOL_REDIS_PASSWORD / REDIS_PASSWORD：Redis 的密码，其中 PROXYPOOL_REDIS_PASSWORD 会覆盖 REDIS_PASSWORD 的值。
- PROXYPOOL_REDIS_DB / REDIS_DB：Redis 的数据库索引，如 0、1，其中 PROXYPOOL_REDIS_DB 会覆盖 REDIS_DB 的值。
- PROXYPOOL_REDIS_CONNECTION_STRING / REDIS_CONNECTION_STRING：Redis 连接字符串，其中 PROXYPOOL_REDIS_CONNECTION_STRING 会覆盖
  REDIS_CONNECTION_STRING 的值。
- PROXYPOOL_REDIS_KEY / REDIS_KEY：Redis 储存代理使用字典的名称，其中 PROXYPOOL_REDIS_KEY 会覆盖 REDIS_KEY 的值。

### 处理器

- CYCLE_TESTER：Tester 运行周期，即间隔多久运行一次测试，默认 20 秒
- CYCLE_GETTER：Getter 运行周期，即间隔多久运行一次代理获取，默认 100 秒
- TEST_URL：测试 URL，默认百度
- TEST_TIMEOUT：测试超时时间，默认 10 秒
- TEST_VALID_STATUS：测试有效的状态码
- MAX_WORKERS：批量测试数量，默认 20 个代理
- API_HOST：代理 Server 运行 Host，默认 0.0.0.0
- API_PORT：代理 Server 运行端口，默认 5555
- API_THREADED：代理 Server 是否使用协程并发，默认 true

### 日志

- LOG_DIR：日志相对路径
- LOG_RUNTIME_FILE：运行日志文件名称
- LOG_ERROR_FILE：错误日志文件名称
- LOG_ROTATION: 日志记录周转周期或大小，默认
  500MB，见 [loguru - rotation](https://github.com/Delgan/loguru#easier-file-logging-with-rotation--retention--compression)
- LOG_RETENTION: 日志保留日期，默认 7
  天，见 [loguru - retention](https://github.com/Delgan/loguru#easier-file-logging-with-rotation--retention--compression)
- ENABLE_LOG_FILE：是否输出 log 文件，默认 true，如果设置为 false，那么 ENABLE_LOG_RUNTIME_FILE 和 ENABLE_LOG_ERROR_FILE 都不会生效
- ENABLE_LOG_RUNTIME_FILE：是否输出 runtime log 文件，默认 true
- ENABLE_LOG_ERROR_FILE：是否输出 error log 文件，默认 true

### 请求参数
- RAISE_FOR_STATUS：请求失败是否抛异常
- RETRIES：重试次数
- RETRY_OPTION：重试间隔停顿方式


以上内容均可使用环境变量配置，即在运行前设置对应环境变量值即可，如更改测试地址和 Redis 键名：

## 扩展代理爬虫

代理的爬虫均放置在 proxypool/crawlers 文件夹下。

若扩展一个爬虫，只需要在 crawlers 文件夹下新建一个 Python 文件声明一个 Class 即可。

在这里只需要定义一个 Crawler 继承 BaseCrawler 即可，然后定义好 urls 变量和 parse 方法即可。

- urls 变量即为爬取的代理网站网址列表，可以用程序定义也可写成固定内容。
- parse 方法接收一个参数即 html，代理网址的 html，在 parse 方法里只需要写好 html 的解析，解析出 host 和 port，并构建 Proxy 对象返回即可。

网页的爬取不需要实现，BaseCrawler 已经有了默认实现，如需更改爬取方式，重写 crawl 方法即可。
