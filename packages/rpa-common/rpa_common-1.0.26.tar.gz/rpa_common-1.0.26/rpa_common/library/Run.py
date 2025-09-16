import threading
import time
import gc
import json
import schedule
import psutil
import socket
import platform
from rpa_common.Common import Common
from rpa_common.request.TaskRequest import TaskRequest
from rpa_common.exceptions import TaskParamsException
from rpa_common.library.Task import Task

common = Common()
taskRequest = TaskRequest()

class Run:
    def __init__(self):
        super().__init__()

        # 本机IP
        self.local_ip = self.get_local_ip()

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

        if not self.local_ip:
            print(f"未获取到本机IP")
            return
        print("IP", self.local_ip)

        # 获取店铺
        try:
            shop_params = {
                "device_ip": self.local_ip
            }
            res = taskRequest.getShop(shop_params)
            code = res.get("code", 500)
            if code != 200:
                print("获取可执行店铺失败", json.dumps(res))
                return
            print("可执行店铺", res)

            shop_data = res.get("data", {})

            thread = threading.Thread(target=self.run_task, args=(shop_data,))
            thread.start()
        except Exception as e:
            print(str(e))
        finally:
            # 垃圾回收
            gc.collect()

    def is_valid_ip(self, interface, addr, os_type):
        """
        判断给定的 IP 地址是否有效
        - 排除回环地址 127.0.0.1
        - 排除虚拟网卡 Windows: vEthernet,Linux:docker、veth
        """
        # 排除回环地址
        if addr.address == "127.0.0.1":
            return False

        # 操作系统类型处理
        if os_type == "Linux":
            # 排除虚拟网卡：docker、veth、lo
            if interface.startswith(("lo", "docker", "veth")):
                return False
        elif os_type == "Windows":
            # 排除虚拟网卡：vEthernet
            if interface.startswith("vEthernet"):
                return False

        # 如果是有效的 IPv4 地址
        return True

    def get_local_ip(self):
        """
        获取本机的 IPv4 地址
        """
        # 获取所有网络接口的信息
        addrs = psutil.net_if_addrs()
        os_type = platform.system()  # 获取当前操作系统类型

        for interface, address_list in addrs.items():
            for addr in address_list:
                # 只处理 IPv4 地址
                if addr.family == socket.AF_INET:
                    if self.is_valid_ip(interface, addr, os_type):
                        return addr.address
        return None  # 如果没有找到有效的 IPv4 地址，返回 None

    def run_task(self, task_item):
        '''
        @Desc    : 执行任务
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:42:03
        '''
        print("----- run_task start -----")
        task = Task()
        task.run(task_item)