#coding=utf-8
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.http import TextResponse
from zhaopin.items import ZhaopinItem
import re
import urllib2
import sys


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
    # start_urls = ['http://talent.baidu.com/baidu/web/templet1000/index/corpwebPosition1000baidu!getPostListByConditionBaidu?pc.currentPage=1&pc.rowSize=1680&releaseTime=&keyWord=&positionType=&trademark=1&workPlaceCode=&positionName=&recruitType=2&brandCode=1&searchType=1&workPlaceNameV=&positionTypeV=&keyWordV=']
    start_urls = ['http://talent.baidu.com/baidu/web/templet1000/index/corpwebPosition1000baidu!getPostListByConditionBaidu?positionType=0/1227/10002&brandCode=1&releaseTime=0&trademark=0&useForm=0&recruitType=2&lanType=&workPlaceCode=&keyWord=&request_locale=zh_CN&pc.currentPage=1&pc.rowSize=2000']
    allowed_domains = ['baidu.com']
    # rules = (
            # Rule(SgmlLinkExtractor(allow=r'.*getOnePosition.*', tags='a'), callback='parse_item', follow = True),
            # Rule(SgmlLinkExtractor(allow=(r'.*getPostListByConditionBaidu.*', )), follow=True, process_request='process'),
            # )

    def process(self, url):
        response = urllib2.urlopen(url)
        html = response.read()
        hxs = HtmlXPathSelector(text=html)
        item = {}
        item['position_desc'] = ''.join(''.join(hxs.select('//*[@id="hrs_jobDetail"]/dl[2]/div').extract()).split())
        item['requirements'] = ''.join(''.join(hxs.select('//*[@id="hrs_jobDetail"]/dl[3]/div').extract()).split())
        return item


    def parse(self, response):
        
        hxs = HtmlXPathSelector(response)
        items = []
        names = hxs.select('//*[@id="hrs_joblistTable"]/tbody/tr[position()>0]/td[1]/a/text()').extract()
        urls = hxs.select('//*[@id="hrs_joblistTable"]/tbody/tr[position()>0]/td[1]/a/@href').extract() 
        times = hxs.select('//*[@id="hrs_joblistTable"]/tbody/tr[position()>0]/td[4]/text()').extract() 
        regions = hxs.select('//*[@id="hrs_joblistTable"]/tbody/tr[position()>0]/td[3]/span/@title').extract() 
        
        for i in range(0, len(names)):
            print i, names[i].encode("utf-8")
            item = ZhaopinItem()
            try:
                item['position'] = names[i].split('_')[1].encode("utf-8")
                item['company'] = '百度在线网络技术' + names[i].split('_')[0].encode("utf-8")
            except:
                try:
                    item['position'] = names[i].split('-')[1].encode("utf-8")
                    item['company'] = '百度在线网络技术' + names[i].split('-')[0].encode("utf-8")
                except:
                    item['position'] = names[i].encode("utf-8")
                    item['company'] = '百度在线网络技术'
            item['time'] = times[i].encode("utf-8")
            item['url'] = 'http://talent.baidu.com' + urls[i].encode("utf-8")
            item['company_address'] = regions[i].encode("utf-8")
            item['company_homepage'] = 'http://www.baidu.com'
            item_request = self.process(item['url'])
            item['position_desc'] = item_request['position_desc']
            item['requirements'] = item_request['requirements']
            item['company_desc'] = '百度，全球最大的中文搜索引擎、最大的中文网站。'
            for i in item:
                item[i] = filter_tags(item[i]).strip()
            items.append(item)
        return items


    
