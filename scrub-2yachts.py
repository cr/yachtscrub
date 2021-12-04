#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
from datetime import datetime

# 2yachts.com
searchurl = 'https://2yachts.com/de/sale?model=&price_from=50000&price_to=200000&length_from=12&length_to=21&production_from=1990&production_to=2017&region_name=&category=&category%5B%5D=90&cabin_count_from=2&cabin_count_to=6&extend=1&sort=added'
sauce = requests.get(searchurl, cookies=dict(currency='EUR'))
soup = BeautifulSoup(sauce.content,'html.parser')

boats = soup.find_all("div", "boat-row")
for boat in boats:
    boatid = boat.find("span")["data-entityid"]
    boatname = boat.find("span", itemprop="name").string
    boaturl = boat.find("meta", itemprop="url")["content"]
    boatprice = boat.find("meta", itemprop="price")["content"]
    boatcur = boat.find("meta", itemprop="priceCurrency")["content"]
    boatts = datetime.strptime(boat.find("div", class_="boat-row__added").string.strip(), '%H:%M %d.%m.%Y')
    print("id: "+boatid + " date: " + boatts.isoformat() + " name: " + boatname + " price: " + boatprice + " curr: " + boatcur)

