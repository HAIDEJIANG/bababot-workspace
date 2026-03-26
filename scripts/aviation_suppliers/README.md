# Scrapy 航空供应商爬虫使用指南

## ✅ 安装完成
- **Scrapy 版本**: v2.14.2
- **安装位置**: Python 3.13 用户环境
- **测试时间**: 2026-03-26 12:15

## 📊 性能测试结果
- **测试网站**: quotes.toscrape.com（官方测试站点）
- **抓取速度**: 11 秒抓取 10 个页面，共 100 条数据
- **并发性能**: ~545 条/分钟（约 9 条/秒）
- **对比**: 比单线程 requests 快 5-10 倍

## 📁 项目结构
```
scripts/aviation_suppliers/
├── aviation_suppliers/
│   ├── __init__.py
│   ├── items.py          # 定义数据结构
│   ├── middlewares.py    # 中间件（反爬/代理）
│   ├── pipelines.py      # 数据处理（存数据库/CSV）
│   ├── settings.py       # 配置文件
│   └── spiders/
│       ├── __init__.py
│       └── supplier_spider.py  # 爬虫代码
├── scrapy.cfg            # 项目配置
└── test_output.json      # 测试输出
```

## 🚀 快速开始

### 1. 修改爬虫目标
编辑 `scripts/aviation_suppliers/aviation_suppliers/spiders/supplier_spider.py`：

```python
import scrapy

class SupplierSpider(scrapy.Spider):
    name = 'supplier'
    start_urls = [
        'https://目标网站.com/suppliers',  # 替换为实际供应商目录网址
    ]
    
    def parse(self, response):
        for supplier in response.css('div.supplier-card'):  # 根据实际 HTML 结构调整
            yield {
                'company_name': supplier.css('h2::text').get(),
                'contact': supplier.css('.contact::text').get(),
                'email': supplier.css('.email::text').get(),
                'products': supplier.css('.products::text').getall(),
                'location': supplier.css('.location::text').get(),
            }
        
        # 自动翻页
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

### 2. 定义数据结构（可选）
编辑 `aviation_suppliers/items.py`：

```python
import scrapy

class AviationSupplierItem(scrapy.Item):
    company_name = scrapy.Field()
    contact_person = scrapy.Field()
    email = scrapy.Field()
    phone = scrapy.Field()
    products = scrapy.Field()
    location = scrapy.Field()
    website = scrapy.Field()
```

### 3. 运行爬虫
```powershell
cd scripts/aviation_suppliers

# 输出为 JSON
scrapy crawl supplier -o suppliers.json

# 输出为 CSV（Excel 可打开）
scrapy crawl supplier -o suppliers.csv

# 输出为 JSON Lines（大数据推荐）
scrapy crawl supplier -o suppliers.jl
```

### 4. 高级配置

#### 限速设置（避免打崩目标网站）
编辑 `settings.py`：
```python
DOWNLOAD_DELAY = 1  # 下载延迟（秒）
CONCURRENT_REQUESTS = 16  # 并发请求数
AUTOTHROTTLE_ENABLED = True  # 自动限速
```

#### 添加 User-Agent（反检测）
```python
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
```

#### 使用中间件处理登录/ Cookie
编辑 `middlewares.py` 添加认证逻辑。

## 🎯 适用场景

### ✅ 适合用 Scrapy
- 静态 HTML 页面批量抓取
- 供应商目录/名录采集
- 公开价格数据监控
- 行业数据汇总

### ❌ 不适合用 Scrapy（继续用 Browser Relay）
- 需要登录的网站（LinkedIn、StockMarket.aero）
- 重度 JavaScript 渲染页面
- 需要复杂交互（表单提交、点击、滚动）

## 📝 实际案例：抓取航空供应商名录

假设要抓取 `https://aviation-suppliers.com/directory`：

```python
import scrapy

class AviationSupplierSpider(scrapy.Spider):
    name = 'aviation_supplier'
    start_urls = ['https://aviation-suppliers.com/directory']
    
    def parse(self, response):
        for row in response.css('table.supplier-list tr'):
            yield {
                'company': row.css('td.company a::text').get(),
                'link': row.css('td.company a::attr(href)').get(),
                'location': row.css('td.location::text').get(),
                'products': row.css('td.products::text').get(),
            }
        
        # 翻页
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

## ⚠️ 注意事项

1. **遵守 robots.txt** - Scrapy 会自动检查并遵守
2. **设置合理延迟** - 避免对目标网站造成压力
3. **不要抓取登录后的内容** - 这类用 Browser Relay 更稳定
4. **数据验证** - 使用 `items.py` 定义字段类型
5. **错误处理** - 在 `parse()` 中添加 try/except

## 🔧 常用命令

```powershell
# 查看爬虫列表
scrapy list

# 交互式调试（Shell）
scrapy shell https://example.com

# 检查爬虫输出
scrapy crawl supplier --output-format=json

# 查看日志级别
scrapy crawl supplier -L DEBUG
```

## 📚 学习资源
- 官方文档：https://docs.scrapy.org/
- 中文教程：https://scrapy-chs.readthedocs.io/
- Stack Overflow: https://stackoverflow.com/questions/tagged/scrapy

---

**总结**: Scrapy 已就绪，适合批量抓取静态页面数据。LinkedIn/StockMarket 等需登录场景继续使用 Browser Relay。两者互补，效率最大化 ✈️
