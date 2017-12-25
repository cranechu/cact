import re
import sys
import bs4
import urllib
import requests
import pypinyin
from bs4 import BeautifulSoup
from material_model import Explain, Wordchar, material


def handle_jieshi(wc, jieshi):
    count = 0
    try:
        j = jieshi.replace('\xa0', '').replace('\n\n\n', '\n').replace('\n\n', '\n')
        l = re.split(',|\n', j)[1:-1]
        n = 6
        result = []
        for item in [l[i:i+n] for i in range(0, len(l), n)]:
            pinyin = item[0].strip()
            jieshi = item[2].strip()
            if pinyin=='':
                pinyin='/'.join([a[0] for a in pypinyin.pinyin(wc.wordchar)])
            zuci = item[5].strip()
            result.append((pinyin, jieshi, zuci))
        for i, r in enumerate(result):
            #print(r)
            count += 1
            Explain.create(wordchar=wc,
                           order=i,
                           pinyin=r[0],
                           explain=r[1],
                           examples=r[2])
    except Exception:
        pass

    return count

if __name__ == '__main__':
    total = 0

    for wc in list(Wordchar.select().order_by(Wordchar.counter.desc())):
        total += 1
        print(total, wc.wordchar, wc.counter)
        if len(wc.explains) != 0:
            print("done")
            continue

        try:
            c = urllib.request.urlopen(u"http://charena2015.appspot.com/edit?target="+urllib.parse.quote(wc.wordchar))
        except Exception as e:
            print(e)
            continue

        with material.transaction():
            soup = BeautifulSoup(c.read(), "html.parser")
            e = soup.text
            e = e.split(wc.wordchar, 1)[1].replace('～', wc.wordchar)
            jieshi, e = e.split(u'同义词：', 1)

            #fewly used, or no explanation found, to remove the word
            if wc.length>1 and wc.counter==1:
                wc.delete_instance()
                print("removed")
            elif 0 == handle_jieshi(wc, jieshi):
                wc.delete_instance()
                print("removed")
            else:
                #update the wordchar
                tongyi, e = e.split(u'反义词：', 1)
                fanyi, english = e.split(u'英文解释：', 1)
                tongyi = ';'.join(tongyi.strip().split(', '))
                if tongyi != '':
                    wc.tongyi = tongyi
                fanyi = ';'.join(fanyi.strip().split(', '))
                if fanyi != '':
                    wc.fanyi = fanyi
                english = ';'.join(english.strip().split(', '))
                if english != '':
                    wc.english = english
                wc.save()
                print(len(wc.explains))
