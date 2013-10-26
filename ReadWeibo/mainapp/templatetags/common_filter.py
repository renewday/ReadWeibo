# !/usr/bin/python
# -*- coding: utf-8 -*-

from django import template
from django.template.defaultfilters import stringfilter
from datetime import datetime, timedelta
import re

register = template.Library()

@register.filter
def add_prefix(value, arg):
    """add some prefix for the given string"""
    return arg + str(value)

@register.filter
def get_range(value):
    '''return a list [0,value-1]'''
    return range(value)

@register.filter
def keyvalue(dict, key):
    ''' return dict keyvalue'''
    return dict[key]

@register.filter
def sp_category(categories, category_id):
    for category in categories:
        if category.category_id == category_id:
            return category.name
    return 'INVALID'

@register.filter
def time_passed(pre_time, cur_time=datetime.now()):
    td = cur_time - pre_time
    if td.days>0:
        return '%2d天之前' % td.days

    hours, seconds = divmod(td.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    res = ''
    if hours>0:  res = '%2d小时' % hours
    if minutes>0: res += '%2d分' % minutes
    if seconds>=0: res += '%2d秒' % seconds

    return res + '之前' + str(pre_time)
