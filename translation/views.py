# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# system
from datetime import datetime
import json
import os
import subprocess

# django
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models import Sum
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse

# app
#from annotate.models import Project, File, Image, Caption, Report
from .models import Project, Corpus, File, Phrase, Process, Translation, Report

#APP_DIR     = os.path.dirname(os.path.abspath(__file__))
#PROJECT_DIR = os.path.dirname(APP_DIR)
#STATIC_DIR  = os.path.join(PROJECT_DIR, 'static')
#UPLOAD_DIR  = os.path.join(STATIC_DIR, 'uploaded')
#PREPROC_DIR = os.path.join(STATIC_DIR, 'preproc')

#logger = logging.getLogger('django')

### form classes

class NewProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'lang_src', 'lang_trg', 'multiplicity']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        #fields = ['name', 'lang_src', 'lang_trg', 'active', 'multiplicity', 'open_date', 'update_date']
        fields = ['name', 'lang_src', 'lang_trg', 'max_sentence_length', 'select_method', 'active', 'multiplicity']
        #fields = ['name', 'lang_src', 'lang_trg']

    def protect(self):
        #self.fields['open_date'].disabled = True
        #self.fields['open_date'].required = False
        #self.fields['update_date'].disabled = True
        #self.fields['update_date'].required = False
        return self

class CorpusForm(forms.ModelForm):
    class Meta:
        model = Corpus
        fields = ['project', 'lang', 'name', 'covered']
        widgets = {
            'project': forms.HiddenInput(),
            'lang': forms.HiddenInput(),
        }
        labels = {
            'name': 'Corpus Name',
            'covered': 'Set as a base corpus (Check if this corpus is covered in the availale parallel data and you want to use it as a base corpus',
        }
    def protect(self, project=None):
        if project:
            self.fields['project'].initial = project
            self.fields['lang'].initial = project.lang_src
        return self

class UploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['info']
        labels = {
            'info': 'File',
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['phrase', 'editor', 'comment']
        widgets = {
            'phrase': forms.HiddenInput(),
            'editor': forms.HiddenInput(),
        }
        labels = {
            'comment': 'Input here the reason why you skip (for example: "It is difficult for me because this phrase is fragmented")',
        }

class TranslationForm(forms.ModelForm):
    class Meta:
        model = Translation
        #fields = ['src', 'trg', 'editor']
        fields = ['trg', 'editor', 'confidence', 'src_phrase']
        widgets = {
            'src_phrase': forms.HiddenInput(),
            'editor': forms.HiddenInput(),
            'confidence': forms.RadioSelect(),
        }
        labels = {
            'trg': 'Translation',
        }

#### sub functions
#
#def py2_to_str(s):
#    if isinstance(s, (bytes, str)):
#        return bytes
#    elif isinstance(s, unicode):
#        return s.encode('utf-8')
#    else:
#        return str(s)

def get_page(request, objects, per_page=100, span=3):
    paginator = Paginator(objects, per_page)
    page_num = request.GET.get("page")
    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    page.previous_pages = range(max(1,page.number-span), page.number)
    page.following_pages = range(page.number+1,min(page.paginator.num_pages,page.number+span)+1)
    return page

#if sys.version_info.major >= 3:
#    pass
#else:
#    to_str = py2_to_str

def safe_makedirs(path):
    try:
        os.makedirs(path)
    except:
        pass

#def save_corpus(request):
#    # deciding save path
#    fileinfo = request.FILES['file']
#    base = os.path.basename(fileinfo.name)
#    last_corpus = Corpus.objects.order_by('id').last()
#    if last_corpus:
#        new_id = last_corpus.id + 1
#    else:
#        new_id = 1
#    fullpath = os.path.join(UPLOAD_DIR, 'corpora', "%04d" % new_id, base)
#    relative = fullpath[len(STATIC_DIR):].lstrip("/")
#    # storing the uploaded file
#    safe_makedirs( os.path.dirname(fullpath) )
#    with open(fullpath, 'wb') as fobj:
#        for chunk in fileinfo.chunks():
#            fobj.write(chunk)
#    # registering corpus entry
#    corpus_form = CorpusForm(request.POST, request.FILES)
#    new_corpus = corpus_form.save(commit=False)
#    new_corpus.path = relative
#    new_corpus.save()
#    messages.success(request, 'Successfully uploaded: "%s"' % relative)
#    return True

### help functions

#def get_page(request, objects, per_page=100, span=3):
#    paginator = Paginator(objects, per_page)
#    page_num = request.GET.get("page")
#    try:
#        page = paginator.page(page_num)
#    except PageNotAnInteger:
#        page = paginator.page(1)
#    except EmptyPage:
#        page = paginator.page(paginator.num_pages)
#    page.previous_pages = range(max(1,page.number-span), page.number)
#    page.following_pages = range(page.number+1,min(page.paginator.num_pages,page.number+span)+1)
#    return page
#

### views

@staff_member_required
def ajax_delete(request, target, id):
    response = {}
    if target == 'file':
        file = get_object_or_404(File, pk=id)
        fullpath = os.path.join(STATIC_DIR, file.path)
        os.remove(fullpath)
        file.delete()
        #messages.success(request, 'Successfully deleted file: %s' % file.path)
        response["message"] = 'Successfully deleted file: %s' % file.path
    elif target == 'project':
        project = get_object_or_404(Project, pk=id)
        name = project.name
        project.delete()
        #messages.success(request, 'Successfully deleted project: %s' % name)
        response["message"] = 'Successfully deleted project: %s' % name
    elif target == 'corpus':
        corpus = get_object_or_404(Corpus, pk=id)
        name = corpus.name
        path = corpus.file.info.name
        corpus.delete()
        response["message"] = 'Successfully deleted corpus: "%s" (%s)' % (name, path)
    else:
        raise Http404
    #if position:
    #    return HttpResponseRedirect(request.META.get("HTTP_REFERER")+"#"+position)
    #else:
    #    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    #return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return HttpResponse(json.dumps(response), content_type='text/javascript')

@staff_member_required
def ajax_toggle(request, target, id):
    response = {}
    if target == 'active':
        project = get_object_or_404(Project, pk=id)
        project.active = not project.active
        project.save()
        response["message"] = 'Successfully toggled activity of project: %s' % project.name
    elif target == 'confirmed':
        translation = get_object_or_404(Translation, pk=id)
        translation.confirmed = not translation.confirmed
        translation.confirm_date = datetime.now()
        translation.save()
        response["message"] = 'Successfully toggled confirmation of translation No.%s.' % translation.id
        response["confirmed"] = translation.confirmed
    else:
        raise Http404
    return HttpResponse(json.dumps(response), content_type='text/javascript')

@staff_member_required
def create(request, model):
    if request.method == 'POST':
        if model == 'project':
            form = NewProjectForm(request.POST)
            project = form.save(commit=False)
            if project.multiplicity < 1:
                messages.error(request, "Project multiplicity shoulde be positive")
            else:
                project.save()
                messages.success(request, "Successfully created project: %s" % project.name)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

@login_required
def index(request, sort_key="", reverse="0"):
    projects = Project.objects.all()
    #projects = Project.objects.filter(active=True).annotate(Count('image'), Count('image__caption'))
    if sort_key:
        try:
            projects = projects.order_by(sort_key)
        except Exception as e:
            raise Http404
    if reverse == '1':
        projects = projects.reverse()
    #captions = Caption.objects.filter(editor_id=request.user.id)
    #confirmed = Caption.objects.filter(editor_id=request.user.id, confirmed=True)
    breadcrumbs = []
    breadcrumbs.append(dict(name='Home'))
    table_columns = []
    if request.user.is_staff:
        table_columns.append(dict(align="center", type="toggle",  key="active", name="Activity"))
        table_columns.append(dict(align="center", type="project", key="name", name="Project Name"))
        table_columns.append(dict(align="center", type="text", key="lang_src", name="Source"))
        table_columns.append(dict(align="center", type="text", key="lang_trg", name="Target"))
        #table_columns.append(dict(align="center", type="progress", name="Status"))
        #table_columns.append(dict(align="center", type="download", name="Download Captions (CSV)"))
        #table_columns.append(dict(align="center", type="text",   key="language", name="Language"))
        #table_columns.append(dict(align="center", type="images", key="image__count", name="Videos / Images"))
        #table_columns.append(dict(align="center", type="text",   key="multiplicity", name="Multiplicity"))
        #table_columns.append(dict(align="center", type="captions", key="image__caption__count", name="Captions"))
        table_columns.append(dict(align="center", type="text",   key="select_method", name="Phrase Selection Method"))
        table_columns.append(dict(align="center", type="delete",   name="Delete"))
    else:
        projects = projects.filter(active = True, process__role='phrases.src')
        table_columns.append(dict(align="center", type="annotate", key="name", name="Project Name"))
        table_columns.append(dict(align="center", type="text", key="lang_src", name="Source"))
        table_columns.append(dict(align="center", type="text", key="lang_trg", name="Target"))
        #table_columns.append(dict(align="center", type="progress", name="Status"))
        #table_columns.append(dict(align="center", type="text",   key="language", name="Language"))
        #table_columns.append(dict(align="center", type="images", key="image__count", name="Videos / Images"))
        #table_columns.append(dict(align="center", type="text",   key="multiplicity", name="Multiplicity"))
        ##table_columns.append(dict(align="center", type="captions", key="image__caption__count", name="Captions"))
    translations = request.user.translation_set.exclude(trg = '')
    confirmed = translations.filter(confirmed = True)
    context = {
    #    #'project_list': project_list,
        'projects': projects,
        'breadcrumbs': breadcrumbs,
        'translations': translations,
        'confirmed': confirmed,
        'table_columns': table_columns,
        'sort_key': sort_key,
        'reverse': reverse,
    }
    #return render(request, 'annotate/index.html', context)
    if request.user.is_staff:
        context['project_form'] = NewProjectForm()
        return render(request, 'translation/staff/index.html', context)
    else:
        return render(request, 'translation/annotator/index.html', context)

@login_required
def edit(request, project_id, edit_id=""):
    if request.method == 'POST' and edit_id:
        translation = get_object_or_404(Translation, pk=edit_id)
        translation.edit_date = datetime.now()
        if not request.user.is_staff and translation.editor != request.user:
            messages.error(request, 'Sorry, you are not assigned for this translation.')
            return render(request, 'translation/annotator/edit.html', context)
        new_edit = True
        if len(translation.trg) > 0:
            new_edit = False
        form = TranslationForm(request.POST, instance=translation)
        form.save()
        if request.user.is_staff:
            messages.success(request, 'Successfully edit translation No.%s, thank you!' % edit_id)
            return HttpResponseRedirect(reverse('translation:translations', args=(project_id,))+'#edit'+edit_id)
        if new_edit:
            messages.success(request, 'Successfully submit your translation, thank you!')
            return HttpResponseRedirect(reverse('translation:edit', args=(project_id,)))
        else:
            messages.success(request, 'Successfully edit your translation, thank you!')
            return HttpResponseRedirect(reverse('translation:translations', args=(request.user.id,))+'#edit'+edit_id)
    project = get_object_or_404(Project, pk=project_id)
    breadcrumbs = []
    breadcrumbs.append(dict(name='Home', url='translation:index'))
    breadcrumbs.append(dict(name='Project: %s' % project.name))

    if edit_id:
        translation = get_object_or_404(Translation, pk=edit_id)
        if not request.user.is_staff and translation.editor != request.user:
            messages.error(request, 'Sorry, you are not assigned for this translation.')
            return HttpResponseRedirect(reverse('translation:index'))
        phrase = translation.src_phrase
        breadcrumbs.append(dict(name='Editting Caption: %s' % edit_id))
    else:
        # check if any image assign and not yet annotated (caption with no text)
        query = {}
        query['project_id'] = project_id
        #query['translation__project_id'] = project_id
        query['editor'] = request.user
        query['trg'] = ''
        translation = Translation.objects.filter(**query).first()
        phrase = None
        if translation:
            phrase = translation.src_phrase
        else:
            # assign new (unassigned yet) image
            phrases = project.phrase_set.annotate(Count('translation__editor'))
            phrases = phrases.filter(translation__editor__count__lt = project.multiplicity)
            phrases = phrases.exclude(report__editor = request.user)
            phrases = phrases.exclude(translation__editor = request.user)
            if phrases.count() > 0:
                phrase = phrases.first()
            else:
                # find new phrase
                for phrase in project.get_phrases():
                    if phrase.id:
                        continue
                    else:
                        phrase.save()
                        break
                if phrase and not phrase.id:
                    phrase = None
            if phrase:
                # create assignment (saving empty translation)
                translation = Translation()
                translation.project = project
                translation.src_phrase = phrase
                translation.editor = request.user
                translation.src = phrase.text
                translation.trg = ""
                translation.save()
            else:
                phrase = None
                translation = None
    user_translations = request.user.translation_set.filter(project=project).exclude(trg='')
    user_num_words = user_translations.aggregate(Sum('src_phrase__num_tokens'))['src_phrase__num_tokens__sum']
    project_translations = project.translation_set.exclude(trg='')
    project_num_words = project_translations.aggregate(Sum('src_phrase__num_tokens'))['src_phrase__num_tokens__sum']
    user_progress = 0
    project_progress = 0
#    if project.translation_set.count() > 0:
#        num_translations = project.get_translation_set().count()
#        num_phrases = project.image_set.count()
#        multiplicity = project.multiplicity
#        project_total = num_images * multiplicity
#        user_progress = round(100*user_captions.count()/num_images, 2)
#        project_progress = round(100*num_captions/project_total, 2)
    report = Report()
    report.phrase = phrase
    report.editor = request.user
    context = {
        'project': project,
        'breadcrumbs': breadcrumbs,
        'phrase': phrase,
        'translation': translation,
        'form': TranslationForm(instance=translation),
        'report_form': ReportForm(instance=report),
        'user_translations': user_translations,
        'user_num_words': user_num_words,
        'project_translations': project_translations,
        'project_num_words': project_num_words,
#        'user_progress': user_progress,
#        'project_progress': project_progress,
#        'project_total': project_total,
    }
    return render(request, 'translation/annotator/edit.html', context)

@staff_member_required
def preprocess(request, project_id):
    messages.warning(request, "implementing preprocessing")
    TRAVATAR_PATH = settings.TRAVATAR_PATH
    CKYLARK_PATH = settings.CKYLARK_PATH
    project = get_object_or_404(Project, pk=project_id)
    base = "project_%s/preproc" % project_id
    def exec_safe(base_command, base_target):
        process = Process.objects.filter(command=base_command).first()
        if not process:
            target = File(base = base)
            target.info.save(base_target, ContentFile(""))
            target.info.close()
            target.save()
            process = Process()
            process.project_id = project_id
            process.command = base_command
            process.target  = target
            process.role    = base_target
            process.save()
        if not process.done:
            command = "%s > %s" % (process.command, process.target.info.path)
            if subprocess.call(command, shell=True) == 0:
                messages.success(request, "done command: '%s'" % command)
                process.done = True
                process.save()
            else:
                messages.error(request, "error on command: '%s'" % command)
                return None
        return process.target.info.path
    if not project.select_method:
        messages.error(request, 'please choose "Select method" for this project')
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    # tokenize files
    tokenizer = TRAVATAR_PATH + '/src/bin/tokenizer'
    corpora = project.corpus_set.filter(covered = True)
    paths = [corpus.file.info.path for corpus in corpora]
    str_paths = unicode.join(u' ', paths) or '/dev/null'
    command = 'cat %s | %s' % (str_paths, tokenizer)
    path_base_cat = exec_safe(command, 'base.cat.src')
    if not path_base_cat:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    corpora = project.corpus_set.filter(covered = False)
    paths = [corpus.file.info.path for corpus in corpora]
    str_paths = unicode.join(u' ', paths) or '/dev/null'
    command = 'cat %s | %s' % (str_paths, tokenizer)
    path_add_cat = exec_safe(command, 'add.cat.src')
    if not path_add_cat:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    # cleaning
    temp_command = "cat %s | awk '0 < NF && NF <= %s && !a[$0]++'"
    command = temp_command % (path_base_cat, project.max_sentence_length)
    path_base_clean = exec_safe(command, 'base.clean.src')
    if not path_base_clean:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    command = temp_command % (path_add_cat, project.max_sentence_length)
    path_add_clean = exec_safe(command, 'add.clean.src')
    if not path_add_clean:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    # parsing (if need)
    if project.select_method.find('struct') >= 0:
        ckylark = os.path.join(CKYLARK_PATH, 'src/bin/ckylark')
        command = "cat %s | %s --model wsj" % (path_add_clean, ckylark)
        path_add_parse = exec_safe(command, 'add.parse.src')
        if not path_add_parse:
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        path_add_clean = path_add_parse
    # select phrases
    command = "%s %s %s" % (project.get_selector_path(), path_base_clean, path_add_clean)
    path_phrases = exec_safe(command, 'phrases.src')
    if not path_phrases:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

@staff_member_required
def project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    breadcrumbs = []
    breadcrumbs.append(dict(name='Home', url='translation:index'))
    breadcrumbs.append(dict(name='Project: %s' % project.name))

    phrases = project.phrase_set
    num_available_tokens = phrases.aggregate(Sum('num_tokens'))['num_tokens__sum']
    corpora = project.corpus_set.filter(covered=False)
    base_corpora = project.corpus_set.filter(covered=True)
    translations = Translation.objects.filter(project=project).exclude(trg='')
    num_translated_tokens = translations.aggregate(Sum('src_phrase__num_tokens'))['src_phrase__num_tokens__sum']
    confirmed = translations.filter(confirmed=True)
    num_confirmed_tokens = confirmed.aggregate(Sum('src_phrase__num_tokens'))['src_phrase__num_tokens__sum'] or 0
#    caption_ratio = 0
#    if images.count() > 0:
#        caption_ratio = round(100*captions.count()/images.count(), 2)
#    confirm_ratio = 0
#    if confirmed.count() > 0:
#        confirm_ratio = round(100*confirmed.count()/captions.count(), 2)
#
    context = {
        "corpus_form": CorpusForm().protect(project=project),
        "upload_form": UploadForm(),
#        "project_form": ProjectForm(instance=project),
        "project_form": ProjectForm(instance=project).protect(),
        "project": project,
        "phrases": phrases,
        "corpora": corpora,
        "base_corpora": base_corpora,
        "translations": translations,
#        "caption_ratio": caption_ratio,
        "confirmed": confirmed,
#        "confirm_ratio": confirm_ratio,
#        "message": None,
        'breadcrumbs': breadcrumbs,
        "num_available_tokens": num_available_tokens,
        "num_translated_tokens": num_translated_tokens,
        "num_confirmed_tokens": num_confirmed_tokens,
    }
#
#    if request.method == 'POST':
#        if 'file' in request.FILES:
#            # file upload
#            save_uploaded(request, project)
#        else:
#            # project update
#            p = ProjectForm(request.POST, instance=project)
#            p.save()
#            messages.success(request, 'Successfully updated project')
#        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return render(request, 'translation/staff/project.html', context)

@login_required
def skip(request, translation_id):
    translation = get_object_or_404(Translation, id=translation_id)
    translation.delete()
    form = ReportForm(request.POST)
    report = form.save(commit=False)
    phrase = get_object_or_404(Phrase, id=report.phrase_id)
    report.save()
    messages.success(request, 'Successfully skip the previous translation.')
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

@login_required
def translations(request, user_id=None, project_id=None, sort_key = "", reverse = "0"):
    user = None
    project = None
    breadcrumbs = []
    breadcrumbs.append(dict(name='Home', url='translation:index'))
    breadcrumbs.append(dict(name='Translation List'))
    translations = Translation.objects.exclude(trg='')
    if user_id:
        user = get_object_or_404(User, pk=user_id)
        translations = translations.filter(project__active = True)
        translations = translations.filter(editor_id = user_id)
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
        translations = translations.filter(project_id = project_id)
    if sort_key:
        try:
            translations = translations.order_by(sort_key)
        except Exception as e:
            raise Http404
    if reverse == '1':
        translations = translations.reverse()
    page = get_page(request, translations, 100)

    table_columns = []
    if request.user.is_staff:
        pass
        table_columns.append(dict(align="center", type="toggle",   key="confirmed",    name="Admin Checked",))
        table_columns.append(dict(align="center", type="text",   key="editor",       name="Editor"))
        table_columns.append(dict(align="center", type="text",   key="edit_date",    name="Edit Date"))
        table_columns.append(dict(align="left", type="text",   key="src",    name="Source"))
        table_columns.append(dict(align="left", type="text",   key="trg",    name="Target"))
        table_columns.append(dict(align="center", type="text",   key="confidence",    name="Confidence Level"))
        table_columns.append(dict(align="center", type="edit",   name="Edit"))
    else:
        table_columns.append(dict(align="center", type="toggle",   key="confirmed",    name="Admin Checked",))
        table_columns.append(dict(align="center", type="text",   key="project", name="Project"))
        table_columns.append(dict(align="center", type="text",   key="edit_date",    name="Edit Date"))
        table_columns.append(dict(align="left", type="text",   key="src",    name="Source"))
        table_columns.append(dict(align="left", type="text",   key="trg",    name="Target"))
        table_columns.append(dict(align="center", type="text",   key="confidence",    name="Confidence Level"))
        table_columns.append(dict(align="center", type="edit",   name="Edit"))
    context = {
        'breadcrumbs': breadcrumbs,
        'user': user,
        'project': project,
        'translations': page,
        'page': page,
        'sort_key': sort_key,
        'reverse': reverse,
        'table_columns': table_columns,
    }
    if request.user.is_staff:
        return render(request, 'translation/staff/translations.html', context)
    else:
        return render(request, 'translation/annotator/translations.html', context)

#@staff_member_required
#def captions(request, project_id, sort_key="", reverse='0'):
#    project = get_object_or_404(Project, pk=project_id)
#    breadcrumbs = []
#    breadcrumbs.append(dict(name='Home', url='manage:index'))
#    breadcrumbs.append(dict(name='Project: %s'%project.name, url='manage:project', args=(project_id,)))
#    breadcrumbs.append(dict(name='Annotation List'))
#    captions = Caption.objects.filter(image__project = project)
#    table_columns = []
#    table_columns.append(dict(align="center", type="toggle", key="confirmed",    name="Confirmed",))
#    table_columns.append(dict(align="center", type="text",   key="editor",       name="Annotator"))
#    table_columns.append(dict(align="center", type="text",   key="edit_date",    name="Edit Date"))
#    table_columns.append(dict(align="center", type="file",   key="image__file__path", name="Video / Image"))
#    table_columns.append(dict(align="center", type="edit",   name="Edit"))
#    table_columns.append(dict(align="left",   type="text",   key="text", name="Caption Text"))
#    if sort_key:
#        try:
#            captions = captions.order_by(sort_key)
#        except Exception as e:
#            raise Http404
#    if reverse == '1':
#        captions = captions.reverse()
#    page = get_page(request, captions, 100)
#    context = {
#        'project': project,
#        'breadcrumbs': breadcrumbs,
#        'captions': page,
#        'page': page,
#        'sort_key': sort_key,
#        'reverse': reverse,
#        'table_columns': table_columns,
#    }
#    return render(request, 'project_manage/captions.html', context)
#

@login_required
def update(request, model, id):
    if request.method == 'POST':
        if model == 'project':
            project = get_object_or_404(Project, pk=id)
            form = ProjectForm(request.POST, instance=project)
            #project = form.save(commit=False)
            project = form.save()
            if project.multiplicity < 1:
                messages.error(request, "Project multiplicity shoulde be positive")
            else:
                project.update_date = datetime.now()
                project.save()
                messages.success(request, "Successfully created project: %s" % project.name)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

@staff_member_required
def upload(request, model):
    if request.method == 'POST':
        if model == 'corpus':
            corpus_form = CorpusForm(request.POST, request.FILES)
            f = File()
            if corpus_form.is_valid():
                f.base = 'project_%s/corpus' % corpus_form.cleaned_data['project'].id
            upload_form = UploadForm(request.POST, request.FILES, instance=f)
            if upload_form.is_valid() and corpus_form.is_valid():
                #save_corpus(request)
                f = upload_form.save()
                corpus = corpus_form.save(commit = False)
                corpus.file = f
                corpus.save()
                messages.success(request, 'Successfully uploaded: "%s" (%s)' % (corpus.name, f.info.name))
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

