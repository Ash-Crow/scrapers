#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import re
import requests
from bs4 import BeautifulSoup


def get_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    h1s = soup.find_all('h1')
    for h in h1s:
        names = repr(h).split('<br/>')
        if len(names) > 1:
            first_name = names[0].replace('<h1>', '')
            last_name = names[1].replace('</h1>', '')
            return first_name, last_name

path = "/home/sylvain/Dropbox/jeux de données/rada/"
filename = "list-of-rada-students-with-wp-articles.txt"
# filename = "testfile.txt"
f = open(path + filename, 'r')
for line in f:
    if '<ref>' in line:
        match = re.search("\|url=(?P<url>.*)}}<\/ref>$", line)
        if(match):
            url = match.group('url')

            if len(url) and '{{,}}' not in url:
                first, last = get_data(url)
                line = line.replace('| [[',
                                    '| <!-- {} {} --> [['.format(last, first))
                line = line.replace('=en|si',
                                    '=en|titre={} {}|si'.format(first, last))

    print(line),
f.close()
