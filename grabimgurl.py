import urlproxy as urlp
from bs4 import BeautifulSoup as bs

class GrabImgError(Exception):
    pass

class OpenUrlError(GrabImgError):
    def __init__(self, url, msg):
        self.url = url
        self.msg = msg

class TooDeepError(GrabImgError):
    def __init__(self, maxdeep):
        self.maxdeep = maxdeep

class ImgNotFoundError(GrabImgError):
    def __init__(self, url, msg):
        self.url = url
        self.msg = msg
        
def save_img_in_url(url, fn='tempimg', maxdepth=1, currentdepth=1 ):
    try:
        if currentdepth > maxdepth:
            raise TooDeepError( maxdepth )

        # get resource
        goturl = urlp.fetch_url(url)

        # check type and save
        if 'image' ==  goturl.info().getmaintype():
            with open(fn,'wb') as f:
                f.write(urlp.fetch_url(url).read())
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

    except:
        logfn = fn+'.saveerror'
        l = open(logfn,'w')
        l.write(url)
        l.close()
        raise GrabImgError

def dmsg(msg):
    print ' [grabimgurl]',msg
