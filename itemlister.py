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

            num_links = len(correct_links)
            chunk_size = 50

            print(num_links)

            last = 0
            correct_items = []
            incorrect_items = []
            while last < num_links:
                chunk = correct_links[last:last + chunk_size]
                c_correct, c_incorrect = self.get_qids(chunk)
                correct_items += c_correct
                incorrect_items += c_incorrect

                last += chunk_size

            if len(correct_items):
                print("== {} links with a Wikidata item ==".format(
                    len(correct_items)))
                print("{| class='wikitable'")
                print("! Link !! Item  ")
                for c in correct_items:
                    print('|-')
                    print('| [[{}]] || [[:d:{}]] '.format(c[0], c[1]))
                print('|}')

            if len(incorrect_items):
                print("== {} links without a Wikidata item ==".format(
                    len(incorrect_items)))
                for c in incorrect_items:
                    print('* [[{}]]'.format(c))

        def get_qids(self, titles):
            wd_api_url = 'https://wikidata.org/w/api.php'

            params = {
                "action": "wbgetentities",
                "props": "info|labels",
                "format": "json",
                "redirects": "yes",
                "sites": self.language + self.site_short,
                "titles": '|'.join(titles[:150])
            }

            response = requests.get(wd_api_url, params=params)
            data = json.loads(response.text)
            correct_items = []
            incorrect_items = []
            for entity, value in data['entities'].items():
                if entity[0] != '-':
                    correct_items.append((
                        value['labels'][self.language]['value'],
                        entity))
                else:
                    incorrect_items.append((value['title']))

            return correct_items, incorrect_items

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

main_article = Article(
                'fr',
                'wikipedia',
                'Liste des membres du Sénat de la Communauté')

main_article.get_all_links()
