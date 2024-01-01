#!/usr/bin/python3

# revgeo.py <database> <latitude> <longitude> <precision>

# RevGeo CLI application takes the latitude and longitude and returns likely callsigns

# Import file schema
# 42.678643,-83.124376,KDTI-FM,/info/KDTI-FM

# Database Schema
# coord(lat FLOAT, lon FLOAT, callsign VARCHAR(20), url VARCHAR(20))

# Select statement
# SELECT * FROM coord WHERE lat between 43.57 and 43.58 AND lon between -84.78 and -84.77;

# Includes and imports
import os
import sys
import sqlite3

# Initial Defines
db_arg = sys.argv[1]
lat_arg = sys.argv[2]
lon_arg = sys.argv[3]
prec_arg = sys.argv[4]

# Function Definitions
def isFloat(str_num):
    try:
        float(str_num)
        return True
    except ValueError:
        return False
    
def chkLat(lat=lat_arg):
    # Is numeric
    if not isFloat(lat):
        return False
    # Is within expected range (not in CA or MX)
    float_lat = float(lat)
    if float_lat < 24 or float_lat > 49:
        return False
    return True

def chkLon(lon=lon_arg):
    # Is numeric
    if not isFloat(lon):
        return False
    # Is within expected range (not in the ocean)
    float_lon = float(lon)
    if float_lon < -125 or float_lon > -66:
        return False
    return True

def chkPrec(prec=prec_arg):
    # Is numeric
    if not prec.isdigit():
        return False
    # Is within expected range (0 - 5)
    int_prec = int(prec)
    if int_prec < 0 or int_prec > 5:
        return False
    return True

def genRange(coord):
    exit()

########################
# BEGIN MAIN EXECUTION #
########################

# Sanity check latitude, longitude and precision inputs
if not chkLat(lat_arg) and chkLon(lon_arg) and chkPrec(prec_arg):
    print('Error: Invalid inputs. Check for proper usage.')
    exit()

# Check database exists and is readable
if not os.path.isfile(db_arg) and os.access(db_arg, os.R_OK):
    print('ERROR: Database not ready.')
    exit()

try:

# Open database
    con = sqlite3.connect(db_arg)
    cur = con.cursor()

# Query database
    # for row in cur.execute('SELECT * FROM coord WHERE lat between 43.57 and 43.58 AND lon between -84.78 and -84.77;'):

# Close database
    con.close()

except sqlite3.OperationalError:
    print('Derp!! Caught an SQLite3 exception. ABORT!!')
    exit()

# Cool, we don't abort execution early.
print("Yay, we ran out of code. Success!!")