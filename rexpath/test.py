from . import TextResponse
import requests
r = requests.get('http://www.baidu.com')
response = TextResponse(r.url, body = r.text, encoding = 'utf-8')
response.xpath('.//script/text()').extract()