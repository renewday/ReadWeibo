# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
Over all configuration

Created on Aug 29, 2013
@author: plex
'''
import logging, sys

logging.basicConfig(level=logging.INFO,
				format='%(asctime)s : %(name)-8s : %(levelname)s : %(message)s',
				datefmt='%Y-%m-%d %H:%M:%S',
				filename='full.log',
				filemode='a+')

formatter = logging.Formatter('%(asctime)s : %(name)-8s: %(levelname)-8s %(message)s',
							'%Y-%m-%d %H:%M:%S')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logging.info("running %s" % ' '.join(sys.argv))

#weibo app settings
# site_url = u'http://www.readweibo.com'
# weibo_app_key = u'3233912973'
# weibo_app_secret = u'289ae4ee3da84d8c4c359312dc2ca17d'
# callback_url = site_url + u'/weibo_callback'
# callback_rm_url = site_url + u'/weibo_callback_rm'
site_url = u'http://115.28.165.49/'#u'http://10.110.25.49:8000' #
weibo_app_key = u'3482624382'
weibo_app_secret = u'af44e0e7c3a7a55760d437cea207dd22'
callback_url = site_url + u'/weibo_callback'
callback_rm_url = site_url + u'/weibo_callback_rm'
default_access_token = u'2.00KDQyqBAhjgnDb478ce55bc7pe2UB'
default_access_token_expires_in = u'1539410603'

#Database settings

if __name__=='__main__':
	logging.warn('a warn message')
	pass
