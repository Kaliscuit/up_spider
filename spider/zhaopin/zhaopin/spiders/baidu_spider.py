#coding=utf-8
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from zhaopin.items import ZhaopinItem
import re


import re
##过滤HTML中的标签
#将HTML中标签等信息去掉
#@param htmlstr HTML字符串.
def filter_tags(htmlstr):
    #先过滤CDATA
    re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?\w+[^>]*>')#HTML标签
    re_xml=re.compile('<?xml[^>]*>')#XML标签
    re_comment=re.compile('<!--[^>]*-->')#HTML注释
    s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_xml.sub('',s) #去掉XML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    s=replaceCharEntity(s)#替换实体
    return s

##替换常用HTML字符实体.
#使用正常的字符替换HTML中特殊的字符实体.
#你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
#@param htmlstr HTML字符串.
def replaceCharEntity(htmlstr):
    CHAR_ENTITIES={'nbsp':' ','160':' ',
                'lt':'<','60':'<',
                'gt':'>','62':'>',
                'amp':'&','38':'&',
                'quot':'"','34':'"',}

    re_charEntity=re.compile(r'&#?(?P<name>\w+);')
    sz=re_charEntity.search(htmlstr)
    while sz:
        entity=sz.group()#entity全称，如&gt;
        key=sz.group('name')#去除&;后entity,如&gt;为gt
        try:
            htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
            sz=re_charEntity.search(htmlstr)
        except KeyError:
            #以空串代替
            htmlstr=re_charEntity.sub('',htmlstr,1)
            sz=re_charEntity.search(htmlstr)
    return htmlstr

def repalce(s,re_exp,repl_string):
    return re_exp.sub(repl_string,s)


class BaiduSpider(CrawlSpider):
    name = 'baidu'
    start_urls = ['http://talent.baidu.com/baidu/web/templet1000/index/corpwebPosition1000baidu!getPostListByConditionBaidu?positionType=0&brandCode=1&releaseTime=0&trademark=0&useForm=0&recruitType=2&lanType=&keyWord=&workPlaceCode=&request_locale=zh_CN']
    allowed_domains = ['baidu.com']
    rules = (
            Rule(SgmlLinkExtractor(allow=r'*getOnePosition*', tags='a'), callback='parse_item', follow = True),
            Rule(SgmlLinkExtractor(allow=(r'*getPostListByConditionBaidu*', )), follow=True, process_request='add_cookie'),
            )

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        item = ZhaopinItem()
        item['position'] = ''.join(''.join(hxs.select('//*[@id="hrs_searchOuter"]/h4').select('text()').extract()).split())
        item['company'] = '百度在线网络技术'.join(''.join(hxs.select('//*[@id="hrs_jobDetail"]/dl[1]/dd[1]').select('text()').extract()).split())
        item['time'] = ''.join(''.join(hxs.select('//*[@id="span4freshdate"]').select('text()').extract()).split())
        item['position_desc'] = ''.join(''.join(hxs.select('//*[@id="hrs_jobDetail"]/dl[2]/div').extract()).split())
        item['company_homepage'] = 'http://www.baidu.com'
        item['company_address'] = ''.join(''.join(hxs.select('//*[@id="hrs_jobDetail"]/dl[1]/dd[2]/font').extract()).split())
        item['company_desc'] = ''.join(''.join(hxs.select('//*[@id="hrs_jobDetail"]/dl[3]/div').extract()).split())
        item['url'] = response.url
        for i in item:
            item[i] = filter_tags(item[i])
            # item[i] = re.sub(r'</?\w+[^>]*>','',item[i]).encode('utf-8')
        # if(item['company_homepage'].startswith('公司主页：')):
            # item['company_homepage'] = item['company_homepage'].replace('公司主页：', '')

        return item


    def add_cookie(self, request):
        request.replace(cookies=[
            {'name': 'COOKIE_NAME','value': 'VALUE','domain': '.douban.com','path': '/'},
            ]);
        return request;