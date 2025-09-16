import threading
import time
import gc
import json
import schedule
import psutil
from rpa_common.Common import Common
from rpa_common.request.TaskRequest import TaskRequest
from rpa_common.exceptions import TaskParamsException
from rpa_common.library.Task import Task

common = Common()
taskRequest = TaskRequest()

class Run:
    def __init__(self):
        super().__init__()

        # 主入口
        self.main()

    def main(self):
        '''
        @Desc    : 主入口
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:42:03
        '''
        # 每10秒钟执行一次
        schedule.every(10).seconds.do(self.run)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def run(self):
        '''
        @Desc    : 运行
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:42:03
        '''
        # 获取 CPU 占用百分比
        cpu_usage = psutil.cpu_percent(interval=1)

        # 获取内存占用百分比
        memory_usage = psutil.virtual_memory().percent

        # 判断是否超过 90%
        if cpu_usage > 90:
            print(f"警告:CPU 占用超过 90%，当前占用 {cpu_usage}%")
            return

        if memory_usage > 90:
            print(f"警告:内存占用超过 90%，当前占用 {memory_usage}%")
            return

        # 获取店铺
        try:
            shop_params = {
                "device_ip": "192.168.110.103",
                "platform_shop": "634418215033754"
            }
            res = taskRequest.getShop(shop_params)
            code = res.get("code", 500)
            if code != 200:
                print("获取可执行店铺失败", json.dumps(res))
                return

            shop_data = res.get("data", {})

            thread = threading.Thread(target=self.run_task, args=(shop_data,))
            thread.start()
        except Exception as e:
            print(str(e))
        finally:
            # 垃圾回收
            gc.collect()

    def run_task(self, task_item):
        '''
        @Desc    : 执行任务
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:42:03
        '''
        print("----- run_task start -----")
        task = Task()
        task.run(task_item)