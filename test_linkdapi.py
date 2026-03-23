# /// script
# dependencies = ["linkdapi"]
# ///

from linkdapi import LinkdAPI
import json

# API密钥
api_key = "li-AqG4H7aQFqrL9OGvesAP1qBWweEyIZ2RxUwQgT73XWlf-XJrXn_19UfArQSZ2OHMjPTJ_A4jIpNYNhhWmtyTbTctTtO82Q"
client = LinkdAPI(api_key)

# 测试API方法
print("测试LinkdAPI方法...")

# 测试搜索帖子
try:
    result = client.search_posts(keyword="CFM56")
    print(f"search_posts结果类型: {type(result)}")
    print(f"search_posts结果: {json.dumps(result, indent=2)[:500]}...")
except Exception as e:
    print(f"search_posts错误: {str(e)}")

# 测试获取个人资料
try:
    result = client.get_profile_overview("nick-chambers-10ab4628")
    print(f"\nget_profile_overview结果类型: {type(result)}")
    if result.get('success'):
        print(f"获取到个人资料: {result['data'].get('fullName', 'Unknown')}")
except Exception as e:
    print(f"get_profile_overview错误: {str(e)}")

# 列出所有可用方法
print(f"\n客户端方法: {[method for method in dir(client) if not method.startswith('_')]}")
