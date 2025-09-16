import json
import uuid

from rpa_common import Common
from rpa_amazon_buyer.api.ProductApi import ProductApi

common = Common()
productApi = ProductApi()

class ProductService():
    def __init__(self):
        super().__init__()

    def getProductInfo(self, driver, shop_data, options):
        '''
        @Desc    : 获取产品信息
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取产品信息
        productApi.getProductInfo(driver, options)