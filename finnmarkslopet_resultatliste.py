#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup, NavigableString
import datetime
import json
import os               # Files and folder manipulations
import re               # Regular expressions
import csv              # CSV file manipulations 
import sys
from collections import Counter
from termcolor import colored

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

def resultatliste(r_id):
	pass

# Main part
if len(sys.argv) == 2:
    if sys.argv[1].isdigit():
        resultatliste(sys.argv[1])
    else:
        raise ValueError("Invalid argument")
else:
    raise ValueError("Please indicate the race number")
