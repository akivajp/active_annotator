# -*- coding: utf-8 -*-

from django import template
from collections import Iterable

register = template.Library()

@register.filter(name='head')
def head(obj, num, default=""):
    if isinstance(obj, Iterable):
        elements = list()
        num = int(num)
        for elem in obj:
            if len(elements) >= num:
                break
            elements.append(elem)
        return elements
    else:
        return default

