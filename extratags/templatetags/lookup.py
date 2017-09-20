# -*- coding: utf-8 -*-

from django import template
from django.db import models

register = template.Library()

@register.filter(name='lookup')
def lookup(obj, key, default=""):
    if isinstance(obj, models.Model):
        if hasattr(obj, key):
            val = getattr(obj,key)
            if hasattr(val,'__call__'):
                return val()
            else:
                return val
        elif key.find('__') > 0:
            field1, fields2 = key.split('__', 1)
            if hasattr(obj, field1):
                return lookup(getattr(obj, field1), fields2, default)
            else:
                return default
    elif hasattr(obj, key):
        return getattr(obj,key)
    elif isinstance(key, dict):
        if key in obj:
            return obj[key]
        else:
            return default
    elif isinstance(obj, list):
        try:
            return obj[key]
        except:
            return default
    else:
        return default

