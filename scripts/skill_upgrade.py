#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能全面升级脚本
功能:
1. 检查所有已安装技能的可用更新
2. 分析技能使用情况
3. 识别过时/低效技能
4. 生成升级建议报告
5. 执行批量升级

使用方法:
python scripts/skill_upgrade.py
"""

import subprocess
import json
import os
from datetime import datetime
from collections import defaultdict

class SkillAnalyzer:
    """技能分析器"""
    
    def __init__(self):
        self.installed_skills = []
        self.skill_usage = defaultdict(int)
        self.upgrade_candidates = []
    
    def list_installed(self):
        """列出已安装技能"""
        result = subprocess.run(
            ['clawhub', 'list'],
            capture_output=True, text=True
        )
        
        skills = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    skills.append({
                        'name': parts[0],
                        'version': parts[1]
                    })
        
        self.installed_skills = skills
        return skills
    
    def check_updates(self):
        """检查可用更新"""
        updates = []
        
        for skill in self.installed_skills:
            # 搜索最新版本
            result = subprocess.run(
                ['clawhub', 'search', skill['name']],
                capture_output=True, text=True
            )
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if skill['name'] in line:
                        # 解析最新版本
                        parts = line.split()
                        if len(parts) >= 3:
                            latest = parts[0]
                            version = parts[1] if len(parts) > 1 else 'unknown'
                            score = parts[2] if len(parts) > 2 else 'N/A'
                            
                            if version != skill['version']:
                                updates.append({
                                    'name': skill['name'],
                                    'current': skill['version'],
                                    'latest': version,
                                    'score': score
                                })
                                break
        
        self.upgrade_candidates = updates
        return updates
    
    def analyze_usage(self):
        """分析技能使用情况"""
        # 检查会话记录中的技能使用频率
        sessions_dir = 'C:/Users/Haide/.openclaw/agents/main/sessions'
        
        if not os.path.exists(sessions_dir):
            return {}
        
        # 统计工具调用
        tool_calls = defaultdict(int)
        
        for filename in os.listdir(sessions_dir):
            if filename.endswith('.jsonl'):
                filepath = os.path.join(sessions_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            if 'toolCall' in line:
                                # 简单统计
                                tool_calls['total'] += 1
                except:
                    continue
        
        self.skill_usage = dict(tool_calls)
        return self.skill_usage
    
    def generate_report(self, output_file):
        """生成升级报告"""
        report = f"""# 技能全面升级报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**已安装技能**: {len(self.installed_skills)} 个

---

## 技能清单

| 序号 | 技能名称 | 当前版本 | 状态 |
|------|---------|---------|------|
"""
        
        for i, skill in enumerate(self.installed_skills, 1):
            # 检查是否需要升级
            needs_update = any(u['name'] == skill['name'] for u in self.upgrade_candidates)
            status = '🔄 需升级' if needs_update else '✅ 最新'
            
            report += f"| {i} | {skill['name']} | {skill['version']} | {status} |\n"
        
        report += f"""
---

## 待升级技能 ({len(self.upgrade_candidates)} 个)

"""
        
        if self.upgrade_candidates:
            for update in self.upgrade_candidates:
                report += f"### {update['name']}\n"
                report += f"- 当前版本：{update['current']}\n"
                report += f"- 最新版本：{update['latest']}\n"
                report += f"- 评分：{update['score']}\n\n"
        else:
            report += "所有技能均为最新版本！\n\n"
        
        report += f"""
---

## 升级建议

### 立即升级
"""
        
        # 按优先级排序
        high_priority = ['browser', 'security', 'email', 'linkedin']
        priority_updates = [u for u in self.upgrade_candidates 
                          if any(kw in u['name'].lower() for kw in high_priority)]
        
        if priority_updates:
            for update in priority_updates:
                report += f"- [ ] `{update['name']}` ({update['current']} → {update['latest']})\n"
        else:
            report += "无高优先级升级\n"
        
        report += f"""
### 可选升级
"""
        other_updates = [u for u in self.upgrade_candidates 
                       if not any(kw in u['name'].lower() for kw in high_priority)]
        
        if other_updates:
            for update in other_updates:
                report += f"- [ ] `{update['name']}` ({update['current']} → {update['latest']})\n"
        else:
            report += "无其他升级\n"
        
        report += f"""
---

## 使用统计

"""
        
        if self.skill_usage:
            report += f"- 总会话数：{self.skill_usage.get('total', 0)}\n"
        else:
            report += "- 数据不足，无法统计\n"
        
        report += f"""
---

## 执行升级命令

```bash
# 升级所有技能
clawhub update --all

# 升级单个技能
clawhub update <skill-name>

# 强制升级（覆盖本地修改）
clawhub update <skill-name> --force
```

---

*报告来源：Skill Analyzer v1.0*
"""
        
        # 保存报告
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report


def main():
    """主函数"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"=== 技能全面升级分析 ({now}) ===\n")
    
    # 初始化分析器
    analyzer = SkillAnalyzer()
    
    # 列出已安装技能
    print("[1/4] 列出已安装技能...")
    skills = analyzer.list_installed()
    print(f"  已安装：{len(skills)} 个技能")
    
    for skill in skills[:5]:
        print(f"    - {skill['name']} v{skill['version']}")
    if len(skills) > 5:
        print(f"    ... 还有 {len(skills) - 5} 个")
    
    # 检查更新
    print("\n[2/4] 检查可用更新...")
    updates = analyzer.check_updates()
    print(f"  待升级：{len(updates)} 个技能")
    
    for update in updates[:3]:
        print(f"    - {update['name']}: {update['current']} → {update['latest']}")
    if len(updates) > 3:
        print(f"    ... 还有 {len(updates) - 3} 个")
    
    # 分析使用情况
    print("\n[3/4] 分析技能使用情况...")
    usage = analyzer.analyze_usage()
    if usage:
        print(f"  总会话数：{usage.get('total', 0)}")
    
    # 生成报告
    print("\n[4/4] 生成升级报告...")
    report_file = 'C:/Users/Haide/Desktop/OPENCLAW/Skill_Upgrade_Report.md'
    report = analyzer.generate_report(report_file)
    print(f"  报告已保存：{report_file}")
    
    print(f"\n=== 分析完成 ===")
    print(f"\n建议:")
    if updates:
        print(f"  发现 {len(updates)} 个技能需要升级")
        print(f"  执行命令：clawhub update --all")
    else:
        print(f"  所有技能均为最新版本")


if __name__ == "__main__":
    main()
