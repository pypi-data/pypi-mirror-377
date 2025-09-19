from datacenter_client.tests.base import BaseClientTest
import unittest


class TestSWIndustryCompanyClient(BaseClientTest):
    """申万行业公司客户端测试类"""
    
    def test_page_list(self):
        """测试分页获取申万行业公司列表"""
        print("\n" + "=" * 50)
        print("测试申万行业公司客户端 - 分页获取列表")
        print("=" * 50)
        
        try:
            result = self.client.sw_industry_company.page_list(page=1, page_size=5)
            print(f"状态: {result.get('status')}")
            self.print_pagination_info(result)
        except Exception as e:
            print(f"测试分页获取列表时出错: {e}")
    
    def test_list(self):
        """测试获取申万行业公司列表"""
        print("\n" + "=" * 50)
        print("测试申万行业公司客户端 - 获取列表")
        print("=" * 50)
        
        try:
            result = self.client.sw_industry_company.list()
            print(f"状态: {result.get('status')}")
            self.print_list_info(result)
        except Exception as e:
            print(f"测试获取列表时出错: {e}")


if __name__ == "__main__":
    unittest.main()