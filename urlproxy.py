import random
import urllib2

# proxy dict for urllib2
proxy_dict = {'http': '127.0.0.1:8087','https': '127.0.0.1:8087'}

# proxy for urllib2
proxyHandler = urllib2.ProxyHandler(proxy_dict)
opener = urllib2.build_opener(proxyHandler)
urllib2.install_opener(opener)

def randomize_user_agent():
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17',
        'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
        'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))',
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.2; SV1; .NET CLR 3.3.69573; WOW64; en-US)'
    ]

    return {'User-Agent': random.choice(user_agents)}

def fetch_url(url):
    request = urllib2.Request(url, None, randomize_user_agent())
    return urllib2.urlopen(request)

