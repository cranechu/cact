from peewee import *
import datetime

material = SqliteDatabase("database/material.sqlite")

class MaterialModel(Model):
    class Meta:
        database = material

class Website(MaterialModel):
    url_base = CharField(primary_key=True)
    url_index = CharField(unique=True)
    nationality = CharField(null=True)
    notes = TextField(null=True)

class Article(MaterialModel):
    source = ForeignKeyField(Website, related_name='articles')
    title = CharField()
    url = CharField()
    date = DateTimeField(default=datetime.datetime.now())
    topic = CharField(null=True)
    author = CharField(null=True)

class Sentence(MaterialModel):
    article = ForeignKeyField(Article, related_name='sentences', null=True)
    content = CharField()
    order = IntegerField()

class Wordchar(MaterialModel):
    wordchar = CharField(primary_key=True, max_length=8)
    counter = IntegerField(default=1)
    length = IntegerField()
    tongyi = CharField(null=True)  #itmes concatenated
    fanyi = CharField(null=True)
    bianxi = CharField(null=True)
    english = CharField(null=True)
    url = CharField(null=True)
    writing = BlobField(null=True)

class Pronounce(MaterialModel):
    pinyin = CharField(primary_key=True, max_length=8)
    mp3 = BlobField()

class Explain(MaterialModel):
    wordchar = ForeignKeyField(Wordchar, related_name='explains')
    order = IntegerField()
    pinyin = CharField()
    explain = TextField()
    examples = CharField(null=True)
