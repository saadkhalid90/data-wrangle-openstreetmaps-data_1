## importing relevant packages
import re
import xml.etree.ElementTree as ET
import os
import pickle

## defining the path of the .osm file
filepath = os.path.abspath("C:/Users/Saad Khalid/Downloads/islamabad_pakistan.osm")
'''
The following fuction takes an osm file and a keytype (e.g "phone", "addr:postcode", "addr:street" etc) and returns a set
containing unique values associated to that keytype in the file.
'''
def audit_by_type(osmfile,typevar):
    osm_file = open(osmfile, "r")
    values = []
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == 'way':
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == typevar:
                    values.append(tag.attrib['v'])

    return set(values)

def print_postcodes(osmfile):
    post_codes = audit_by_type(osmfile, "addr:postcode")
    post_codes = set(post_codes)
    for post_code in post_codes:
        print post_code

def print_phones(osmfile):
    phones = audit_by_type(osmfile, "phone")
    phones = set(phones)
    for phone in phones:
        print phone

def print_street_addresses(osmfile):
    street_addresses = audit_by_type(osmfile, "addr:street")
    street_addresses = set(street_addresses)
    for street_address in street_addresses:
        print street_address
