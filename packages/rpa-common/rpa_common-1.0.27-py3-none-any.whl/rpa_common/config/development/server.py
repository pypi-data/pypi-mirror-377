# -*-coding:utf-8-*-

""" 队列配置 """
class server:
    def __init__(self):
        super().__init__()

    @staticmethod
    def default():
        data = {
            "api": "http://admin.rpa.zs.com",
            "open_api": "http://api.wisserp.com",
            "cdn": "https://oss-rpa.oss-cn-shenzhen.aliyuncs.com",
        }

        return data