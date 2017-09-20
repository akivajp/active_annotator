# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Corpus
from .models import File
from .models import Phrase
from .models import Project
from .models import Process
from .models import Report
from .models import Translation

##admin.site.register(Project, ProjectAdmin)
admin.site.register(Corpus)
admin.site.register(File)
admin.site.register(Phrase)
admin.site.register(Process)
admin.site.register(Project)
admin.site.register(Report)
admin.site.register(Translation)
#admin.site.register(Report)

