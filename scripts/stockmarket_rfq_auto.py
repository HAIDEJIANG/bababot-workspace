#!/usr/bin/env python3
"""
StockMarket.aero RFQ 自动化脚本
直接通过 HTTP 请求提交 RFQ，跳过浏览器 UI 操作
预计效率提升 10-20 倍
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import csv
import os
import sys
from datetime import datetime

# 修复 Windows 控制台编码
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ===== 配置 =====
BASE_URL = "https://www.stockmarket.aero/StockMarket"
USERNAME = "sale@aeroedgeglobal.com"
PASSWORD = "Aa138222"
RFQ_REFERENCE = "RFQ20260324-02"
RFQ_COMMENTS = "Please quote in USD. Delivery time unit required (e.g., 1D/2W/3M/4Y). Validity period must be specified. Thank you."

# 条件匹配规则（铁律）
NEW_CONDITIONS = {"FN", "NE", "NS"}          # 全新件
SV_CONDITIONS = {"OH", "RP", "SV", "TESTED", "INSPECTED"}  # 可用件
EXCLUDED_CONDITIONS = {"AR", "DIST", "EXCHANGE", "RQST", "REQUEST"}

# 零件清单
PARTS_LIST = [
    # (序号, PN, 描述, 需求条件类型, 数量)
    # 需求条件类型: "new" = 全新件, "sv" = 可用件
    (1, "796880-5-006", "座舱温度控制器", "sv", 1),       # 忽略（已处理）
    (2, "CE2A26", "导线和插座组件", "new", 5),              # 已完成
    (3, "501-1-14713-000", "盖板组件", "new", 2),           # 已完成
    (4, "285N0431-3", "IO 板", "new", 1),                   # 已完成
    (5, "10395N01T00", "涡轮级间温度指示器", "new", 1),
    (6, "08DM15TYP1862", "涡轮级间温度指示器", "new", 1),
    (7, "23080-1035-503", "卡箍", "new", 3),
    (8, "PDCR330-3185", "传感器", "new", 3),
    (9, "042147-4", "连接器", "new", 3),
    (10, "42-767-1", "防滑/自动刹车控制组", "sv", 1),       # 已完成
    (11, "277-0859-030", "IC", "new", 4),
    (12, "277-0859-050", "IC", "new", 4),
    (13, "ROS-100-5RM", "IC", "new", 4),
    (14, "ROS-310-7", "IC", "new", 4),
    (15, "STD3359-2", "变压器", "new", 1),                   # 已完成
    (16, "2117388-15", "座舱压力控制器", "sv", 1),           # 已完成
    (17, "2117388-11", "座舱压力控制器", "sv", 1),           # 已完成
    (18, "2117388-12", "座舱压力控制器", "sv", 1),
    (19, "183-1524-020", "电容", "new", 10),
    (20, "DNN3551B", "壳体", "new", 1),
    (21, "966-3138-001", "电路板", "new", 10),
    (22, "98-0976", "电路板", "new", 1),
    (23, "2156-604A", "烟雾探测器", "sv", 1),
    (24, "98-1122", "LED", "new", 2),
    (25, "7743-00361-04", "公共服务板", "new", 1),
    (26, "49-170-11", "襟翼缝翼控制计算机", "sv", 1),
    (27, "2G916-1039", "控制面板", "new", 1),
    (28, "2G916-2501", "电路板", "new", 1),
    (29, "42-767191", "PCA", "new", 1),
    (30, "814462-1", "旋钮开关", "new", 3),
    (31, "433-673-1004-4061", "开关", "new", 1),
    (32, "433-673-1004-4060", "开关", "new", 1),
    (33, "433-673-1004-4062", "开关", "new", 1),
    (34, "TS30176", "弹簧", "new", 5),
    (35, "0248001981", "IC", "new", 20),
    (36, "IDT74FCT162646CTPV", "IC", "new", 20),
    (37, "RDX-7708CRW", "测试设备", "sv", 1),
    (38, "RDX-7708BRW", "测试设备", "sv", 1),
    (39, "5DV411474-10", "点火装置组件", "new", 5),
    (40, "H150AK26", "平衡块", "new", 1),
    (41, "822-0990-002", "HF 收发机", "sv", 1),
    (42, "822-0990-003", "HF 收发机", "sv", 1),
]

# 已完成的 PN（跳过）
COMPLETED_PNS = {
    "796880-5-006",   # PN1 忽略
    "CE2A26",          # PN2 已完成
    "501-1-14713-000", # PN3 已完成
    "285N0431-3",      # PN4 已完成
    "42-767-1",        # PN10 已完成
    "STD3359-2",       # PN15 已完成
    "2117388-15",      # PN16 已完成
    "2117388-11",      # PN17 已完成
}


class StockMarketRFQ:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False  # StockMarket.aero SSL 证书问题
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8",
        })
        self.logged_in = False
        self.results = []
        self.log_file = os.path.join(os.path.dirname(__file__), "..", "rfq_auto_log.csv")

    def login(self):
        """登录 StockMarket.aero"""
        print(f"[LOGIN] 正在登录 {USERNAME}...")
        login_url = f"{BASE_URL}/LoadLogin.do"
        
        # 先获取登录页面（获取 cookies）
        resp = self.session.get(login_url, timeout=30)
        print(f"  GET login page: {resp.status_code}")
        
        # 解析登录表单（获取 action URL 和隐藏字段）
        soup = BeautifulSoup(resp.text, "html.parser")
        form = soup.find("form")
        form_action = form.get("action") if form else "/StockMarket/LoginAction.do"
        
        login_data = {
            "username": USERNAME,
            "password": PASSWORD,
            "rememberMe": "on",
            "group1": "signIn",
        }
        
        post_url = f"https://www.stockmarket.aero{form_action}"
        resp = self.session.post(post_url, data=login_data, timeout=30, allow_redirects=True)
        print(f"  POST login: {resp.status_code}, URL: {resp.url}")
        
        if USERNAME in resp.text:
            self.logged_in = True
            print(f"  [OK] Login success")
            return True
        
        print(f"  [FAIL] Login failed")
        return False

    def search_part(self, part_number):
        """搜索零件号，返回供应商列表"""
        search_url = f"{BASE_URL}/SearchAction.do"
        params = {
            "theAction": "",
            "partNumber": part_number,
            "partial": "false",
        }
        
        try:
            resp = self.session.get(search_url, params=params, timeout=30)
            if resp.status_code != 200:
                print(f"    搜索失败: HTTP {resp.status_code}")
                return []
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # 检查是否有结果
            no_results = soup.find("h3", string=lambda s: s and "0" in s and "results" in s)
            if no_results:
                return []
            
            return self._parse_vendors(soup, part_number)
        except Exception as e:
            print(f"    搜索异常: {e}")
            return []

    def _parse_vendors(self, soup, part_number):
        """解析供应商列表，提取 vendor 名称和库存条件"""
        vendors = []
        
        # 找到所有行
        rows = soup.find_all("tr")
        current_vendor = None
        
        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue
            
            # 检查是否是供应商行（包含 PN 和 Qty）
            cell_texts = [c.get_text(strip=True) for c in cells]
            
            # 供应商名称行（有 vendor name + PN + qty + location）
            if len(cells) >= 4:
                pn_cell = None
                qty_cell = None
                
                for i, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    if text == part_number and i > 0:
                        pn_cell = i
                    if pn_cell and i == pn_cell + 1:
                        qty_cell = text
                
                if pn_cell and qty_cell:
                    vendor_name = cells[0].get_text(strip=True)
                    # 清理 vendor name（移除认证信息）
                    for cert in ["This vendor has been", "European Commission", "Lists Alternates", "View Images"]:
                        if cert in vendor_name:
                            vendor_name = vendor_name[:vendor_name.index(cert)].strip()
                    
                    qty_text = qty_cell
                    capability = cells[pn_cell + 2].get_text(strip=True) if len(cells) > pn_cell + 2 else ""
                    location = cells[pn_cell + 3].get_text(strip=True) if len(cells) > pn_cell + 3 else ""
                    
                    if qty_text not in ("RQST", ""):
                        current_vendor = vendor_name
            
            # 检查展开后的条件行（Part Number | Description | Qty | Cond | Send RFQ）
            if len(cells) == 7:
                pn_text = cells[0].get_text(strip=True)
                desc = cells[1].get_text(strip=True)
                qty = cells[2].get_text(strip=True)
                cond = cells[3].get_text(strip=True)
                
                if pn_text == part_number and cond:
                    # 找到 Send RFQ 链接
                    send_link = cells[4].find("a")
                    send_onclick = ""
                    if send_link and send_link.get("onclick"):
                        send_onclick = send_link["onclick"]
                    
                    vendors.append({
                        "vendor": current_vendor or "Unknown",
                        "pn": pn_text,
                        "description": desc,
                        "qty": qty,
                        "condition": cond.upper(),
                        "send_onclick": send_onclick,
                    })
        
        return vendors

    def expand_vendor_and_get_details(self, part_number):
        """使用 Expand All 获取所有供应商的条件详情"""
        # 先搜索
        search_url = f"{BASE_URL}/SearchAction.do"
        params = {
            "theAction": "",
            "partNumber": part_number,
            "partial": "false",
        }
        
        try:
            resp = self.session.get(search_url, params=params, timeout=30)
            if resp.status_code != 200:
                return [], False
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # 检查是否有结果
            no_results = soup.find("h3", string=lambda s: s and "0" in str(s) and "results" in str(s))
            if no_results:
                return [], True
            
            # 尝试 Expand All
            expand_url = f"{BASE_URL}/SearchAction.do"
            expand_params = {
                "theAction": "expandAll",
                "partNumber": part_number,
                "partial": "false",
            }
            resp2 = self.session.get(expand_url, params=expand_params, timeout=30)
            if resp2.status_code == 200:
                soup = BeautifulSoup(resp2.text, "html.parser")
            
            # 解析所有库存条目
            entries = []
            rows = soup.find_all("tr")
            current_vendor = None
            current_location = ""
            
            for row in rows:
                cells = row.find_all("td")
                if not cells:
                    continue
                
                cell_texts = [c.get_text(strip=True) for c in cells]
                
                # 7 列行 = 库存条目行（PN | Desc | Qty | Cond | Send RFQ | Buy Now | Place PO）
                if len(cells) == 7 and cells[0].get_text(strip=True) == part_number:
                    cond = cells[3].get_text(strip=True).upper()
                    qty = cells[2].get_text(strip=True)
                    desc = cells[1].get_text(strip=True)
                    
                    # 获取 Send RFQ 的表单信息
                    send_cell = cells[4]
                    
                    if cond and cond not in ("COND", "SEND RFQ"):
                        entries.append({
                            "vendor": current_vendor or "Unknown",
                            "location": current_location,
                            "pn": part_number,
                            "description": desc,
                            "qty": qty,
                            "condition": cond,
                        })
                
                # 供应商名称行（通常有 4-5 列，包含 vendor name, PN, Qty, Capability, Location）
                elif len(cells) >= 4:
                    for i, cell in enumerate(cells):
                        if cell.get_text(strip=True) == part_number and i > 0:
                            vendor_text = cells[0].get_text(strip=True)
                            # 清理
                            for cert in ["This vendor has been", "European Commission", "Lists Alternates", "View Images", "This vendor is displaying"]:
                                idx = vendor_text.find(cert)
                                if idx > 0:
                                    vendor_text = vendor_text[:idx].strip()
                            current_vendor = vendor_text
                            
                            # Location
                            if len(cells) > i + 3:
                                current_location = cells[i + 3].get_text(strip=True)
                            elif len(cells) > i + 2:
                                current_location = cells[i + 2].get_text(strip=True)
                            break
            
            return entries, True
            
        except Exception as e:
            print(f"    异常: {e}")
            return [], False

    def send_rfq(self, vendor_key, part_number, condition, qty):
        """
        发送 RFQ
        StockMarket.aero 的 RFQ 提交需要特定的表单参数
        """
        # 尝试通过搜索结果页面直接找到供应商的 RFQ 表单
        # 这需要先展开供应商，然后点击 Send RFQ
        # 由于是 AJAX 表单，需要找到正确的提交 URL
        
        # StockMarket 的 RFQ 提交 URL
        rfq_url = f"{BASE_URL}/SendRFQAction.do"
        
        rfq_data = {
            "partNumber": part_number,
            "condition": condition,
            "referenceNumber": RFQ_REFERENCE,
            "quantity": str(qty),
            "priority": "ROUTINE",
            "comments": RFQ_COMMENTS,
        }
        
        try:
            resp = self.session.post(rfq_url, data=rfq_data, timeout=30)
            if resp.status_code == 200 and "sent successfully" in resp.text.lower():
                return True
            else:
                return False
        except Exception as e:
            print(f"    RFQ 发送异常: {e}")
            return False

    def process_part(self, idx, pn, desc, cond_type, qty):
        """处理单个零件号"""
        print(f"\n[PN {idx}] {pn} | {desc} | {'全新件' if cond_type == 'new' else '可用件'} | x{qty}")
        
        # 确定匹配条件
        if cond_type == "new":
            valid_conditions = NEW_CONDITIONS
        else:
            valid_conditions = SV_CONDITIONS
        
        # 搜索并获取所有库存条目
        entries, searched = self.expand_vendor_and_get_details(pn)
        
        if not searched:
            print(f"  ⚠️ 搜索失败，跳过")
            self.results.append((idx, pn, desc, "搜索失败", 0, ""))
            return
        
        if not entries:
            print(f"  ❌ 无库存")
            self.results.append((idx, pn, desc, "无库存", 0, ""))
            return
        
        # 筛选匹配条件的供应商
        matched = [e for e in entries if e["condition"] in valid_conditions]
        excluded = [e for e in entries if e["condition"] in EXCLUDED_CONDITIONS]
        
        print(f"  总库存: {len(entries)} | 匹配: {len(matched)} | 排除: {len(excluded)}")
        
        if not matched:
            all_conds = set(e["condition"] for e in entries)
            print(f"  ❌ 无匹配条件 (库存条件: {all_conds})")
            self.results.append((idx, pn, desc, f"无匹配条件({all_conds})", 0, ""))
            return
        
        # 去重（同一供应商只发一次）
        seen_vendors = set()
        unique_matched = []
        for e in matched:
            if e["vendor"] not in seen_vendors:
                seen_vendors.add(e["vendor"])
                unique_matched.append(e)
        
        # 最多发 10 家
        to_send = unique_matched[:10]
        
        sent_count = 0
        sent_vendors = []
        for e in to_send:
            print(f"    → {e['vendor']} | {e['condition']} | Qty: {e['qty']} | {e.get('location', '')}")
            # 记录（实际发送需要完整的表单参数，先记录）
            sent_vendors.append(f"{e['vendor']}({e['condition']})")
            sent_count += 1
        
        self.results.append((idx, pn, desc, "有匹配", sent_count, "; ".join(sent_vendors)))
        print(f"  ✅ 找到 {sent_count} 家匹配供应商")

    def run(self, start_from=18):
        """执行全部零件的 RFQ 流程"""
        print("=" * 60)
        print(f"StockMarket.aero RFQ 自动化脚本")
        print(f"RFQ 编号: {RFQ_REFERENCE}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"从 PN {start_from} 开始执行")
        print("=" * 60)
        
        # 登录
        if not self.login():
            print("登录失败，退出")
            return
        
        # 处理每个零件
        for idx, pn, desc, cond_type, qty in PARTS_LIST:
            # 跳过已完成的
            if pn in COMPLETED_PNS:
                print(f"\n[PN {idx}] {pn} - 已完成，跳过")
                continue
            
            # 跳过指定序号之前的
            if idx < start_from:
                continue
            
            self.process_part(idx, pn, desc, cond_type, qty)
            time.sleep(1)  # 请求间隔，避免被封
        
        # 输出汇总
        self._print_summary()
        self._save_log()

    def _print_summary(self):
        """打印汇总报告"""
        print("\n" + "=" * 60)
        print("执行汇总")
        print("=" * 60)
        
        total = len(self.results)
        has_match = sum(1 for r in self.results if r[3] == "有匹配")
        no_stock = sum(1 for r in self.results if r[3] == "无库存")
        no_match = sum(1 for r in self.results if "无匹配" in r[3])
        total_rfq = sum(r[4] for r in self.results)
        
        print(f"总查询: {total} 个 PN")
        print(f"有匹配: {has_match} 个 PN")
        print(f"无库存: {no_stock} 个 PN")
        print(f"无匹配条件: {no_match} 个 PN")
        print(f"匹配供应商总数: {total_rfq}")
        
        print(f"\n详细结果:")
        for idx, pn, desc, status, count, vendors in self.results:
            print(f"  PN {idx}: {pn} | {status} | {count} 家 | {vendors[:80]}")

    def _save_log(self):
        """保存日志到 CSV"""
        try:
            with open(self.log_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["序号", "件号", "描述", "状态", "匹配供应商数", "供应商列表"])
                for row in self.results:
                    writer.writerow(row)
            print(f"\n日志已保存: {self.log_file}")
        except Exception as e:
            print(f"保存日志失败: {e}")


if __name__ == "__main__":
    bot = StockMarketRFQ()
    # 从 PN 18 开始（1-17 已手动完成）
    bot.run(start_from=18)
