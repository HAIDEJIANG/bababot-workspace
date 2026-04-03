import smtplib
import ssl

# 测试不同的 SMTP 配置
configs = [
    {'host': 'smtp.163.com', 'port': 465, 'method': 'SSL', 'starttls': False},
    {'host': 'smtp.163.com', 'port': 25, 'method': 'STARTTLS', 'starttls': True},
    {'host': 'smtp.163.com', 'port': 587, 'method': 'STARTTLS', 'starttls': True},
]

# 读取密码
with open(r'C:\Users\Haide\.config\himalaya\.imap_pw', 'r') as f:
    password = f.read().strip()

email = 'sale@aeroedgeglobal.com'

for cfg in configs:
    print(f"\n测试: {cfg['host']}:{cfg['port']} ({cfg['method']})...")
    try:
        if cfg['starttls']:
            server = smtplib.SMTP(cfg['host'], cfg['port'], timeout=10)
            server.starttls()
        else:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(cfg['host'], cfg['port'], context=context, timeout=10)
        
        server.login(email, password)
        print(f"✅ 登录成功！")
        server.quit()
        break
    except Exception as e:
        print(f"❌ 失败: {e}")