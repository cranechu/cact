import os
import re
from pydub import AudioSegment as au
from material_model import material, Pronounce

yuanyin = {
    'a' : ['ā', 'á', 'ǎ', 'à'],
    'o' : ['ō', 'ó', 'ǒ', 'ò'],
    'e' : ['ē', 'é', 'ě', 'è'],
    'i' : ['ī', 'í', 'ǐ', 'ì'],
    'u' : ['ū', 'ú', 'ǔ', 'ù'],
    'ü' : ['ǖ', 'ǘ', 'ǚ', 'ǜ']
}

def pinyin2to1(s):
    vowel = '[aoeiuü]'
    vowel2 = 'iuü'
    p1 = None
    try:
        p1 = re.search(vowel, s).start()
        p2 = re.search(vowel, s[p1+1:]).start() + p1+1
    except:
        p2 = None

    if p1==None: return s

    p = p1
    if p2 and (s[p1] in vowel2):
        p = p2

    if s[-1].isdecimal():
        tone = int(s[-1])
        assert(tone<=4)
        l = list(s)
        l[p] = yuanyin[s[p]][tone-1]
        s = ''.join(l[:-1])
    return s

def add_pinyin_from_file():
    count = 0
    for dir in ['full', 'yinjie', 'shengmu', 'yunmu']:
        for f in os.listdir('pinyin'+'/'+dir):
            if 'mp3' in f: continue
            filename = 'pinyin'+'/'+dir+'/'+ f
            #song = au.from_mp3(filename)
            #filename = filename.replace('mp3', 'ogg')
            #song.export(filename, 'ogg')
            count += 1
            pinyin = open(filename, 'rb').read()
            f = pinyin2to1(f.replace('.ogg', '').replace('v', 'ü'))
            assert(len(f)<8)
            print(count, filename, f)
            p, created = Pronounce.create_or_get(pinyin=f, mp3=pinyin)
            if not created:
                print("ignore dup", f)

def add_light_pinyin():
    vowel = 'aoeiuü'
    light_list = [yuanyin[p][0] for p in vowel]
    print(light_list)
    for py in list(Pronounce.select()):
        for p in vowel:
            if yuanyin[p][0] in py.pinyin:
                py1 = py.pinyin
                py0 = py.pinyin.replace(yuanyin[p][0], p)
                print(py1, py0)
                p, created = Pronounce.create_or_get(pinyin=py0, mp3=py.mp3)
                if not created:
                    print("existed already")

if __name__ == '__main__':
    add_light_pinyin()
