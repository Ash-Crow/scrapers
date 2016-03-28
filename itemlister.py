#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from bs4 import BeautifulSoup


class Article(object):
        def __init__(self, language, site, title):
            self.language = language
            self.site = site
            self.title = title

            if self.site == 'wikipedia':
                self.site_short = 'wiki'
            else:
                self.site_short = self.site

        def get_all_links(self):
            rest_api_url = 'https://rest.wikimedia.org/'
            api_call = rest_api_url + '{}.{}.org/v1/page/html/{}'.format(
                self.language,
                self.site,
                self.title)

            response = requests.get(api_call)
            soup = BeautifulSoup(response.text)
            internal_links = soup.find_all(rel="mw:WikiLink")

            correct_links = []
            for link in internal_links:
                title = link.get('href')[2:]  # links start with "./"
                correct_links.append(title)

            self.get_qids(correct_links)

        def get_qids(self, titles):
            wd_api_url = 'https://wikidata.org/w/api.php'

            params = {
                "action": "wbgetentities",
                "props": "info|labels",
                "format": "json",
                "redirects": "yes",
                "sites": self.language + self.site_short,
                "titles": '|'.join(titles)
            }

            response = requests.get(wd_api_url, params=params)
            data = json.loads(response.text)
            for entity, value in data['entities'].items():
                if entity[0] != '-':
                    print(value['labels'][self.language]['value'], entity)

        def __repr__(self):
            return 'Site : {}.{}.org - Article : {}'.format(
                self.language,
                self.site,
                self.title)


main_article = Article(
                'fr',
                'wikipedia',
                'Utilisateur%3AAsh%20Crow%2Fwikilinks%20test')

main_article.get_all_links()
