#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup

def ordinal(value):
    """
    Converts zero or a *positive* integer (or its string 
    representation) to an ordinal value.
    """
    try:
        value = int(value)
    except ValueError:
        return value

    if value % 100//10 != 1:
        if value % 10 == 1:
            ordval = u"%d%s" % (value, "st")
        elif value % 10 == 2:
            ordval = u"%d%s" % (value, "nd")
        elif value % 10 == 3:
            ordval = u"%d%s" % (value, "rd")
        else:
            ordval = u"%d%s" % (value, "th")
    else:
        ordval = u"%d%s" % (value, "th")

    return ordval

root_url = 'http://www.xkcd.com'
index_url = root_url + '/archive/index.html'

response = requests.get(index_url)
soup = BeautifulSoup(response.text)

header = "qid, s854|url source, Lfr, Len, Lbr, Lde, Dfr, Dde, Den, p31, p361|partie de, p433|numéro, p577|date de publication, p50|auteur, p854|url"

print(header)

episodes = soup.select('div#middleContainer a')
episodes.reverse()

for a in episodes:
	title = "\"" + a.get_text() + "\"" or ""
	urlbit = a.attrs.get('href') or ""
	episode_url = root_url + urlbit
	episodenumber = urlbit.replace("/","")

	descriptions = "strip de xkcd n° " + episodenumber + ", Folge des Webcomics xkcd, " + ordinal(episodenumber) + " strip of the webcomic xkcd"
	#date = a.attrs.get('title') or ""
	date = "+0000000" + '-'.join(["{0:0>2}".format(v) for v in a.attrs.get('title').split("-")]) + "T00:00:00Z/11" or ""


	print("," + index_url + "," + title + "," + title + "," + title + "," + title + ","
	+ descriptions + ", q838795|Comic strip , q13915|xkcd, " + episodenumber + "," + date + ", q285048|Randall," + episode_url)
