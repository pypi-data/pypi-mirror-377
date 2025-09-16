import json
import time
import requests
import requests
import mimetypes
import uuid
import random
import jwt
import hmac
import secrets
import string
import hashlib
import base64
import pandas as pd
from io import BytesIO, StringIO
from urllib.parse import urlparse, urlencode
from typing import Union, Dict, Literal, List
from rpa_common.library.Decorator import retry
from rpa_common import Common
from rpa_common.exceptions import RequestException

common = Common()

class Request():
    def __init__(self):
        super().__init__()

    def get(self, url, data = {}, headers=None):
        '''
        @描述    : GET 请求
        @作者    : 钟水洲
        @时间    : 2024/05/31 10:20:48
        '''
        if not headers:
            headers = self.getHeaders("GET", url, data)

        if data:
            # 使用 urlencode 方法将字典转为查询字符串（会自动处理 URL 编码）
            query_string = urlencode(data)

            # 检查 URL 是否已经包含查询参数（即是否含有 '?'）
            if '?' in url:
                # 如果有查询参数，使用 '&' 拼接新的参数
                url = f"{url}&{query_string}"
            else:
                # 如果没有查询参数，使用 '?' 拼接参数
                url = f"{url}?{query_string}"

        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()  # 如果响应状态码不正确，则抛出 HTTPError 异常
            print("响应状态码", res.status_code)  # 打印响应状态码
            if res.status_code == 200:
                return res.json()  # 如果响应状态码是 200，返回 JSON 数据
            else:
                print("响应结果", res.text)  # 输出响应的文本内容

        except Exception as e:
            raise RequestException(str(e))

    def post(self, url, data = {}, files=None, headers=None):
        '''
        @描述    : POST 请求
        @作者    : 钟水洲
        @时间    : 2024/05/31 10:20:53
        '''
        if not headers:
            headers = self.getHeaders("POST", url, data)

        try:
            if files:
                res = requests.post(url, data=json.dumps(data), files=files, headers=headers)
            else:
                res = requests.post(url, data=json.dumps(data), headers=headers)

            res.raise_for_status()  # 如果响应状态码不正确，则抛出 HTTPError 异常
            print("响应状态码", res.status_code)  # 打印响应状态码
            if res.status_code == 200:
                return res.json()  # 如果响应状态码是 200，返回 JSON 数据
            else:
                print("响应结果", res.text)  # 输出响应的文本内容

        except Exception as e:
            raise RequestException(str(e))

    def getHeaders(self, method, url, params = None):
        '''
        @描述    : POST 请求
        @作者    : 钟水洲
        @时间    : 2024/05/31 10:20:53
        '''
        # 解析 URL
        parsed_url = urlparse(url)

        # 获取路径部分
        path = parsed_url.path

        # 应用ID
        app_id = "app_1757061695_bou_01"
        # 应用秘钥
        app_secret = "3079f14cc84c0f7afe49a0b616efb1b4"

        # 随机字符串
        nonce = common.generate_random_string(32)
        # 当前时间
        timestamp_precise = int(time.time())
        # 毫秒
        timestamp = str(timestamp_precise * 1000)
        # 微秒
        timestamp_microseconds = int(timestamp_precise * 1_000_000)

        # 随机数
        random_number = random.randint(10000000, 99999999)

        # 请求ID
        request_id = f"{app_id}-{timestamp_microseconds}-{random_number}"

        sign = self.generate_sign(method, path, timestamp, nonce, params, app_secret)

        token = self.generate_token()

        headers = {
            "X-AppID": app_id,
            "X-Nonce": nonce,
            "X-Timestamp": timestamp,
            "X-Request-ID": request_id,
            "X-Sign": sign,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        return headers

    def generate_token(self):
        '''
        @Desc    : 生成Token
        @Author  : 钟水洲
        @Time    : 2025/09/05 15:00:50
        '''
        secret_key = 'QZT3mm3FW3Y4rkC2pKf3JaXrEEsp7NAN'

        timestamp = int(time.time())

        exp = timestamp + 86400

        jti = common.generate_random_string(32)

        payload = {
            "sub": "1",
            "iss": "http://:",
            "exp": exp,
            "iat": timestamp,
            "nbf": timestamp,
            "app": "rpa",
            "userinfo": {
                "username": "0000",
                "id": "0000"
            },
            "uid": 0,
            "s": "8im8uy",
            "jti": jti
        }

        token = jwt.encode(payload, secret_key, algorithm='HS256')

        return token

    def generate_sign(self, method, path, timestamp, nonce, params, app_secret):
        '''
        @Desc    : 生成加密串
        @Author  : 钟水洲
        @Time    : 2025/09/05 15:00:50
        '''
        # 1. 拼接原始字符串（按固定顺序）
        raw = []
        raw.append(method.upper())  # 请求方法（大写）
        raw.append(path)  # API路径
        raw.append(timestamp)  # 增加X-Timestamp
        raw.append(nonce)  # 增加X-Nonce

        # 2. 拼接排序后的请求参数（params是已排序的字典）
        if params:
            sorted_params = dict(sorted(params.items()))

            # 循环遍历排序后的字典
            for key, value in sorted_params.items():
                param_str = f"{key}={value}"
                raw.append(param_str)

        # 3. HMAC-SHA256加密
        raw_string = "&".join(raw)  # 拼接原始字符串
        key = app_secret.encode('utf-8')  # 转换appSecret为字节
        message = raw_string.encode('utf-8')  # 转换原始字符串为字节

        # 使用hmac进行sha256加密
        hmac_obj = hmac.new(key, message, hashlib.sha256)
        sign_bytes = hmac_obj.digest()

        # 4. 转为Base64字符串
        signature = base64.b64encode(sign_bytes).decode('utf-8')

        return signature

    def reques(self, *, max_retries=3, delay=1, exceptions=(Exception,), status_code: Union[None, List[int]]=None,
               method: Literal['GET', 'POST', 'HEAD'],
               url,
               data=None,
               json=None,
               cookies=None,
               headers=None,
               params=None,
               timeout=None,
               files=None
               ) -> requests.Response:
        """
        @Desc     : requests请求方法封装
        @Author   : 祁国庆
        @Time     : 2025/07/21 10:44:10
        @Params   :
            - max_retries: 最大重试次数
            - delay: 重试间隔时间(秒)
            - exceptions: 需要重试的异常类型
            - status_code: 白名单状态码条件重试，非白名单的状态码会进行重试，None为不开启
        @Returns  : 返回此方法 requests.Response
        用法示例：reques(method='GET', url='https://www.xxx.com', params={'t': 1752681600})
        支持自定义重试次数、条件重试
        """
        @retry(max_retries=max_retries, delay=delay, exceptions=exceptions)
        def _(*,
               method: Literal['GET', 'POST', 'HEAD'],
               url,
               data = None,
               json = None,
               cookies = None,
               headers = None,
               params = None,
               timeout = None,
               files = None
               ):
            assert method in ['GET', 'POST', 'HEAD'], '[reques]method参数错误'
            assert url, '[reques]url参数不能为空'
            request = getattr(requests, method.lower())
            response = request(**{
                'url': url,
                'data': data,
                'json': json,
                'cookies': cookies,
                'headers': headers,
                'params': params,
                'timeout': timeout,
                'files': files
            })
            if status_code and response.status_code not in status_code:
                raise Exception(f'[reques]当前状态码:{response.status_code} | 白名单状态码:{status_code}')
            return response
        return _(**{
            'method': method,
            'url': url,
            'data': data,
            'json': json,
            'cookies': cookies,
            'headers': headers,
            'params': params,
            'timeout': timeout,
            'files': files
        })

    @retry(max_retries=5, delay=2, exceptions=(ValueError))
    def downloadExcel(self, url, head={}):
        '''
        @Desc    : 获取远程表格文件内容（支持xlsx/xls/csv）
        @Author  : 黄豪杰
        @return  : 多维数组或JSON字符串
        @Time    : 2025/03/28 09:55:13
        '''
        if not url:
            return []

        cookies = head.get('cookies', {})
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            **head.get('headers', {})
        }
        
        try:
            # 发送 GET 请求获取文件内容
            response = requests.get(url, cookies=cookies, headers=headers, stream=True)
            response.raise_for_status()
            
            # 获取文件类型
            content_type = response.headers.get('Content-Type', '').lower()
            parsed_url = urlparse(url)
            file_ext = parsed_url.path.split('.')[-1].lower() if '.' in parsed_url.path else ''
            
            # 根据类型处理不同格式
            content = response.content
            
            if 'excel' in content_type or file_ext in ('xls', 'xlsx'):
                return self._process_excel(content)
            elif 'csv' in content_type or file_ext == 'csv':
                return self._process_csv(content)
            else:
                # 尝试自动检测类型
                try:
                    return self._process_excel(content)
                except Exception:
                    return self._process_csv(content)
                    
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"下载文件失败: {e}")
        except Exception as e:
            raise ValueError(f"处理表格文件时出错: {e}")

    def _process_excel(self, content):
        """处理Excel文件（xlsx/xls）"""
        with BytesIO(content) as buffer:
            with pd.ExcelFile(buffer) as xls:
                excel_data = {}
                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    df.fillna("", inplace=True)
                    excel_data[sheet_name] = df.to_dict(orient='records')
                return excel_data

    def _process_csv(self, content):
        """处理CSV文件"""
        # 尝试常见编码
        encodings = ['utf-8', 'gbk', 'latin1', 'iso-8859-1']
        for encoding in encodings:
            try:
                with StringIO(content.decode(encoding)) as buffer:
                    df = pd.read_csv(buffer)
                    df.fillna("", inplace=True)
                    return {'Sheet1': df.to_dict(orient='records')}
            except UnicodeDecodeError:
                continue
        raise ValueError("无法解析CSV文件的编码")