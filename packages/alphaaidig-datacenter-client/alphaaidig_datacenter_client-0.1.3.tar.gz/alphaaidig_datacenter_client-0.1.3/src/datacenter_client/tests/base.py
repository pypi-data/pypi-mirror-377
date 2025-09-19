import unittest
from typing import Dict, Any

from datacenter_client.client import DatacenterClient


class BaseClientTest(unittest.TestCase):
    """基础测试类，提供通用的测试设置和方法"""
    
    BASE_URL = "http://localhost:10000"
    TOKEN = "4e2e929a1ba14b06b8e8ca7e7e560efe"
    
    def setUp(self):
        """设置测试环境"""
        self.client = DatacenterClient(base_url=self.BASE_URL, token=self.TOKEN)
    
    def check_success_response(self, result: Dict[str, Any]) -> bool:
        """检查响应是否成功"""
        # 由于BaseClient._request()已经处理了status检查并只返回data部分
        # 这里我们只需要检查result是否为非空字典
        return isinstance(result, dict) and bool(result)
    
    def check_pagination_response(self, result: Dict[str, Any]) -> bool:
        """检查分页响应格式"""
        if not self.check_success_response(result):
            return False
        
        # 由于BaseClient._request()已经处理了status检查并只返回data部分
        # 这里result就是data本身
        return 'items' in result and 'pagination' in result
    
    def print_pagination_info(self, result: Dict[str, Any]):
        """打印分页信息"""
        if self.check_pagination_response(result):
            # 由于BaseClient._request()已经处理了status检查并只返回data部分
            # 这里result就是data本身
            print(f"返回记录数: {len(result['items'])}")
            print(f"分页信息: {result['pagination']}")
            if result['items']:
                print(f"第一条记录: {result['items'][0]}")
        else:
            print("返回数据格式不符合预期")
    
    def print_list_info(self, result: Any):
        """打印列表信息"""
        if isinstance(result, list):
            print(f"返回记录数: {len(result)}")
            if result:
                print(f"第一条记录: {result[0]}")
        elif isinstance(result, dict):
            # 如果是字典，可能是分页数据
            if 'items' in result:
                print(f"返回记录数: {len(result['items'])}")
                if result['items']:
                    print(f"第一条记录: {result['items'][0]}")
            else:
                print("返回数据格式不符合预期")
        else:
            print("返回数据格式不符合预期")
    
    def print_item_info(self, result: Dict[str, Any]):
        """打印单项信息"""
        if self.check_success_response(result):
            # 由于BaseClient._request()已经处理了status检查并只返回data部分
            # 这里result就是data本身
            print(f"返回数据: {result}")
        else:
            print("请求失败")