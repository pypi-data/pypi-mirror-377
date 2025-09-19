from datacenter_client.tests.base import BaseClientTest
import unittest


class TestMarginAnalysisClient(BaseClientTest):
    """融资融券分析客户端测试类"""
    
    def test_page_list(self):
        """测试通用分页获取融资融券分析"""
        print("\n" + "=" * 50)
        print("测试融资融券分析客户端 - 通用分页获取")
        print("=" * 50)
        
        try:
            result = self.client.margin_analysis.page_list(page=1, page_size=5)
            print(f"状态: {result.get('status')}")
            self.print_pagination_info(result)
        except Exception as e:
            print(f"测试通用分页获取时出错: {e}")
    
    def test_page_list_by_index(self):
        """测试按指数分页获取融资融券分析"""
        print("\n" + "=" * 50)
        print("测试融资融券分析客户端 - 按指数分页获取")
        print("=" * 50)
        
        try:
            result = self.client.margin_analysis.page_list_by_index(page=1, page_size=5)
            print(f"状态: {result.get('status')}")
            self.print_pagination_info(result)
        except Exception as e:
            print(f"测试按指数分页获取时出错: {e}")
    
    def test_page_list_by_industry(self):
        """测试按行业分页获取融资融券分析"""
        print("\n" + "=" * 50)
        print("测试融资融券分析客户端 - 按行业分页获取")
        print("=" * 50)
        
        try:
            result = self.client.margin_analysis.page_list_by_industry(page=1, page_size=5)
            print(f"状态: {result.get('status')}")
            # 注意：这个接口的响应格式略有不同，直接返回包含 items 和 pagination 的字典
            if isinstance(result, dict) and 'items' in result and 'pagination' in result:
                print(f"返回记录数: {len(result['items'])}")
                print(f"分页信息: {result['pagination']}")
                if result['items']:
                    print(f"第一条记录: {result['items'][0]}")
            else:
                print("返回数据格式不符合预期")
        except Exception as e:
            print(f"测试按行业分页获取时出错: {e}")


if __name__ == "__main__":
    unittest.main()