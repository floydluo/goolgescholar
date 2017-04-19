from rexpath import TextResponse
import requests
import re
import json

class GoogleScholar(object):
    baseurl = 'https://scholar.google.com'
    headers = { "Connection": "keep-alive",
                "Cache-Control": "max-age=0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36",
                "Accept-Encoding": "gzip,deflate,sdch",
                "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2" }
    
    def request(self, url):
        r = requests.get(url, headers = self.headers)      
        return TextResponse(r.url, body = r.text, encoding = 'utf-8')   
        
    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
    
    
class Scholar(GoogleScholar):
    gs_id = None
    url = None
    name = None
    avatar = None
    homepage = None  # mark   
    position = None
    organization = None   
    org_url = None   # mark
    coauth_url = None
    article_urls = None  
    keywords = None  # mark
    stats = None
    
    def __init__(self, url):
        self.url = url
        self.getProfile()
    
    
    def getProfile(self):
        # get a Scrapy-like Response
        response = self.request(self.url + '&pagesize=100')
        # gs_id
        # self.gs_id = response.xpath().extract()[0]
        # fullname
        self.name = response.xpath('.//div[@id="gsc_prf_in"]/text()').extract()[0]
        # avatar
        self.avatar = self.baseurl + response.xpath('.//img[@id="gsc_prf_pup"]/@src').extract()[0]
        # position
        self.position = response.xpath('.//div[@class="gsc_prf_il"][1]/text()').extract()[0]
        # organization
        self.organization = response.xpath('.//div[@class="gsc_prf_il"][1]/a/text()').extract()[0]
        # org_url
        self.org_url = self.baseurl + response.xpath('.//div[@class="gsc_prf_il"][1]/a/@href').extract()[0]
        # homepage
        self.homepage = response.xpath('.//div[@id="gsc_prf_ivh"]/a/@href').extract()[0]
        # article_urls
        self.article_urls =[ self.baseurl + i for i in response.xpath('.//tr[@class="gsc_a_tr"]/td[@class="gsc_a_t"]/a/@href').extract()]
        # keywords
        self.keywords = response.xpath('.//div[@class="gsc_prf_il"][2]/a/text()').extract()
        # coauth_url 
        self.coauth_url = self.baseurl + response.xpath('.//div[@id="gsc_rsb_co"]/h3/a/@href').extract()[0]
        
    def getStats(self, **kw_arg):
        a = {}
        a["article_number"] = len(self.article_urls)
        
        '''
        Something need to add
        '''
        self.stats =a
        

class Document(GoogleScholar):
    authors = None
    description = None
    issue = None
    journal = None
    pages = None
    publication_date = None
    publisher = None
    title = None
    citations = None
    volume = None
    
    def __init__(self, url):
        self.url = url
        self.getProfile()
    
    def getProfile(self):
        response = self.request(self.url)
        
        fields = [i.lower()  for i in response.xpath('.//div[@class="gsc_field"]/text()').extract()][:7]
        values = response.xpath('.//div[@class="gsc_value"]/text()').extract()[:7]    
        self.__dict__.update(**dict(zip(fields, values)))
       
        # abstract
        self.abstract = self.cleanhtml(response.xpath('.//div[@id="gsc_descr"]').extract()[0].replace('\n',''))
        years = response.xpath('.//span[@class="gsc_g_t"]/text()').extract()
        citations = response.xpath('.//span[@class="gsc_g_al"]/text()').extract()
        # citation
        self.citation = json.dumps(dict(zip(years, citations)))
        #title
        self.title = response.xpath('.//a[@class="gsc_title_link"]/text()').extract()[0]
        
#TODO

def Coauth(GoogleScholar):
    pass