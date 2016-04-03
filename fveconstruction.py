#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

url = "http://www.fveconstruction.ch/anDetails.asp?RT=2&M=06&R=4&ID=10003401"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')


# First, get the data in a clean list
contact_name = soup.find("span", class_="titreentreprise").string
contact_info_raw = str(soup.find_all("span",
                       class_="entrepriseDef")[0].next_sibling()[0])
contact_info = contact_info_raw.split('<br>')
contact_info = filter(None, contact_info)
del contact_info[-1]

# Now, parse the list to get the actual data
address = ""
contact_data = {}
for line in contact_info:
    split_line = line.split('\xc2\xa0:\xc2\xa0')
    if len(split_line) == 1:
        address += ' ' + line
    else:
        contact_data[split_line[0]] = split_line[1]

contact_data["address"] = address
email = BeautifulSoup(contact_data['e-Mail'])
contact_data['e-Mail'] = email.find('a').string

print(contact_name, contact_data)
