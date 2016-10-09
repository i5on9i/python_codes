# coding=utf-8
from __future__ import unicode_literals
import re

import requests

__author__ = 'namh'


class JdnyRssParser(object):
    def __init__(self):
        self.url = 'http://pod.ssenhosting.com/rss/rrojia2/rrojia2.xml'

    def open(self):
        r = requests.get(self.url)
        r.encoding = 'utf-8'

        rlist = re.findall(r'<item>.*?<title>(.*?)</title>.*?'
                           r'<itunes\:subtitle>(.*?)</itunes\:subtitle>.*?'
                           r'<guid>(.*?)</guid>.*?'
                           r'<pubDate>(.*?)\d{2}:\d{2}:\d{2}\s\+\d{4}</pubDate>'
                           , r.text, re.DOTALL)

        for rr in rlist:
            title = rr[0]
            sre = re.search(r'(\d+)회', title)

            space = '<br>'
            if sre is not None:
                lastchar = sre.group(1)[-1]
                if lastchar == '6' or lastchar == '1':
                    space = '<br><br>'
            print("<a href={fpath}>{title} - {subtitle}</a>, {pubdate}{space}"\
                .format(fpath=rr[2], pubdate=rr[3],
                        title=rr[0], subtitle=rr[1],
                        space=space))




def main():
    """

    :return:
    """
    parser = JdnyRssParser()
    print (parser.open())


if __name__ == '__main__':
    main()
