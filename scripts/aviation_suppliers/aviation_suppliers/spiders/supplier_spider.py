import scrapy

class SupplierSpider(scrapy.Spider):
    name = 'supplier'
    # 示例：抓取测试网站（实际使用时替换为真实供应商目录网址）
    start_urls = [
        'https://quotes.toscrape.com/',  # 测试用，实际可替换为 aviation supplier 目录
    ]
    
    def parse(self, response):
        # 示例：提取名言数据（实际使用时替换为供应商信息）
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }
        
        # 自动翻页
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
