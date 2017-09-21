#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import requests
import json

csv_input = "resources/framalibre_liens_wikipedia.csv"


def get_qid(language, title):
    wd_api_url = 'https://wikidata.org/w/api.php'

    params = {
        "action": "wbgetentities",
        "props": "info|labels",
        "format": "json",
        "redirects": "yes",
        "sites": language + 'wiki',
        "titles": title
    }

    response = requests.get(wd_api_url, params=params)
    data = json.loads(response.text)
    qid = list(data['entities'].keys())[0]
    return qid


with open(csv_input, 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')

    for row in reader:
        framalibre_id = row['framalibre_id']
        url = row['url'].split('/')
        wiki = url[2].split('.')[0]
        page = url[-1]
        qid = get_qid(wiki, page)

        print("{}\tP4107\t\"{}\"".format(qid, framalibre_id))
