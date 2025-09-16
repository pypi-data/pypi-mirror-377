import json
import gc
import requests
import time
import threading
import tempfile
import traceback
import sys
import os
from pathlib import Path
from rpa_common.Common import Common
from rpa_common.library.AdsPower import AdsPower
from rpa_common.request.ShopRequest import ShopRequest
from rpa_common.request.TaskRequest import TaskRequest
from rpa_common.exceptions import TaskParamsException

common = Common()
adsPower = AdsPower()
shopRequest = ShopRequest()
taskRequest = TaskRequest()

class Task():
    def __init__(self):
        super().__init__()

        self.platform_shopid = None
        self.account_id = None

        self.driver = None

    def run(self, shop_data):
        '''
        @Desc    : 运行
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:21:14
        '''
        # 记录开始时间
        start_time = time.time()

        try:
            self.platform_shopid = shop_data.get("platformShipId")
            print("platform_shopid", self.platform_shopid)
            if not self.platform_shopid:
                print("主店铺ID为空")
                return

            platform_account_id_list = shop_data.get("platformAccountIdList")
            if not platform_account_id_list:
                print("店铺ID为空")
                return

            self.account_id = platform_account_id_list[0]
            print("account_id", self.account_id)
            if not self.account_id:
                print("店铺ID为空")
                return

            print("获取店铺详情")
            shop_detail_params = {
                "account_id": self.account_id
            }
            res = shopRequest.getDetail(shop_detail_params)
            code = res.get("code", 0)
            if code != 1:
                print("获取店铺详情失败：", json.dumps(res))
                return

            shop_detail = res.get("data", {})

            env_data = shop_detail.get("env_data")
            profile = env_data.get("profile")

            # 环境ID
            self.profile_id = profile.get("profile_id")
            if not self.profile_id:
                print("环境ID为空")
                return

            # 启动AdsPower
            print("启动AdsPower")
            self.driver = adsPower.start_driver(self.profile_id)
            if not self.driver:
                print("未启动打开店铺")
                return

            # 登录
            res = self.login(self.driver, shop_detail)
            if res['status'] != 1:
                print(res['message'])
                return common.back(0, res['message'])

            # 循环任务
            self.loop_task(self.driver, shop_detail)

        except Exception as e:
            # 获取异常
            error_data = self.get_error_data(e)

            # 计算运行时长（秒）
            run_duration = time.time() - start_time
            error_data['run_duration'] = run_duration

            # 任务ID
            print("任务失败", json.dumps(error_data, ensure_ascii=False))

            # 任务失败
            # taskRequest.errorShop(error_data)

        finally:
            # 垃圾回收
            gc.collect()

    def login(self, driver, shop_data):
        '''
        @Desc    : 登录
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        platform = shop_data['platform']

        if platform == 'tiktok':
            # 登录
            from rpa_tiktok.service.TiktokService import TiktokService
            tiktokService = TiktokService()

            res = tiktokService.login(driver, shop_data)
            if res['status'] != 1:
                print(res['message'])
                return common.back(0, res['message'])

        elif platform == 'lazada':
            from rpa_lazada.service.LazadaService import LazadaService
            lazadaService = LazadaService()

            # 登录
            res = lazadaService.login(driver, shop_data, options)
            if res['status'] != 1:
                print(res['message'])
                return common.back(0, res['message'])

        elif platform == 'temu':
            from rpa_temu.service import TemuService
            temuService = TemuService()

            temuService.login(driver, shop_data)

        elif platform == 'shopee':
            from rpa_shopee.service.ShopeeService import ShopeeService
            shopeeService = ShopeeService()

            shopeeService.login(driver, shop_data, options)

        elif platform == 'aliexpress':
            from rpa_aliexpress.service import AliexpressService
            aliexpressService = AliexpressService()

            aliexpressService.login(driver, shop_data, options)

        elif platform == 'shein':
            from rpa_shein.service.SheinService import SheinService
            sheinService = SheinService()

            sheinService.login(driver, shop_data, options)
        elif platform == 'temu':
            from rpa_eaby.service.EbayService import EbayService
            ebayService = EbayService()

            ebayService.login(driver, shop_data, options)

        return common.back(1, "登录成功")

    def loop_task(self, driver, shop_data):
        '''
        @Desc    : 循环任务
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("循环任务开始")

        # 获取任务
        print("获取任务")
        task_params = {
            "platform_shopid": self.platform_shopid
        }
        res = taskRequest.getTaskDetail(task_params)
        if res['code'] != 200:
            raise TaskParamsException(res['error'])
        task_list = res['data']

        if not task_list:
            print("暂无任务")
            return

        for item in task_list:
            # 任务参数
            task_params = self.build_task_params(item)
            if not task_params:
                print(f"任务参数不完善")

                # 任务ID
                error_data = {
                    "task_id": item['task_id'],
                    "status": 3,
                    "fail_code": '43000',
                    "fail_count": 1,
                    "fail_message": '任务参数不完善'
                }
                # 任务失败
                taskRequest.response(error_data)
                continue

            print("任务参数", json.dumps(task_params))

            print("=====检查店铺状态=====")
            start_time = time.time()
            params = {
                "user_id": self.profile_id,
            }
            res = adsPower.api_get("/api/v1/browser/active", params)
            run_duration = time.time() - start_time
            print(f"检查店铺状态用时：{run_duration}秒")

            if res["code"] == 0:
                status = res["data"]['status']
                if status != "Active":
                    print(res['msg'])
                    return common.back(0, res['msg'])
            else:
                print(res['msg'])
                return common.back(0, res['msg'])

            # 执行任务
            print("任务执行中...")
            self.run_task(driver, shop_data, task_params)

            time.sleep(1)

    def build_task_params(self, item):
        '''
        @Desc    : 组装任务参数
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("组装任务参数")
        task_id             = item.get("id")
        shop_global_id      = item.get("platformShipId")
        account_id          = item.get("platformAccountId")
        platform            = item.get("platform")
        appInfo             = item.get("appInfo", {})
        requestBody         = item.get("requestBody")
        site                = item.get("site")
        platformShip        = item.get("platformShip")
        dataSource          = item.get("dataSource")

        app_id      = appInfo.get("id", 0)
        task_job    = appInfo.get("runPath", '')
        if not task_job:
            return

        default_params = {
            "task_id": task_id,
            "account_id": account_id,
            "shop_global_id": shop_global_id,
            "type_id": app_id,
            "shop_id": platformShip,
            "site": site,
            "data_source": dataSource
        }

        task_params = {
            "platform": platform,
            "task_job": task_job
        }

        # 空值转对象
        if requestBody == '':
            requestBody = {}

        # 字符串转字典
        if isinstance(requestBody, str):
            requestBody = json.loads(requestBody)

        print("合并参数")
        params = {**default_params, **requestBody}

        task_params['params'] = params

        return task_params

    def run_task(self, driver, shop_data, task_params):
        '''
        @Desc    : 执行任务
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("执行任务")

        # 记录开始时间
        start_time = time.time()

        params = task_params.get("params")

        try:
            # 调用脚本
            common.runJob(driver, shop_data, task_params)

            # 计算运行时长（秒）
            run_duration = time.time() - start_time
            params['run_duration'] = run_duration
            print(f"任务用时：{run_duration}秒")

            # 完成任务
            params['status'] = 2
            params['success_count'] = 1
            taskRequest.response(params)

        except Exception as e:
            # 获取异常
            error_data = self.get_error_data(e)

            # 计算运行时长（秒）
            run_duration = time.time() - start_time
            error_data['run_duration'] = run_duration
            print(f"任务用时：{run_duration}秒")

            # 任务ID
            error_data['task_id'] = params['task_id']
            print("任务失败", json.dumps(error_data, ensure_ascii=False))

            # 任务失败
            error_data['status'] = 3
            error_data['fail_count'] = 1
            taskRequest.response(error_data)

    def get_error_data(self, e):
        '''
        @Desc    : 获取异常
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        try:
            exc_type, exc_obj, tb = sys.exc_info()  # 解包
            # 获取完整 traceback 栈
            tb_list = traceback.extract_tb(tb)
        except Exception:
            exc_obj = None
            tb_list = None

        # 失败信息
        try:
            error_data = e.error_data()
        except Exception:
            if tb_list:
                last_call = tb_list[-1]  # 最底层的异常点
                file_path = last_call.filename
                line_no = last_call.lineno
            else:
                file_path = None
                line_no = -1

            error_data = {
                "error_code": "99999",
                "error_msg": "未知异常",
                "error_response": str(exc_obj),
                "error_file": file_path,
                "error_line": line_no
            }

        return error_data