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
    cur.execute('''SELECT rowid, boatid, created, changed, name, price, year 
                    FROM boats
                    WHERE market = ? AND boatid = ?''', (marketid, boatid,))
    return cur.fetchone()

def get_market_boats(marketid):
    "retrieves all boats of a market from db"
    cur.execute('''SELECT rowid, boatid, created, changed, name, price, year 
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

def get_results(page):
    if(exists(marketname + "_page" + str(page) + ".html")): # use cached result
        print("using cached file for page " + str(page))
        fsauce = open(marketname + "_page" + str(page) + ".html")
        soup = BeautifulSoup(fsauce.read(), 'html.parser')
    else:
        searchurl = 'https://2yachts.com/de/sale?model=&price_from=71000&price_to=230000&length_from=12&length_to=21&production_from=1990&production_to=2018&region_name=&category=&category%5B%5D=90&cabin_count_from=0&cabin_count_to=20&extend=1&sort=added'
        if (page > 1):
            searchurl.append('&per-page=50&page='+page)
        sauce = requests.get(searchurl, cookies=dict(currency='EUR'))
        soup = BeautifulSoup(sauce.content, 'html.parser')
    return soup


con = sqlite3.connect('boats.db')
cur = con.cursor()

marketname = "2yachts"
# 2yachts.com
marketid = get_marketid(marketname)
market_per_page = 50
page = 1
pages = 1 # set real value later

while (page <= pages):
    soup = get_results(page)

    # figure out once how many pages there really are
    if (pages == 1):
        results = soup.find("h2", class_="market-header__note").span.string.replace(",","")
        pages   = math.ceil(int(results) / market_per_page)
        print("there are " + str(results) + " results on " + str(pages) + " pages in total")

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
    page += 1
    
con.close()
exit(0)
#eof. This file has not been truncate
