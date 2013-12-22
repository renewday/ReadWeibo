# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import Category, Weibo, Comment
from ReadWeibo.account.models import Account

from main import Config

import networkx as nx
import sys, re, logging

def gen_graph(save_path, start_idx=0, max_cnt=1000):

    import jieba
    import jieba.posseg as pseg
    jieba.load_userdict(u"/etc/jieba/jieba.dic")

    G = nx.Graph()
    wb_cnt = Weibo.objects.filter(retweeted_status__exact=None).count()
    if max_cnt>0 and wb_cnt>max_cnt+start_idx:
        wb_cnt = max_cnt+start_idx
    page_size = min(100, wb_cnt)
    wb_idx = start_idx

    while wb_idx<wb_cnt:

        logging.info(u'**********Collected %d of %d weibos, with %d nodes, %d edges***********' %
                (wb_idx, wb_cnt, G.number_of_nodes(), G.number_of_edges()))

        wb_list = Weibo.objects.filter(retweeted_status__exact=None).order_by('-created_at')[wb_idx:wb_idx+page_size]
        wb_idx += len(wb_list)

        for wb in wb_list:

            logging.debug(u"\nDealing with %s" % wb)
            G.add_node(wb.w_id, category=wb.real_category, tp=u'weibo')

            w_user =[] ; w_user.append(wb.owner)
            w_text = wb.text

            for retweet in wb.retweet_status.all():
                w_text += retweet.text
                w_user.append(retweet.owner)

            for comment in wb.comments.all():
                w_text += comment.text
                w_user.append(comment.owner)

            for user in w_user:
                if not user:
                    continue
                G.add_node(user.w_uid, category=user.real_category, tp=u'user')
                G.add_edge(wb.w_id, user.w_uid, weight=1.0)
                logging.debug('Add <%s, %s>' % (wb, user))
            w_text = re.sub("@[^\s@:]+", "", w_text)
            for w in pseg.cut(w_text.lower()):
                if len(w.word)>1 and u'n' in w.flag:
                    G.add_node((w.word), tp=u'word')
                    G.add_edge((w.word), wb.w_id, weight=1.0)
                    logging.debug(u'Add <%s, %s>' % (wb, w.word))

    #nx.write_pajek(G, save_path, encoding='UTF-8')
    #nx.write_graphml(G, save_path, encoding='UTF-8', prettyprint=True)
    if save_path:
        nx.write_yaml(G, save_path, encoding='UTF-8')
    return G

def load_graph(load_path, encoding='UTF-8'):
    logging.info('Loading graph from file:%s' % load_path)
    #G=nx.read_pajek(load_path, encoding=encoding)
    #G=nx.read_graphml(load_path, node_type=unicode)
    G=nx.read_yaml(load_path)
    logging.info('Loaded %d nodes and %d edges' % (G.number_of_nodes(), G.number_of_edges()))

    dist = {}
    for key, node in G.nodes(data=True):
        tp = node['tp']
        if tp in dist:
            dist[tp] += 1
        else:
            dist[tp] = 1
    logging.info(dist)
    return G

if __name__ == '__main__':
    for i in range(8):
        _path = u"test_data/graph-500-%d.yaml" % (i+3);
        _start_idx=100*(i+4)
        gen_graph(save_path=_path, max_cnt=500, start_idx=_start_idx)
        #G = load_graph(load_path=_path,)
    pass


