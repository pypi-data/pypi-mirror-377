import json
import time
import hashlib
import urllib.request
import os
import time
import uuid
from datetime import datetime, timedelta
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from rpa_common.exceptions import TaskParamsException
from rpa_common.request.TaskRequest import TaskRequest
from rpa_common.service.ExecuteService import ExecuteService

taskRequest = TaskRequest()
executeService = ExecuteService()

class ProductApi():
    def __init__(self):
        super().__init__()

    def getProductInfo(self, driver, options):
        '''
        @Desc    : 获取产品信息
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "url" not in options:
            raise TaskParamsException("缺少 url")
        url = options.get("url")

        # 访问页面
        driver.get(url)

        # 等待页面加载
        time.sleep(0.1)

        # 打印页面标题
        print(driver.title)

        # 执行 JS 发起 fetch 请求
        # url = "https://api16-normal-useast1a.tiktokshopglobalselling.com/api/v1/product/global/product_creation/preload_all_categories"

        # params = {
        #     "oec_seller_id": oec_seller_id,
        #     "aid": "6556"
        # }

        # res = executeService.request(driver=driver, url=url, params=params, method="GET")

        # request_id = str(uuid.uuid4())

        # # 保存数据
        # options['request_id'] = request_id
        # options['response'] = res
        # taskRequest.save(options)
