import json
import time
import traceback
import json
import psutil
import platform
import os
import requests
import subprocess
import urllib.parse
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from rpa_common.exceptions import IpException, ChromeException, FingerprintException

from rpa_common.library.Request import Request
from rpa_common.Common import Common

common = Common()
request = Request()

class AdsPower():
    def __init__(self):
        super().__init__()

        # 端口
        self.api_port = int(os.getenv("ADS_PORT", "50325"))

        self.profile_id = None

        self.webdriver = None
        self.selenium = None

        self.system = platform.system()

    def start_driver(self, profile_id):
        '''
        @Desc    : 启动驱动
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:21:14
        '''
        # 系统
        if self.system == "Windows":
            bool = self.check_ads_power_running()
        else:
            bool = self.check_ads_power_installed()

        if not bool:
            return

        self.profile_id = profile_id

        print("=====启动客户端=====")
        start_time = time.time()
        self.start_browser()
        run_duration = time.time() - start_time
        print(f"启动客户端用时：{run_duration}秒")

        print("=====API接口状态=====")
        start_time = time.time()
        self.api_get("/status")
        run_duration = time.time() - start_time
        print(f"API接口状态用时：{run_duration}秒")

        print("=====检查店铺状态=====")
        start_time = time.time()
        params = {
            "user_id": self.profile_id,
        }
        res = self.api_get("/api/v1/browser/active", params)
        run_duration = time.time() - start_time
        print(f"检查店铺状态用时：{run_duration}秒")

        code = res.get("code", 1)
        if code == 0:
            status = res["data"]['status']
            if status == "Active":
                self.webdriver = res["data"]["webdriver"]
                print("chrome_driver", self.webdriver)

                self.selenium = res["data"]["ws"]["selenium"]
                print("selenium", self.selenium)
            else:
                # 关闭店铺
                self.stop_shop(self.profile_id)

                # 打开店铺
                self.open_shop()
        else:
            # 打开店铺
            self.open_shop()

        # 设置调试地址
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", self.selenium)
        chrome_options.add_argument("--disable-popup-blocking")  # 禁用弹出窗口拦截

        # 创建 Service 对象，传入 ChromeDriver 路径
        service = Service(executable_path=self.webdriver)

        # 使用 webdriver.Chrome() 正确传递参数
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 打印页面标题
        print(driver.title)

        return driver

    def check_ads_power_running(self):
        '''
        @Desc    : 检测Ads客户端
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:21:14
        '''
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == "AdsPower Global.exe":
                print("AdsPower 应用程序正在运行")
                return True
        print("AdsPower 应用程序未运行")
        return False

    def stop_shop(self, profile_id):
        '''
        @Desc    : 关闭店铺
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:21:14
        '''
        print("=====关闭店铺=====")
        start_time = time.time()
        params = {
            "user_id": profile_id,
        }
        self.api_get("/api/v1/browser/stop", params)
        run_duration = time.time() - start_time
        print(f"关闭店铺用时：{run_duration}秒")

    def open_shop(self):
        '''
        @Desc    : 打开店铺
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:21:14
        '''
        print("=====打开店铺=====")
        start_time = time.time()
        params = {
            "user_id": self.profile_id,
            "open_tabs": "1",
            "ip_tab": "0",
            "disable_password_filling": "1",
            "enable_password_saving": "0",
        }

        # 系统
        if self.system == "Linux":
            # linux
            params['headless'] = 1

        resp = self.api_get("/api/v1/browser/start", params)
        run_duration = time.time() - start_time
        print(f"打开店铺用时：{run_duration}秒")

        code = resp.get("code", 1)
        if code != 0:
            raise ChromeException(resp.get("msg", "打开店铺失败"))

        self.webdriver = resp["data"]["webdriver"]
        print("chrome_driver", self.webdriver)

        self.selenium = resp["data"]["ws"]["selenium"]
        print("selenium", self.selenium)

    def check_ads_power_installed(self):
        '''
        @Desc    : linux检测是否安装 adspower
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:21:14
        '''
        try:
            # 使用 which 命令检查 adspower_global 是否安装
            result = subprocess.run(['which', 'adspower_global'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # 如果输出有路径，说明 adspower_global 已安装
            if result.stdout:
                print(f'adspower_global 已安装，安装路径: {result.stdout.strip()}')
                return True
            else:
                print('adspower_global 未安装。')
                return False
        except Exception as e:
            print(f"错误: {e}")
            return False

    def start_browser(self):
        '''
        @Desc    : 启动客户端
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:21:14
        '''
        # 系统
        if self.system == "Linux":
            # linux
            app = "adspower_global"
            api_key = "109bfb4a512cafd534c86362f5ec1566"
        else:
            print(f"请手动启动客户端: {self.system}")
            return False

        try:
            # 检查是否已经有进程在运行
            process_running = False
            for proc in psutil.process_iter(attrs=['pid', 'name']):
                if 'adspower_global' in proc.info['name']:
                    process_running = True
                    break

            # 如果进程没有在运行，则启动浏览器
            if not process_running:
                os.environ["DISPLAY"] = ":1"
                cmd = [
                    app,
                    '--no-sandbox',
                    '--disable-gpu',
                    '--headless=true',
                    f'--api-key={api_key}',
                    '--api-port=' + str(self.api_port)
                ]
                subprocess.Popen(cmd)
                time.sleep(15)
                print("浏览器启动成功")
                return True
            else:
                print("进程已经在运行中")
                return True
        except Exception as e:
            print('启动浏览器进程失败: ' + traceback.format_exc())
            return False

    def api_get(self, path, params = {}):
        '''
        @Desc    : get请求
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:21:14
        '''
        try:
            url = f'http://127.0.0.1:{self.api_port}{path}'
            # 如果有参数，转化为 URL 查询参数并拼接到 URL 后面
            if params:
                query_string = urllib.parse.urlencode(params)  # 将字典转换为 URL 编码的查询字符串
                url = f'{url}?{query_string}'  # 拼接查询字符串到 URL
            print(f"url:{url}")
            res = request.get(url)
            print(f"res:{res}")
            return res
        except Exception as err:
            print(err)

    def api_post(self, path, data = {}):
        '''
        @Desc    : post请求
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:21:14
        '''
        try:
            url = f'http://127.0.0.1:{self.api_port}{path}'
            res = request.post(url, data)
            print(f"res:{res}")
            return res
        except Exception as err:
            print(err)