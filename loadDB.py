#!/usr/bin/python3

# loadDB.py <import_file> <database>

# loadDB.py takes the import file as CSV and loads into the specified SQLite3 database

# Import file schema
# 42.678643,-83.124376,KDTI-FM,/info/KDTI-FM

# Database Schema
# coord(lat FLOAT, lon FLOAT, callsign VARCHAR(20), url VARCHAR(20))

# Includes and imports
import os
import sys
import sqlite3

# Initial Defines
import_arg = sys.argv[1]
db_arg = sys.argv[2]

# Function Definitions

########################
# BEGIN MAIN EXECUTION #
########################

# Check import file exists and is readable
if not os.path.isfile(import_arg) and os.access(import_arg, os.R_OK):
    print('ERROR: Import file not ready.')
    exit()

# Check if dest database exists or not and is loadable
if not os.path.isfile(db_arg) and os.access(db_arg, os.W_OK):
    print('ERROR: Destination database not ready.')
    exit()

try:

# Open input file
    if (os.path.isfile(import_arg) and os.access(import_arg, os.R_OK)):
        import_file = open(import_arg, 'r')
    else:
        print('Whoa! Something\'s wrong! Check import file.')
    
# Define import list 
    import_list = []

# ** Primary Loop **
    for import_line in import_file:
        import_clean = import_line.replace('\n', '')
        import_items = import_clean.split(',')
        lat = float(import_items[0])
        lon = float(import_items[1])
        callsign = import_items[2]
        web_dir = import_items[3]
        line_list = (lat, lon, callsign, web_dir)
        # print(line_list)
        import_list.append(line_list)

# ** End of Loop **

    print('Sizeof list: ' + str(len(import_list)))

# Close import files
    import_file.close()

except OSError:
    print('Derp!! Caught an OS exception. ABORT!!')
    exit()

try:

# Open database
    con = sqlite3.connect(db_arg)
    cur = con.cursor()

# Create table in database
    cur.execute("CREATE TABLE coord(lat FLOAT, lon FLOAT, callsign VARCHAR(20), url VARCHAR(20))")
    con.commit()

# Load data into table
    cur.executemany("INSERT INTO coord VALUES(?, ?, ?, ?)", import_list)
    con.commit()

# Close database
    con.close()

except sqlite3.OperationalError:
    print('Derp!! Caught an SQLite3 exception. ABORT!!')
    exit()

# Cool, we don't abort execution early.
print("Yay, we ran out of code. Success!!")