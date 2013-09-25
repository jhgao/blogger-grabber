import urllib2
from bs4 import BeautifulSoup as bs

class Error(Exception):
    pass

class OpenUrlError(Error):
    def __init__(self, url, msg):
        self.url = url
        self.msg = msg

class TooDeepError(Error):
    def __init__(self, maxdeep):
        self.maxdeep = maxdeep

class ImgNotFoundError(Error):
    def __init__(self, url, msg):
        self.url = url
        self.msg = msg
        
def save_img_in_url(url, fn='tempimg', maxdepth=1, currentdepth=1, proxy_dict={}, user_agent=[] ):
    try:
        if currentdepth > maxdepth:
            raise TooDeepError( maxdepth )
        # proxy for urllib2
        proxyHandler = urllib2.ProxyHandler(proxy_dict)
        opener = urllib2.build_opener(proxyHandler)
        urllib2.install_opener(opener)
 
        # get url
        request = urllib2.Request(url, None, user_agent)
        goturl = urllib2.urlopen(request)

        # check type and save
        if 'image' ==  goturl.info().getmaintype():
            with open(fn,'wb') as f:
                f.write(urllib2.urlopen(url).read())
                f.close()
                dmsg('saved img:'+url)

        elif 'text/html' == goturl.info().gettype():
            imglist = bs(goturl)('img')
            if len(imglist) > 0:
                for img in imglist:
                    save_img_in_url(img['src'], fn, maxdepth, currentdepth+1)
            else:
                dmsg("no img found")
                raise ImgNotFoundError( url, "no img found in the given url" )

        else:
            raise OpenUrlError(url,'unknown type' + goturl.info().gettype())

    except Exception as e:
        logfn = fn+'.saveerror'
        l = open(logfn,'w')
        l.write(url)
        l.close()
        raise e

def dmsg(msg):
    print ' [grabimgurl DMSG]',msg
