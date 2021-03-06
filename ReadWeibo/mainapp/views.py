# !/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
#from ipware.ip import get_ip_address_from_request
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from django.utils import simplejson

from ReadWeibo.mainapp.models import Weibo, Category
from ReadWeibo.account.models import Account
from libweibo import weibo
from main import Config
from ranking.TriRank import TriRank
from ranking.ManifoldRank import ManifoldRank
from ranking import DataUtil as du

from time import sleep
import itertools
import datetime
import logging
import thread
import re

# global static variables
_DEBUG = True
_mimetype = u'application/javascript, charset=utf8'

wclient = weibo.APIClient(app_key = Config.WEIBO_API['app_key'],
                       app_secret = Config.WEIBO_API['app_secret'],
                     redirect_uri = Config.WEIBO_API['callback_url'])

all_categories = Category.objects.exclude(category_id=0)
#default_user = Account.objects.get(w_name='WeBless')

G = du.load_graph('/home/plex/wksp/projects/ReadWeibo/ranking/data/graph500.yaml')
#ranker = TriRank(G, 133)
#ranker.build_model()

def search(request, query):
    mr = ManifoldRank(G, topic_words=query)
    mr.rank()
    weibo_list = mr.test(verbose=True)
    #weibo_list = ranker.test(query)
    template_var = {}
    template_var['weibo_list'] = weibo_list
    template_var['all_categories'] = all_categories
    template_var['authorize_url'] = wclient.get_authorize_url()

    return render_to_response("weibos.html", template_var,
                              context_instance=RequestContext(request))

def home(request, category_id=1):
    return show_weibo_for_labeling(request)

def trending(request):

    logging.info('trending view, current login user: %s' % request.user)

    weibo_list = Weibo.objects.filter(relevance__gt=0).order_by("-relevance")[:60]

    template_var = {}
    template_var['weibo_list'] = weibo_list
    template_var['all_categories'] = all_categories
    template_var['authorize_url'] = wclient.get_authorize_url()

    return render_to_response("weibos.html", template_var,
                              context_instance=RequestContext(request))


def show_weibo_for_labeling(request):
    ''' show statuses for labeling '''

    logging.info('show_weibo_for_labeling current login user: %s' % request.user)


    weibo_list = Weibo.objects.filter(real_category=0).filter(owner__in=Account.objects.filter(real_category=1))[:40]
    #.filter(retweeted_status__exact=None)

    template_var = {}
    template_var['weibo_list'] = weibo_list
    template_var['all_categories'] = all_categories
    template_var['authorize_url'] = wclient.get_authorize_url()

    return render_to_response("weibos.html", template_var,
                              context_instance=RequestContext(request))

def show_weibos_predict(request, category_id=0, show_predict=True):
    return show_weibos(request, category_id, show_predict)

def show_weibos(request, original=True, category_id=0, show_predict=False):
    try:
        category = Category.objects.get(category_id=category_id)
    except:
        logging.warn('No category found')
        return HttpResponse('No category found for id:%s' % category_id)

    #ip = get_ip_address_from_request(request)

    #logging.info('current login user: %s, show %s, ip:%s' % (request.user, category, ip))

    template_var = {}
    if show_predict:
        watch_weibo = Weibo.objects.filter(predict_category=category_id)
    else:
        watch_weibo = Weibo.objects.filter(real_category=category_id)

    if original:
        watch_weibo = watch_weibo.filter(retweeted_status__exact=None)[:40]
    else:
        watch_weibo = watch_weibo[:40]

    template_var['weibo_list'] = watch_weibo
    template_var['category_id'] = category_id
    template_var['all_categories'] = all_categories
    template_var['authorize_url'] = wclient.get_authorize_url()

    logging.info('category weibos count:%d' % len(watch_weibo))

    return render_to_response("weibos.html", template_var,
                              context_instance=RequestContext(request))

def set_weibo_category(request):
    if not request.user.is_authenticated() or not request.user.is_superuser:
        return HttpResponse(simplejson.dumps(False), _mimetype)
    if not request.is_ajax():
        return HttpResponse('ERROR:NOT AJAX REQUEST')
    post_data = simplejson.loads(request.raw_post_data)
    try:
        wb = Weibo.objects.get(w_id=post_data['w_id'])
        category_id = post_data['category']
        category = Category.objects.get(category_id=category_id)
        wb.real_category = category_id
        wb.save()

        if wb.retweeted_status:
            original_status = wb.retweeted_status
            original_status.real_category = category_id
            original_status.save()
            for retweet in original_status.retweet_status.all():
                retweet.real_category = category_id
                retweet.save()
    except:
        logging.warn('post_data error:%s' % post_data)
        return HttpResponse(simplejson.dumps(False), _mimetype)
    return HttpResponse(simplejson.dumps(category.name), _mimetype)


