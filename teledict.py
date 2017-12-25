#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import sys
import time
import urllib
import asyncio
import telepot
import jieba.posseg
import jieba.analyse
from material_model import *
from pydub import AudioSegment as audio
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
from mutagen.oggvorbis import OggVorbis
#import image
#import images2gif

class MissWuBot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(MissWuBot, self).__init__(*args, **kwargs)

    def on_chat_message(self, msg):
        to = msg['from']['id']

        try:
            output = []
            wc = Wordchar.get(Wordchar.wordchar==msg['text'])
            explain = wc.explains[0]
            output.append("*%s*: %s, %s" % (msg['text'],
                                            explain.pinyin,
                                            explain.explain))
            if wc.english:
                output.append("English: %s" % wc.english.split(',')[0].strip())
            if wc.tongyi:
                output.append("同义词: %s" % wc.tongyi.split(',')[0].strip())
            if wc.fanyi:
                output.append("反义词: %s" % wc.fanyi.split(',')[0].strip())
            if wc.bianxi:
                output.append("辨析: %s" % wc.bianxi.split(',')[0].strip())
            if wc.url:
                output.append("Link: %s" % wc.url)
            c = '\n'.join(output)

            #send writing gif
            if wc.writing:
                self.sendDocument(to, ('a.gif', io.BytesIO(wc.writing)))

        except DoesNotExist:
            c = None

        markup2 = ForceReply()
        markup = ReplyKeyboardMarkup(keyboard=[
            ['上', '下', '左', '右'],
            ])

        #send basic information
        if c:

            #self.sendMessage(to, c, parse_mode='markdown',
            #                 disable_web_page_preview=True)
            pass

            #send full explaination
            # output = []
            # for e in wc.explains.order_by(Explain.order):
            #     output.append("%s, %s, %s" % (e.pinyin, e.explain, e.examples))
            # self.sendMessage(to, '\n'.join(output))

        #send voice
        wcl = []
        pl = []

        if not c:
            for w in jieba.posseg.cut(msg['text']):
                try:
                    wcl.append(Wordchar.get(Wordchar.wordchar==w.word))
                except DoesNotExist:
                    #collect one by one
                    self.sendMessage(to, 'Give me Chinese words you want to learn...')
                    return
                    #for c in w.word:
                    #    wcl.append(Wordchar.get(Wordchar.wordchar==c))
            pinyin = '/'.join([w.explains[0].pinyin for w in wcl])
        else:
            pinyin = explain.pinyin

        if c:
            py_str = c
        else:
            py_str = ' '.join(pinyin.split('/'))

        playtime = 0
        for pinyin in pinyin.split('/'):
            p = Pronounce.get(Pronounce.pinyin == pinyin)
            pl.append(p)
            f = OggVorbis(io.BytesIO(p.mp3))
            playtime += f.info.length
        py = b''.join([p.mp3 for p in pl])
        self.sendVoice(to, io.BytesIO(py), duration=playtime, caption=py_str)


TOKEN = "211740905:AAE86C6xBJ7rUHiUVscIrUUPaDUBmYyEkds"
bot = MissWuBot(TOKEN)
bot.message_loop()
print('Listening ...')
while True: time.sleep(10)
