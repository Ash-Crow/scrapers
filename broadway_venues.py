import requests
import sys
from bs4 import BeautifulSoup

verbose = 1


def browse_entries(item_type, start, end):
	base_url = 'http://www.ibdb.com/{}/View/'.format(item_type)
	entries_list= []
	for i in range(start, end):
		item_url = base_url + str(i)
		response = requests.get(item_url)
		soup = BeautifulSoup(response.text)
		item_name = soup.title.text
		if item_name != 'Error':
			item_name = item_name.split("|")[0].strip()
			if verbose:
				print('{} ; "{}" ; "{}"'.format(i, item_name, item_url))

			entries_list.append((i, item_name, item_url))

		elif verbose:
			print('No {} with identifier {}'.format(item_type.lower(), i))

	return entries_list

known_types = ['Award', 'Character', 'Person', 'Production', 'Show', 'Venue']
# Cycle trough the races
if len(sys.argv) > 1:
    if sys.argv[1] in known_types:
        if len(sys.argv) == 2:
                entries_list = browse_entries(sys.argv[1], 1000, 10000)
        elif len(sys.argv) == 4 and  all(arg.isdigit() for arg in sys.argv[2:]):
            minimum = int(sys.argv[2])
            maximum = int (sys.argv[3])
            if minimum < maximum:
                entries_list = browse_entries(sys.argv[1], minimum, maximum)
            else:
                raise ValueError("The inferior limit must be inferor to superior limit!")
        else:
            raise ValueError("Invalid arguments or bad number of arguments")

        for e in entries_list:
            print('{} ; "{}" ; "{}"'.format(e[0], e[1], e[2]))

    else:
        raise ValueError("Type of venue unknown")
else:
    print('syntax: python broadway_venues.py [type] [inferior limit] [superior limit]')
