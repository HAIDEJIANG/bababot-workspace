import urllib.request, json, os

# 尝试从环境变量获取 API key
api_key = os.environ.get('MATON_API_KEY', '')

if not api_key:
    # 尝试从文件读取
    try:
        with open('C:/Users/Haide/.maton/api_key.txt', 'r') as f:
            api_key = f.read().strip()
    except:
        pass

if not api_key:
    print("ERROR: MATON_API_KEY not found")
    print("Please set environment variable or create ~/.maton/api_key.txt")
else:
    print(f"API Key found: {api_key[:20]}...")
    
    # 测试连接
    req = urllib.request.Request('https://ctrl.maton.ai/connections?app=google-mail&status=ACTIVE')
    req.add_header('Authorization', f'Bearer {api_key}')
    try:
        response = json.load(urllib.request.urlopen(req))
        print(f"\nGmail connections: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")