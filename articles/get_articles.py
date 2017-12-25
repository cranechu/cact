import sys
import bs4
import requests
import newspaper

article_id = 0

def save_article(url, mag):
    try:
        global article_id
        a = newspaper.Article(url, language='zh')
        a.download()
        a.parse()
        if len(a.text)>100:
            article_id += 1
            print(article_id, a.title)
            with open("%s/%d.txt"%(mag, article_id), "w") as f:
                f.writelines(url+'\n')
                f.writelines(a.title+'\n')
                f.writelines(a.text+'\n')
    except Exception:
        pass

def get_articles_etwx():
    url_base = "http://www.ccppg.com.cn/baokan/etwx/"
    url_index = "http://www.ccppg.com.cn/baokan/etwx/"
    url_src_set = set([url_index,])
    url_dest_set = set()
    while url_src_set:
        url = url_src_set.pop()
        print(url, len(url_src_set), len(url_dest_set))
        res  = requests.get(url)
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        more_url = {a.attrs.get('href') for a in soup.select('a[href^=%s]'%url_base)}
        url_src_set |= more_url
        url_dest_set |= {url}
        url_src_set -= url_dest_set
        save_article(url, "etwx")

def get_articles_bowu():
    url_base = "http://www.dili360.com"
    url_index = "http://www.dili360.com/nh/index/index.htm"
    url_src_set = set([url_index,])
    url_dest_set = set()
    while url_src_set:
        url = url_src_set.pop()
        print(url, len(url_src_set), len(url_dest_set))
        res  = requests.get(url)
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        more_url = {url_base+a.attrs.get('href') for a in soup.select('a[href^=%s]'%'/nh')}
        url_src_set |= more_url
        url_dest_set |= {url}
        url_src_set -= url_dest_set
        save_article(url, "bowu")

def get_articles_zbjy():
    url_base = "http://www.zaobao.com"
    url_index = "http://www.zaobao.com/lifestyle/education"
    url_src_set = set([url_index,])
    url_dest_set = set()
    while url_src_set:
        url = url_src_set.pop()
        print(url, len(url_src_set), len(url_dest_set))
        res  = requests.get(url)
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        more_url = {url_base+a.attrs.get('href') for a in soup.select('a[href^=%s]'%'/lifestyle/education')}
        url_src_set |= more_url
        url_dest_set |= {url}
        url_src_set -= url_dest_set
        save_article(url, "zbjy")

if __name__=='__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('which magazine?\n')
    else:
        if sys.argv[1] == 'bowu':
            get_articles_bowu()
        elif sys.argv[1] == 'etwx':
            get_articles_etwx()
        elif sys.argv[1] == 'zbjy':
            get_articles_zbjy()
