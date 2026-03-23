import re

# 读取原始模型列表
with open('openrouter_models.txt', 'r', encoding='utf-8') as f:
    models = [line.strip() for line in f if line.strip()]

print(f"原始模型数量: {len(models)}")

# 修复模型ID
fixed_models = []
special_models = ['openrouter/auto', 'openrouter/free', 'openrouter/openrouter/free']

for model in models:
    if model in special_models:
        # 特殊模型保持原样
        fixed_models.append(model)
    elif model.startswith('openrouter/'):
        # 移除开头的 openrouter/ 前缀
        # 但需要检查是否是 openrouter/openrouter/ 这种双重前缀
        if model.startswith('openrouter/openrouter/'):
            # 移除一个 openrouter/ 前缀
            fixed_model = model.replace('openrouter/', '', 1)
        else:
            # 移除开头的 openrouter/ 前缀
            fixed_model = model.replace('openrouter/', '', 1)
        
        # 检查是否有 :free 后缀，如果有则移除
        if ':free' in fixed_model:
            fixed_model = fixed_model.replace(':free', '')
        
        fixed_models.append(fixed_model)
    else:
        # 其他情况保持原样
        fixed_models.append(model)

# 去重
unique_models = list(set(fixed_models))
unique_models.sort()

print(f"修复后模型数量: {len(unique_models)}")

# 保存修复后的模型列表
with open('openrouter_models_fixed.txt', 'w', encoding='utf-8') as f:
    for model in unique_models:
        f.write(model + '\n')

# 显示前20个模型作为示例
print("\n前20个修复后的模型:")
for i, model in enumerate(unique_models[:20], 1):
    print(f"{i:3}. {model}")

print(f"\n完整列表已保存到: openrouter_models_fixed.txt")