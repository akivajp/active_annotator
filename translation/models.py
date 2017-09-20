# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# system
from datetime import datetime
import os
#from os.path import dirname

# python-magic (file type checking)
import magic

# django
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

MAX_TEXT_LENGTH = 4096
MAX_NAME_LENGTH = 256
MAX_CODE_LENGTH = 10

DIGEST_SIZE = 256

#STATIC_DIR = os.path.join(BASE_DIR, 'static')

APP_DIR      = os.path.dirname(os.path.abspath(__file__))
SELECTOR_DIR = os.path.join(APP_DIR, 'phrase_selectors')
#PROJECT_DIR = settings.BASE_DIR
#STATIC_DIR  = os.path.join(PROJECT_DIR, 'static')
#UPLOAD_DIR  = os.path.join(STATIC_DIR, 'uploaded')
#PREPROC_DIR = os.path.join(STATIC_DIR, 'preproc')

### sub functions

SELECT_METHODS = os.listdir(SELECTOR_DIR)
#def get_select_methods():
#    methods_dir = os.path.join(APP_DIR, 'phrase_selectors')
#    methods = os.listdir(methods_dir)
#    return zip(methods, methods)

def include_any(string, keywords):
    return any([string.find(key) >= 0 for key in keywords])

### choices

LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('ja', 'Japanese'),
    ('zh', 'Chinese'),
]

### models

def save_to(instance, filename):
    #date = datetime.now().strftime("%Y/%m/%d")
    return os.path.join(instance.base, filename)

class File(models.Model):
    #info = models.FileField(upload_to='uploaded/%Y/%m/%d')
    info = models.FileField(upload_to = save_to)
    upload_date = models.DateTimeField(default = datetime.now)
    #category = models.CharField(max_length=MAX_NAME_LENGTH)
    base = models.CharField(max_length=MAX_NAME_LENGTH)

    def __unicode__(self):
        if self.info:
            return self.info.name
        else:
            return "[N/A]"

class Project(models.Model):
    #SELECT_METHODS = get_select_methods()
    SELECT_METHODS = zip(SELECT_METHODS, SELECT_METHODS)
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    #lang_src = models.CharField(max_length=MAX_CODE_LENGTH, choices=LANGUAGE_CHOICES, default='en')
    lang_src = models.CharField(max_length=MAX_CODE_LENGTH, choices=LANGUAGE_CHOICES, verbose_name='Source Language')
    #lang_trg = models.CharField(max_length=MAX_CODE_LENGTH, choices=LANGUAGE_CHOICES, default='ja')
    lang_trg = models.CharField(max_length=MAX_CODE_LENGTH, choices=LANGUAGE_CHOICES, verbose_name='Target Language')
    select_method = models.CharField(max_length=MAX_NAME_LENGTH, choices=SELECT_METHODS)
    #corpora = models.ManyToManyField(Corpus)
    #base_corpora = models.ManyToManyField(Corpus)
    active = models.BooleanField(default = False)
    #preprocessed = models.BooleanField(default = False)
    max_sentence_length = models.IntegerField(default = 60)
    open_date = models.DateTimeField(default = datetime.now)
    update_date = models.DateTimeField(default = datetime.now)
    multiplicity = models.IntegerField(default = 1)

    def __unicode__(self):
        return self.name

    def get_phrases(self):
        phrases_file = self.get_phrases_file()
        if phrases_file:
            phrases_file.info.open()
            for line in phrases_file.info:
                fields = line.strip().split(u'\t')
                if len(fields) > 0:
                    str_phrase = fields[0]
                phrase = self.phrase_set.filter(text = str_phrase).first()
                if not phrase:
                    phrase = Phrase(project = self, text = str_phrase)
                    phrase.num_tokens = len(str_phrase.split(' '))
                    if len(fields) > 1:
                        phrase.context = fields[1]
                    else:
                        phrase.context = str_phrase
                    if len(fields) > 2:
                        phrase.frequency = int(fields[2])
                    else:
                        phrase.frequency = 1
                yield phrase

    def get_digest_phrases(self):
        phrases_file = self.get_phrases_file()
        if phrases_file:
            phrases_file.info.open()
        #self.file.info.open()
        #digest = self.file.info.read(DIGEST_SIZE)
        #digest = digest.replace('\n', '<br />\n')
        #if self.file.info.read(1):
        #    digest += '...'
        #return digest

    def get_phrases_file(self):
        proc_phrases = self.process_set.filter(role = 'phrases.src').first()
        if proc_phrases and proc_phrases.done:
            return proc_phrases.target
        else:
            return None

    def get_phrases_path(self):
        proc_phrases = self.process_set.filter(role = 'phrases.src').first()
        if proc_phrases and proc_phrases.done:
            return proc_phrases.target.info.path
        else:
            return ""

    def get_selector_path(self):
        if self.select_method:
            return os.path.join(SELECTOR_DIR, self.select_method)
        else:
            return ""

    def get_valid_translations(self):
        return self.translation_set.exclude(trg='')

    def is_ready(self):
        if self.active and self.get_phrases_path():
            return True
        else:
            return False

#class Project(models.Model):
#    LANGUAGE_CHOICES = (
#        ('en', 'English'),
#        ('ja', 'Japanese'),
#        ('zh', 'Chinese'),
#    )
#    name = models.CharField(max_length=MAX_LENGTH)
#    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
#    active   = models.BooleanField(default=False)
#    open_date = models.DateTimeField(default = datetime.now)
#    multiplicity = models.IntegerField(default = 1)
#
#    def __unicode__(self):
#        return self.name
#
#    def get_caption_set(self):
#        return Caption.objects.filter(image__project=self)
#
#    def get_max_captions(self):
#        return self.image_set.count() *self.multiplicity
#
#    def get_progress(self):
#        progress = 0
#        if self.image_set.count() > 0:
#            num_captions = self.get_caption_set().count()
#            progress = round(100.0 * num_captions / self.get_max_captions(), 2)
#        return progress
#
#    def get_confirm_progress(self):
#        progress = 0
#        if self.image_set.count() > 0:
#            num_confirmed = self.get_caption_set().filter(confirmed=True).count()
#            progress = round(100.0 * num_confirmed / self.get_caption_set().count(), 2)
#        return progress

class Corpus(models.Model):
    project = models.ForeignKey(Project)
    file = models.ForeignKey(File)
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    #path = models.CharField(max_length=MAX_TEXT_LENGTH)
    lang = models.CharField(max_length=MAX_CODE_LENGTH, choices=LANGUAGE_CHOICES)
    covered = models.BooleanField(default=False)
    upload_date = models.DateTimeField(default = datetime.now)

    class Meta:
        verbose_name_plural = 'corpora'

    def get_fullpath(self):
        return os.path.join(self.file.info.path)

    def get_digest(self):
        self.file.info.open()
        digest = self.file.info.read(DIGEST_SIZE)
        digest = digest.replace('\n', '<br />\n')
        if self.file.info.read(1):
            digest += '...'
        return digest

class Process(models.Model):
    project = models.ForeignKey(Project)
    role    = models.CharField(max_length=MAX_NAME_LENGTH)
    command = models.CharField(max_length=MAX_TEXT_LENGTH)
    target  = models.ForeignKey(File)
    issue_date = models.DateTimeField(default = datetime.now)
    done    = models.BooleanField(default = False)

    class Meta:
        verbose_name_plural = 'processes'

    def __unicode__(self):
        return "%s > %s" % (self.command, self.target.info.path)

class Phrase(models.Model):
    project    = models.ForeignKey(Project)
    text       = models.CharField(max_length=MAX_TEXT_LENGTH)
    num_tokens = models.IntegerField()
    context    = models.CharField(max_length=MAX_TEXT_LENGTH)
    frequency  = models.IntegerField()

    def __unicode__(self):
        return self.text

    def get_highlighted(self):
        html = self.context
        html = html.replace(self.text, '<span class="highlight">%s</span>' % self.text)
        return html

CONFIDENCE_CHOICES = [
        [3, '3: sure about the translation'],
        [2, '2: not so sure about the translation'],
        [1, '1: not sure at all'],
]
class Translation(models.Model):
    project = models.ForeignKey(Project)
    editor  = models.ForeignKey(User)
    src_phrase  = models.ForeignKey(Phrase)
    src = models.CharField(max_length=MAX_TEXT_LENGTH)
    trg = models.CharField(max_length=MAX_TEXT_LENGTH, default='')
    confidence = models.IntegerField(default = -1, choices = CONFIDENCE_CHOICES, verbose_name='Confidence Level')
    confirmed  = models.BooleanField(default = False)
    #duration = models.FloatField(default = -1)
    assign_date = models.DateTimeField(default = datetime.now)
    edit_date = models.DateTimeField(default = datetime.now)
    confirm_date = models.DateTimeField(default = datetime.now)

    def __unicode__(self):
        return "(src=%s, trg=%s, editor=%s)" % (self.src, self.trg, self.editor.username)

#class File(models.Model):
#    path = models.CharField(max_length=MAX_LENGTH)
#    orig_path = models.CharField(max_length=MAX_LENGTH)
#    upload_date = models.DateTimeField(default = datetime.now)
#
#    def __unicode__(self):
#        return self.path
#
#class Image(models.Model):
#    project  = models.ForeignKey(Project)
#    file     = models.ForeignKey(File)
#    registered_date = models.DateTimeField(default = datetime.now)
#    valid    = models.BooleanField(default=True)
#
#    def __unicode__(self):
#        return "project:%s file:%s" % (self.project.name, self.file.path)
#
#    def is_video(self):
#        fullpath = os.path.join(STATIC_DIR, self.file.path)
#        return include_any(magic.from_file(fullpath), ['MP4', 'WebM'])
#
#    def get_caption_text(self):
#        caption = self.caption_set.first()
#        if caption:
#            return caption.text
#        return ""
#
#    def get_editor_name(self):
#        caption = self.caption_set.first()
#        if caption:
#            return caption.editor.username
#        return ""
#
#class Caption(models.Model):
#    image         = models.ForeignKey(Image)
#    editor        = models.ForeignKey(User)
#    text          = models.CharField('Caption Text', max_length=MAX_LENGTH)
#    edit_date     = models.DateTimeField(default = datetime.now)
#    #staff_checked = models.BooleanField(default=False)
#    confirmed     = models.BooleanField(default=False)
#    check_date    = models.DateTimeField(default = datetime.now)
#
#    def __unicode__(self):
#        return '(project="%s", file="%s", caption_id="%s")' % (self.image.project.name, self.image.file.path, self.id)

class Report(models.Model):
    phrase      = models.ForeignKey(Phrase)
    editor      = models.ForeignKey(User)
    comment     = models.CharField(max_length=MAX_TEXT_LENGTH)
    report_date = models.DateTimeField(default = datetime.now)

    def __unicode__(self):
        return '(project="%s", phrase="%s", editor="%s")' % (self.phrase.project.name, self.phrase.text, self.editor.username)

