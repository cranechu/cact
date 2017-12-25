import io
import re
import bs4
import sys
import imghdr
import requests
import pypinyin
import wikipedia
from material_model import *
from hanziconv import HanziConv

def update_from_wiki(wc):
    try:
        p = wikipedia.page(wc)
    except wikipedia.DisambiguationError:
        return [], ''

    l = []
    url = ''
    if HanziConv.same(p.title, wc):
        s = wikipedia.summary(wc, sentences=2)
        s = HanziConv.toSimplified(s)
        py ='/'.join([a[0] for a in pypinyin.pinyin(wc)])
        l.append((py, s))
        url = p.url
    return l, url

def update_from_zdic(wc):
    r = requests.post('http://www.zdic.net/sousuo/',
                      data = {'lb_a':'hp',
                              'lb_b':'mh',
                              'lb_c':'mh',
                              'tp'  :'tp1',
                              'q'   :wc})
    s = bs4.BeautifulSoup(r.content.decode('utf-8', 'ignore'),
                          "html.parser")
    explains = s.find_all('p', class_=re.compile('zdct'))
    pinyin = None
    l=[]
    url=r.url

    for tag in explains:
        line = str(tag)
        if 'strong' in line:
            pinyin = None
        elif 'dicpy' in line and 'spz' in line:
            pinyin = str(tag.span).split('>')[1].split('<')[0].strip()
        elif ('汉' in line or '漢' in line) and \
             ('典' in line or '典' in line):
            break
        elif pinyin:
            soup = bs4.BeautifulSoup(line, "html.parser")
            jieshi = soup.text.strip().replace('～', wc)
            if '.' in jieshi:
                jieshi = jieshi.split('.', 1)[1]
            else:
                jieshi = jieshi[1:]
            jieshi = jieshi.strip()
            l.append((pinyin, jieshi))

    return l, url

def get_writing_gif(url):
    '''http://www.zdic.net/z/20/js/7A7A.htm =>
       http://pic.zdic.net/kai/jt_bh/gif/20/7A7A.gif'''
    l = url.split('/')
    k = l[4]
    c = l[-1].split('.')[0]

    url = 'http://pic.zdic.net/kai/jt_bh/gif/%s/%s.gif'%(k,c)
    #print(url)
    r = requests.get(url)
    if r.ok:
        return r.content
    else:
        return None

def update_wordchar_explain(wc):
    print("updating: ", wc)
    r = []
    url = ''
    if len(wc) == 1:
        r, url = update_from_zdic(wc)
        get_writing_gif(url)
    else:
        r, url = update_from_wiki(wc)

    print(url)
    for i in r:
        print(i)

#wiki explain is too hard to follow for Chiense learner, not use
def update_word_wiki(counter, wc):
    if wc.length > 1 and wc.url == None:
        r, url = update_from_wiki(wc.wordchar)
        if r != []:
            explain = wc.explains[0]
            explain.pinyin = r[0][0]
            explain.explain = r[0][1]
            explain.save()
            wc.url = url
            wc.save()
            print(counter, explain.pinyin, explain.explain)

gif_count = 0


def update_pic(wc):
    global gif_count
    if wc.picture: return
    s = requests.get("https://www.google.com.sg/search?safe=active&tbm=isch&q=%s&ei=9WSTV73fDJeSvQTsv7gw&emsg=NCSR&noj=1#imgrc=m--PHI_LJBy-JM%%3A"%(wc.wordchar+' file:*'))
    b = bs4.BeautifulSoup(s.text, 'html.parser')
    link = b.select('a[href^=/url]')[0].img.get('src')
    print(link)
    pic = requests.get(link).text
    pic_content = bytearray(pic[:50], 'utf-8')
    print(pic_content)
    print(imghdr.what('', pic_content))
    gif_count += 1
    filename = 'picture/%d'%gif_count
    with open(filename, 'wb') as f:
        f.write(pic)
    new_filename = filename+'.'+imghdr.what(filename)
    os.rename(filename, new_filename)
    wc.picture = new_filename
    print(wc.wordchar, new_filename)
    #wc.save()

def main():
    counter = 0
    wikipedia.set_lang('zh')
    for wc in list(Wordchar.select().order_by(Wordchar.counter.desc())):
        counter += 1
        print(counter, wc.wordchar)
        with material.transaction():
            update_pic(wc)

if __name__ == '__main__':
    main()
