from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector

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
        filename = response.url.split("/")[-2]
        open(filename, 'wb').write(response.body)

    def add_cookie(self, request):
        request.replace(cookies=[
            {'name': 'COOKIE_NAME','value': 'VALUE','domain': '.douban.com','path': '/'},
            ]);
        return request;
