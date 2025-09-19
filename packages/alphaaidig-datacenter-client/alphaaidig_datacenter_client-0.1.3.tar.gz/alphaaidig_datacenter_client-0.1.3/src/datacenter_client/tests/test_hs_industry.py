from datacenter_client.tests.base import BaseClientTest
import unittest


class TestHSIndustryClient(BaseClientTest):
    """沪深行业客户端测试类"""
    
    def test_list(self):
        """测试获取沪深行业列表"""
        print("\n" + "=" * 50)
        print("测试沪深行业客户端 - 获取列表")
        print("=" * 50)
        
        try:
            result = self.client.hs_industry.page_list()
            print(f"状态: {result.get('status')}")
            self.print_pagination_info(result)
        except Exception as e:
            print(f"测试获取列表时出错: {e}")
    
    def test_get(self):
        """测试获取单个沪深行业信息"""
        print("\n" + "=" * 50)
        print("测试沪深行业客户端 - 获取单个行业信息")
        print("=" * 50)
        
        try:
            result = self.client.hs_industry.get("801180")
            print(f"状态: {result.get('status')}")
            self.print_item_info(result)
        except Exception as e:
            print(f"测试获取单个行业信息时出错: {e}")
    
    def test_summary(self):
        """测试获取沪深行业统计信息"""
        print("\n" + "=" * 50)
        print("测试沪深行业客户端 - 获取统计信息")
        print("=" * 50)
        
        try:
            result = self.client.hs_industry.summary()
            print(f"状态: {result.get('status')}")
            self.print_item_info(result)
        except Exception as e:
            print(f"测试获取统计信息时出错: {e}")


if __name__ == "__main__":
    unittest.main()