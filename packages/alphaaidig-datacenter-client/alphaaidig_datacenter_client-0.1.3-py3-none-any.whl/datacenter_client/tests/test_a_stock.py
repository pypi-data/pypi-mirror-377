from datacenter_client.tests.base import BaseClientTest
import unittest


class TestAStockClient(BaseClientTest):
    """A 股客户端测试类"""
    
    def test_list(self):
        """测试获取 A 股列表"""
        print("\n" + "=" * 50)
        print("测试 A 股客户端 - 获取列表")
        print("=" * 50)
        
        try:
            result = self.client.a_stock.page_list()
            print(f"状态: {result.get('status')}")
            self.print_pagination_info(result)
        except Exception as e:
            print(f"测试获取列表时出错: {e}")
    
    def test_get(self):
        """测试获取单只 A 股信息"""
        print("\n" + "=" * 50)
        print("测试 A 股客户端 - 获取单只股票信息")
        print("=" * 50)
        
        try:
            result = self.client.a_stock.get("000001")
            print(f"状态: {result.get('status')}")
            self.print_item_info(result)
        except Exception as e:
            print(f"测试获取单只股票信息时出错: {e}")
    
    def test_page_list(self):
        """测试分页获取 A 股列表"""
        print("\n" + "=" * 50)
        print("测试 A 股客户端 - 分页获取列表")
        print("=" * 50)
        
        try:
            result = self.client.a_stock.page_list(page=1, page_size=5)
            print(f"状态: {result.get('status')}")
            self.print_pagination_info(result)
        except Exception as e:
            print(f"测试分页获取列表时出错: {e}")


if __name__ == "__main__":
    unittest.main()