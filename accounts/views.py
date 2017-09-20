# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

from django.contrib.auth import logout as auth_logout

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('annotate:index'))

