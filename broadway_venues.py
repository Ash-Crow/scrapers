import requests
from bs4 import BeautifulSoup

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


verbose = 1


def browse_entries(topic, start, end):
	base_url = 'http://www.ibdb.com/{}}/View/'.format(topic)
	entries_list= []
	for i in range(1, 10000):
		venue_url = base_url + str(i)
		response = requests.get(venue_url)
		soup = BeautifulSoup(response.text)
		venue_name = soup.title.text
		if venue_name != 'Error':
			venue_name = venue_name.split("|")[0].strip()
			if verbose:
				print('{} ; "{}" ; "{}"'.format(i, venue_name, venue_url))

			entries_list.append(i, venue_name, venue_url)

		elif verbose:
			print('No venue with identifier {}'.format(i))

	return entries_list

