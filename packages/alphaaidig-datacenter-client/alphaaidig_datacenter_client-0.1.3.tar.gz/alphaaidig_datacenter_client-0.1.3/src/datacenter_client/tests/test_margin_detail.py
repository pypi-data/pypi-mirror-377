from datacenter_client.tests.base import BaseClientTest
import unittest


class TestMarginDetailClient(BaseClientTest):
    """融资融券明细客户端测试类"""
    
    def test_page_list_by_date(self):
        """测试按日期分页获取融资融券明细"""
        print("\n" + "=" * 50)
        print("测试融资融券明细客户端 - 按日期分页获取")
        print("=" * 50)
        
        try:
            result = self.client.margin_detail.page_list_by_date(page=1, page_size=5)
            print(f"状态: {result.get('status')}")
            self.print_pagination_info(result)
        except Exception as e:
            print(f"测试按日期分页获取时出错: {e}")
    
    def test_page_list_by_stock(self):
        """测试按股票分页获取融资融券明细"""
        print("\n" + "=" * 50)
        print("测试融资融券明细客户端 - 按股票分页获取")
        print("=" * 50)
        
        try:
            result = self.client.margin_detail.page_list_by_stock(stock_code="000001", page=1, page_size=5)
            print(f"状态: {result.get('status')}")
            self.print_pagination_info(result)
        except Exception as e:
            print(f"测试按股票分页获取时出错: {e}")


if __name__ == "__main__":
    unittest.main()