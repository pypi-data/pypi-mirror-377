# 请求异常

from .Base import BaseAppException

class RequestException(BaseAppException):
    def __init__(self, error_msg="请求异常", error_response=None):
        super().__init__(error_msg, error_response, "81000")