import csv
import re
from xml.dom.minidom import parseString
from urllib import urlopen, quote_plus

yahookey = 'gjG9MBPV34GvRAoz0iM_ehQm.I4r_0XojAClPWoPigTsb4Tz_gON5T6HxckU'
loc_cache = {}

def getlocation(address):
    if address in loc_cache: return loc_cache[address]
    data = urlopen('http://api.local.yahoo.com/MapsService/V1/' +\
                   'geocode?appid=%s&location=%s' %
                   (yahookey, quote_plus(address))).read()
    print data
    doc = parseString(data)
    lat = doc.getElementsByTagName('Latitude')[0].firstChild.nodeValue
    lng = doc.getElementsByTagName('Longitude')[0].firstChild.nodeValue
    loc_cache[address] = (float(lat), float(lng))
    return loc_cache[address]

reader = csv.DictReader(open('items.csv'))
fieldnames = reader.fieldnames
fieldnames.extend(['Latitude', 'Longitude'])
writer = csv.DictWriter(open('geocoded_items.csv', 'wb'), fieldnames, quoting=csv.QUOTE_MINIMAL)
writer.writeheader()
for row in reader:
    if re.search('both|entire|rural', row['area'].lower()):
        address = row['district']
    else:
        address = row['area']
    address = address.split('/')[0] + ' New Zealand'
    (lat, lng) = getlocation(address);
    newrow = row.copy()
    newrow.update({ 'Latitude': lat, 'Longitude': lng })
    writer.writerow(newrow)
