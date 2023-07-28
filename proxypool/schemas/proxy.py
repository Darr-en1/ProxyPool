from attr import attr, attrs


@attrs
class Proxy(object):
    """
    proxy schema
    """

    host = attr(type=str, default=None)
    port = attr(type=int, default=None)
    expire = attr(type=int, default=None)

    def __str__(self):
        """
        to string, for print
        :return:
        """
        return f"{self.host}:{self.port}"

    def string(self):
        """
        to string
        :return: <host>:<port>
        """
        return self.__str__()
