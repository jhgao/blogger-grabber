# python 2.7

import os
import sys
import random
import re
import urllib2
import urlparse
from bs4 import BeautifulSoup as bs

# proxy dict for urllib2
proxy_dict = {'http': '127.0.0.1:8087','https': '127.0.0.1:8087'}
image_dir = 'images/'

# anchor
newer_posts_a_id = 'Blog1_blog-pager-newer-link'
deep_limit = 2
log_gotfn = 'gotpost.log'

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

def find_string_div( soup, divclass ):
    list_div = soup.find_all("div", {"class": divclass})
    if len(list_div) > 0:
        return  list_div[0].string

class post:
    p = {'title':'','body':'','author':'','timestamp':''}

def save_posts( soup ):
    # touch log file
    script_dir = os.path.dirname(__file__)
    logf  = open(os.path.join(script_dir,log_gotfn),'a')
    logf.close()
    
    # save post in to dirs
    p = {'title':'','body':'','author':'','timestamp':''}
    list_div_outer = soup("div", {"class": "post-outer"})
    for outer in list_div_outer:
        try:
            p['timestamp'] = outer.find("abbr",{"itemprop":"datePublished"})['title']
        except:
            print "except:timestamp"
        ## if already got this post
        if p['timestamp'] in open(log_gotfn,'r').read():
            print 'skip saving ', p['timestamp']
            return
        
        try:
            p['title']= outer.find("h3").string
        except AttributeError as e:
            print 'title',"AttributeError",e
        try:
            p['body']= outer.find("div",{"id":re.compile("^post-body")})
        except :
            print 'body',"IndexError",e
        try:
            p['author'] = outer.find("span",{"class":"post-author vcard"}).find("span",{"itemprop":"author"}).find("span",{"itemprop":"name"}).string
        except AttributeError as e:
            print "author","AttributeError",e
        for key in p.keys():
            print key,p[key]

        #save to folder, one by each post
        subdirname = p['timestamp']
        tgtpath = os.path.join(script_dir, subdirname)
        if not os.path.exists(tgtpath):
            os.makedirs(tgtpath)
        for key in p.keys():
            f = open(os.path.join(tgtpath,key),'w')
            f.write(p[key].encode('utf8'))
            f.close()
        #save images
        save_imgs( p['body'] , tgtpath)

    # log save success
    logf  = open(os.path.join(script_dir,log_gotfn),'a')
    logf.write( (p['timestamp']+'\n').encode('utf8') )
    logf.write( (p['title']+'\n').encode('utf8') )
    logf.close()


def save_imgs( soup, path ):
    imglist = soup("img")
    if len(imglist) == 0:
        return

    imgpath = os.path.join(path, image_dir)
    if not os.path.exists(imgpath):
        os.makedirs(imgpath)

    for img in imglist:
        url = img['src']
        fn = url.split('/')[-1]
        tgt = os.path.join(imgpath, fn)
        with open(tgt,'wb') as imgf:
            imgf.write(urllib2.urlopen(url).read())
            imgf.close()

def newer_page( soup ):
    linklist = soup.find_all('a', id=newer_posts_a_id)
    if len(linklist) > 0:
        newer_posts = linklist[0].get('href')
    if newer_posts is None:
        return
    else:
        url = newer_posts
    return url

def main(url):
    # proxy for urllib2
    proxyHandler = urllib2.ProxyHandler(proxy_dict)
    opener = urllib2.build_opener(proxyHandler)
    urllib2.install_opener(opener)
    depth = 1

    while url:
        print
        print '[page]',url
        # send the request with a random user agent in the header
        request = urllib2.Request(url, None, randomize_user_agent())
        html = urllib2.urlopen(request)

        soup = bs(html)
        save_posts(soup)

        url = newer_page( soup )
        if ( url is None ) or ( depth > deep_limit ):
                break
        depth = depth + 1

if __name__ == '__main__':
    url = sys.argv[-1]
    if not url.lower().startswith('http'):
            print 'use http://...'
    main(url)
