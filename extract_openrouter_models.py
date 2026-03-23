import re
import sys

# 读取 fallbacks list 输出
output = sys.stdin.read()

# 提取所有以 openrouter/ 开头的模型
openrouter_models = []
lines = output.split('\n')
for line in lines:
    line = line.strip()
    # 匹配格式: - openrouter/xxx 或 openrouter/xxx
    if line.startswith('- openrouter/') or line.startswith('openrouter/'):
        # 提取模型ID
        if line.startswith('- '):
            model_id = line[2:].strip()
        else:
            model_id = line.strip()
        
        # 确保是有效的模型ID格式
        if model_id.startswith('openrouter/'):
            openrouter_models.append(model_id)

# 去重
unique_models = list(set(openrouter_models))
unique_models.sort()

print(f"找到 {len(unique_models)} 个 OpenRouter 模型:")
for model in unique_models:
    print(model)

# 保存到文件
with open('openrouter_models.txt', 'w', encoding='utf-8') as f:
    for model in unique_models:
        f.write(model + '\n')