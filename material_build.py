import os
import re
import jieba.posseg
import jieba.analyse
import peewee
from material_model import *
from bs4 import BeautifulSoup

#build material database
# - scan directories
# - scan files
# - break into sentences
# - break into words
# - collect information for words


def handle_wordchar(wordchar):
    wc, created = Wordchar.get_or_create(wordchar=wordchar, length=len(wordchar))
    if not created:
        wc.counter += 1
        wc.save()

def handle_sentence(article, order, sentence):
    if len(sentence) > 3:
        #print("%d: %s"%(order, sentence))
        Sentence.create(article=article,
                        content=sentence,
                        order=order)
        for w in jieba.posseg.cut(sentence):
            if len(w.word) <= 7:
                if w.flag != 'x' and w.flag != 'eng':
                    handle_wordchar(w.word)
            if len(w.word) > 1:
                for c in w.word:
                    handle_wordchar(c)
file_count = 0
def handle_file(website, filename):
    global article
    global file_count
    #1st pass: get article informations
    with open(filename) as f:
        url = f.readline()
        title = f.readline()
        print(file_count, title)
        file_count += 1
        tags = jieba.analyse.extract_tags(f.read(), 5)
        topic = ','.join(tags)
        article = Article.create(source=website,
                                 title=title,
                                 url=url,
                                 topic=topic)

    #2nd pass: get sentences
    order = 0
    with open(filename) as f:
        f.readline()
        f.readline()
        for line in f.readlines():
            soup = BeautifulSoup(line, "html.parser")
            l = re.split('(。|！|？)', soup.text)
            for i in range(0, len(l)-1, 2):
                handle_sentence(article, order, l[i] + l[i+1])
                order += 1


if __name__=='__main__':
    material.connect()
    material.create_tables([Website, Article, Sentence,
                            Pronounce, Explain, Wordchar], True)

    root_dir = "articles"
    dir_list = [d for d in os.listdir(root_dir) if \
                not os.path.isfile(os.path.join(root_dir, d))]
    for sub_dir in dir_list:
        website = Website.create(url_base=sub_dir, url_index=sub_dir)
        sub_dir = root_dir + '/' + sub_dir
        files = [f for f in os.listdir(sub_dir) if \
                 os.path.isfile(os.path.join(sub_dir, f))]
        for file in files:
            filename = sub_dir + '/' + file
            with material.transaction():
                handle_file(website, filename)
