import urllib
import json


langs = {'en': 'English',
         'sv': 'Swedish',
         'nl': 'Dutch',
         'de': 'German',
         'fr': 'French',
         'war': 'Waray-Waray',
         'ru': 'Russian',
         'ceb': 'Cebuano',
         'it': 'Italian',
         'es': 'Spanish'
}
"""
langs = {'br': 'Breton',
         'cy': 'Welsh'
}
"""

lang_codes = sorted(langs.keys())
lang_sizes = {}

def nb_items(url):
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data["status"]["items"]

print "Number of articles for each language"
for i in lang_codes:
    url = "https://wdq.wmflabs.org/api?q=link[" + i + "wiki]%20and%20noclaim[31:4167836]%20and%20noclaim[31:15647814]%20and%20noclaim[31:4167410]&noitems=1"
    lang_sizes[i] = float(nb_items(url))
    print i, nb_items(url) 

print "\n=============\n"

print "Percentage of common articles"
for i in lang_codes:
    for j in lang_codes:
        if i < j:
            url = "https://wdq.wmflabs.org/api?q=link[" + i  + "wiki]%20and%20link[" + j + "wiki]%20and%20noclaim[31:4167836]%20and%20noclaim[31:15647814]%20and%20noclaim[31:4167410]&noitems=1"
            nb = nb_items(url)
            print "{} - {} : {} common items ({} % of {} Wikipedia - {} % of {} Wikipedia)".format(i, j, nb, round(nb / lang_sizes[i] * 100, 2), langs[i], round(nb / lang_sizes[j] * 100,2), langs[j])