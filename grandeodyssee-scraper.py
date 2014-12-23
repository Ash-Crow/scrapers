#!/usr/bin/env python
# grandeodyssee-scraper.py


import requests
from bs4 import BeautifulSoup

results_url = 'http://www.grandeodyssee.com/fr/16/resultats/'

response = requests.get(results_url)
soup = BeautifulSoup(response.text)

mushers = soup.select('aside.gab-identite div')

print ('"Nom", "Pays", "Années"')

for m in mushers:
	full_name_list = m.h3.contents
#	full_name.replace('<br/>',' ') 
	full_name = full_name_list[0] + ' ' + full_name_list[2].title()
	country = m.span.text
	years = m.p.text

	print('"' + full_name + '", "' + country + '", "' + years + '"')