# Copyright 2019-2025 by Sergio Valqui. All rights reserved.
# https://www.zenrows.com/blog/scraping-javascript-rendered-web-pages#extract-html
import json

import bs4.element
import requests
from bs4 import BeautifulSoup
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from os import path
import sys
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

service = Service()

options = webdriver.FirefoxOptions()
options.add_argument("--headless=new")
driver = webdriver.Firefox(service=service, options=options)

