from datacenter_client.tests.base import BaseClientTest
import unittest


class TestMarginSummaryClient(BaseClientTest):
    """融资融券总结客户端测试类"""
    
    def test_page_list(self):
        """测试分页获取融资融券总结"""
        print("\n" + "=" * 50)
        print("测试融资融券总结客户端 - 分页获取")
        print("=" * 50)
        
        try:
            result = self.client.margin_summary.page_list(page=1, page_size=5)
            print(f"状态: {result.get('status')}")
            self.print_pagination_info(result)
        except Exception as e:
            print(f"测试分页获取时出错: {e}")


if __name__ == "__main__":
    unittest.main()