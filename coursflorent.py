#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup


base_url = "http://www.coursflorent.fr/ecole/anciens/acteurs"

for page in range(3):
    payload = {'page': page}
    response = requests.get(base_url, params=payload)
    soup = BeautifulSoup(response.text, "lxml")

    alumni = soup.select(".force_content div div")

    for alumnus in alumni:
        name = alumnus.text.title()
        if name and name != "(Comédie Française)":
            print(name)
