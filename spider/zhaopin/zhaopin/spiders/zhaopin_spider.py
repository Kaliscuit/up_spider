from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from zhaopin.items import ZhaopinItem

class ZhaopinSpider(CrawlSpider):
    name = 'zhaopin'
    #start_urls = ['http://jobs.zhaopin.com']
    start_urls = ['http://sou.zhaopin.com/jobs/searchresult.ashx?bj=160000&sj=045']
    allowed_domains = ['zhaopin.com']
    rules = (
            Rule(SgmlLinkExtractor(allow=r'jobs.zhaopin.com/.*\.htm', tags='a'), callback='parse_item', follow = True),
            Rule(SgmlLinkExtractor(allow=('sou.zhaopin.com/jobs/', )), follow=True, process_request='add_cookie'),
            )

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        item = ZhaopinItem()
        item['position'] = ''.join(''.join(hxs.select('/html/body/div[3]/div[1]/div[1]/div[1]/table[1]/tr[1]/td/h1').select('text()').extract()).split())
        item['company'] = ''.join(''.join(hxs.select('/html/body/div[3]/div[1]/div[1]/div[1]/table[1]/tr[2]/td/h2/a').select('text()').extract()).split())
        item['time'] = ''.join(''.join(hxs.select('//*[@id="span4freshdate"]').select('text()').extract()).split())
        item['description'] = ''.join(''.join(hxs.select('/html/body/div[3]/div[1]/div[2]/div[2]').select('text()').extract()).split())
        item['url'] = response.url
        return item


    def add_cookie(self, request):
        request.replace(cookies=[
            {'name': 'COOKIE_NAME','value': 'VALUE','domain': '.douban.com','path': '/'},
            ]);
        return request;
