#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
from datetime import datetime
import sqlite3
from os.path import exists
import math

def get_marketid(marketname):
    "retrieves marketid from db"
    cur.execute("SELECT rowid FROM markets WHERE name = ?", (marketname,))
    row = cur.fetchone()
    if (row is None):
        return
    else:
        return row[0]

def get_boat(marketid, boatid):
    "retrieves a boat from db"
    cur.execute('''SELECT rowid, boatid, created, changed, name, price 
                    FROM boats
                    WHERE market = ? AND boatid = ?''', (marketid, boatid,))
    return cur.fetchone()

def get_market_boats(marketid):
    "retrieves all boats of a market from db"
    cur.execute('''SELECT rowid, boatid, created, changed, name, price 
                    FROM boats
                    WHERE market = ?''', (marketid,))
    return cur.fetchall()

def add_boat(marketid, boatid, created, changed, name, price, year):
    "stores a boat in db"
    cur.execute('''INSERT INTO boats (market, boatid, created, changed, name, price, year)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
	(marketid, boatid, created, changed, name, price, year))
    con.commit()
    return

con = sqlite3.connect('boats.db')
cur = con.cursor()

# 2yachts.com
marketid = get_marketid("2yachts")
if(exists("2yachts.html")): # use cached result
    fsauce = open("2yachts.html")
    soup = BeautifulSoup(fsauce.read(), 'html.parser')
else:
    searchurl = 'https://2yachts.com/de/sale?model=&price_from=50000&price_to=200000&length_from=12&length_to=21&production_from=1990&production_to=2017&region_name=&category=&category%5B%5D=90&cabin_count_from=2&cabin_count_to=6&extend=1&sort=added'
    sauce = requests.get(searchurl, cookies=dict(currency='EUR'))
    soup = BeautifulSoup(sauce.content, 'html.parser')

# TODO: retrieve all results (pagination!)
#results = soup.find("h2", class_="market-header__note").span.string.replace(",","")
#pages   = math.ceil(results / 50)
# 2yachts: &page=2&per-page=50
boats = soup.find_all("div", "boat-row")
for boat in boats:
    boatid = boat.find("span")["data-entityid"]
    boatname = boat.find("span", itemprop="name").string
    boaturl = boat.find("meta", itemprop="url")["content"]
    boatprice = boat.find("meta", itemprop="price")["content"]
    boatyear = boat.find("ul", itemprop="description").li.string
    #boatcur = boat.find("meta", itemprop="priceCurrency")["content"]
    boatts = datetime.strptime(boat.find("div", class_="boat-row__added").string.strip(), '%H:%M %d.%m.%Y')
    
    dbboat = get_boat(marketid, boatid)
    if (dbboat is None): 
        print("new boat id: "+boatid + " date: " + boatts.isoformat() + " name: " + boatname + " price: " + boatprice + " year: " + boatyear)
        add_boat(marketid, boatid, boatts, boatts, boatname, boatprice, boatyear)
    else:
        print("previously known boat id: " + boatid)
    # TODO: find boats in DB but no longer in results (and delete them in db)

con.close()
exit(0)
#eof. This file has not been truncate
