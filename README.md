# The Usage of Google Scholar

```python
from googlescholar import Scholar
AlanWang = Scholar()
AlanWang = Scholar('https://scholar.google.com/citations?user=onKvwjAAAAAJ&hl=en&oi=ao')
AlanWang.keywords
```



## a look at rexpath
```python
from rexpath import TextResponse
import requests
r = requests.get('http://www.baidu.com')
response = TextResponse(r.url, body = r.text, encoding = 'utf-8')
response.xpath('.//script/text()').extract()
```
