# python 2.7

from time import sleep
import os
import sys
import re
import urlparse
from bs4 import BeautifulSoup as bs

import grabimgurl as gimg
import urlproxy as urlp

image_dir = 'images/'
sleep_between_post = 0
num_limit = 150
max_depth_img_url = 3


# anchor
newer_posts_a_id = 'Blog1_blog-pager-newer-link'
log_gotfn = 'gotpost.log'

class ProbError(Exception):
    pass

class NoTimestampError(ProbError):
    pass
def find_string_div( soup, divclass ):
    list_div = soup.find_all("div", {"class": divclass})
    if len(list_div) > 0:
        return  list_div[0].string

def prob_save_post( soup ):
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
            if 0 == len(p['timestamp']):
                raise NoTimestampError()

            if p['timestamp'] in open(log_gotfn,'r').read(): #skip post already saved
                print 'skip saving ', p['timestamp']
                return

            p['title']= outer.find("h3").string
            hints = p['title'].replace('\r','+')
            hints = hints.replace('\n','+')
            print hints
            p['titlehint'+hints]=''

            p['body']= outer.find("div",{"id":re.compile("^post-body")})

            p['author'] = outer.find("span",{"class":"post-author vcard"}).find("span",{"itemprop":"author"}).find("span",{"itemprop":"name"}).string
        except Exception as e:
            for key in p.keys():
                if 0 == len(p[key]):
                    print 'post missing :', key

        #save post in folder
        subdirname = p['timestamp']
        tgtpath = os.path.join(script_dir, subdirname)
        if not os.path.exists(tgtpath):
            os.makedirs(tgtpath)
        for key in p.keys():
            f = open(os.path.join(tgtpath,key),'w')
            f.write(p[key].encode('utf8'))
            f.close()

        #save images in the post
        save_imgs_in_soup( p['body'] , tgtpath)

    # log save success
    logf  = open(os.path.join(script_dir,log_gotfn),'a')
    logf.write( (p['timestamp']+'\n').encode('utf8') )
    logf.write( (p['title']+'\n').encode('utf8') )
    logf.close()

def save_imgs_in_soup( soup, todir):
    '''try to get original img, fall back to direct img'''
    imglist = soup("img")
    if len(imglist) == 0:
        return

    imgpath = os.path.join(todir, image_dir)
    if not os.path.exists(imgpath):
        os.makedirs(imgpath)

    for img in imglist:
        try:
            ourl = img.parent.get('href')
            ofn = os.path.join(imgpath,'o'+ ourl.split('/')[-1])
            gimg.save_img_in_url(ourl,ofn,max_depth_img_url)
        except:
            print '[fail orig img]', ourl
            try:
                surl = img['src']
                sfn = os.path.join(imgpath,'s'+ surl.split('/')[-1])
                gimg.save_img_in_url(surl,sfn,max_depth_img_url)
            except gimg.GrabImgError as e:
                print '[faild img]',surl
                print e


def newer_page( soup ):
    try:
        url = soup('a', id=newer_posts_a_id)[0].get('href')
        return url
    except:
        return None

def main(url):
    step = 1
    while url:
        print
        print 'step',step
        print 'page',url

        soup = bs(urlp.fetch_url(url))
        try:
            prob_save_post(soup)
        except NoTimestampError:
            print 'missing timestamp', url

        step = step + 1
        if (step > num_limit):
            break

        url = newer_page( soup )
        if ( url is None ):
                break

        sleep(sleep_between_post)

if __name__ == '__main__':
    url = sys.argv[-1]
    if not url.lower().startswith('http'):
            print 'use http://...'
    main(url)
