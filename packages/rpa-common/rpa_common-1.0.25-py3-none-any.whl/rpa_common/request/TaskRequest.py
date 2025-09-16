import json
from rpa_common import Env
from rpa_common.library.Request import Request
from rpa_common.exceptions import TaskParamsException

env = Env()
request = Request()

class TaskRequest():
    def __init__(self):
        super().__init__()

        env_data = env.get()
        self.host = env_data['api']
        self.open_api = env_data['open_api']

    def getShop(self, data):
        '''
        @Desc    : 获取店铺
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("获取店铺 strat", json.dumps(data))
        url = self.open_api + '/openapi-api/rpa/shipid'
        res = request.get(url, data)
        print("获取店铺 end")
        return res

    def getTaskDetail(self, data):
        '''
        @Desc    : 获取任务明细
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("获取任务明细 strat")
        url = self.open_api + '/openapi-api/rpa/request'
        res = request.get(url, data)
        print("获取任务明细 end", json.dumps(res))
        return res

    def getTaskShopList(self):
        '''
        @Desc    : 获取任务店铺列表
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("获取任务店铺列表 strat")
        url = self.host + '/api/v2/index/post?c=task&a=getTaskShopList&zsit=debug'
        res = request.post(url, {})
        print("获取任务店铺列表 end", res)
        return res

    def getTaskDebug(self, data):
        '''
        @Desc    : 获取任务调试
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("获取任务调试 strat")
        url = self.host + '/api/v2/index/post?c=task&a=getTaskDebug&zsit=debug'
        res = request.post(url, data)
        print("获取任务调试 end", res)
        return res

    def getShopTask(self, data):
        '''
        @Desc    : 获取任务店铺列表
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("获取店铺任务 strat")
        url = self.host + '/api/v2/index/post?c=task&a=getShopTask&zsit=debug'
        res = request.post(url, data)
        print("获取店铺任务 end", res)
        return res

    def getTask(self, data):
        '''
        @Desc    : 获取任务信息
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("获取任务信息 strat")

        url = self.host + '/api/v2/index/post?c=task&a=getTaskInfo&zsit=debug'
        res = request.post(url, data)
        print("获取任务信息 end", res)
        return res

    def save(self, data):
        '''
        @Desc    : 保存数据
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("保存数据 strat")
        url = self.host + '/api/v2/index/post?c=data&a=storage&zsit=debug'
        res = request.post(url, data)
        print("保存数据 end")
        code = res.get("code", 0)
        if code != 1:
            print("保存数据失败", json.dumps(res))
            raise TaskParamsException(json.dumps(res))

        return res

    def end(self, data):
        '''
        @Desc    : 完成任务
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("完成任务 strat")
        url = self.host + '/api/v2/index/post?c=task&a=completeTask&zsit=debug'
        res = request.post(url, data)
        print("完成任务 end", res)
        return res

    def error(self, data):
        '''
        @Desc    : 任务失败
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("任务失败 strat")
        url = self.host + '/api/v2/index/post?c=task&a=failedTask&zsit=debug'
        res = request.post(url, data)
        print("任务失败 end", res)
        return res

    def errorShop(self, data):
        '''
        @Desc    : 店铺任务失败
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("店铺任务失败 strat")
        url = self.host + '/api/v2/index/post?c=task&a=failedShopTask&zsit=debug'
        res = request.post(url, data)
        print("店铺任务失败 end", res)
        return res

    def response(self, data):
        '''
        @Desc    : 任务结果
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        params = self.build_response_params(data)

        print("任务结果 strat", json.dumps(params))
        url = self.open_api + '/openapi-api/rpa/response'
        res = request.post(url, params)
        print("任务结果 end", json.dumps(res))
        return res

    def build_response_params(self, data):
        '''
        @Desc    : 组装任务结果参数
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        params = {
            "id": data.get("task_id"),
            "status": data.get("status"),
            "success_count": data.get("success_count", 0),
            "fail_count": data.get("fail_count", 0),
            "fail_code": data.get("error_code", ''),
            "fail_message": data.get("error_msg", ''),
            "fail_data": data.get("error_response", ''),
        }

        return params