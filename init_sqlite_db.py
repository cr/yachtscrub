#!/usr/bin/env python3

import sqlite3

con = sqlite3.connect('boats.db')
con.execute('''CREATE TABLE markets
         (name      TEXT    NOT NULL UNIQUE,
         url       TEXT    NOT NULL UNIQUE);''')
con.execute("INSERT INTO markets (name, url) values(?,?)", ("2yachts","2yachts.com"))
con.commit()
con.execute('''CREATE TABLE boats
         (market   INT     NOT NULL,  -- market.rowid
         boatid   INT     NOT NULL,  -- id on marketplace, hopefully always numeric!
         name     TEXT    NOT NULL,
         created  DATETIME,
         changed  DATETIME,
         price    INT,               -- in standard currency, rounded, no cents etc.
         FOREIGN KEY(market) REFERENCES markets(rowid));''')

con.close()

print("SQLite database 'boats.db' created")
exit(0)
