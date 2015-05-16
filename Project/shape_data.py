import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json
"""
The shape_element function in this file is taken form the exercises of lesson 6

The structure of the ducument for reference
{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}
"""


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

## The following fuction shapes the element of the osm file into a dictionary based on the document structure given above. This has been taken dirsctly from
## the lesson 6 exercise

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        node['created'] = {}
        addr_counter = 0
        ref_counter = 0

        if 'lat' in element.keys():
            node['pos'] = [float(element.attrib['lat']), float(element.attrib['lon'])]

        node['type'] = element.tag

        for key in element.keys():
            if key in ['version', 'changeset', 'timestamp', 'user', 'uid']:
                node['created'][key] = element.attrib[key]
            if key in ["visible", "id"]:
                node[key] = element.attrib[key]

        for tag in element.iter("tag"):
            if re.search("^addr:",tag.attrib['k']):
                if re.match("^addr:.+:.+$", tag.attrib['k']):
                    continue

                if addr_counter == 0:
                    addr_counter += 1
                    node['address'] = {}
                node['address'][re.sub("^addr:","",tag.attrib['k'])] = tag.attrib['v']
            else:
                node[tag.attrib['k']] = tag.attrib['v']

        for nd in element.iter("nd"):
            if ref_counter == 0:
                ref = []
                ref_counter += 1
            ## ____debudding code____
            ## print nd.attrib['ref']
            ## print ref_counter
            ## print ref
            ref.append(nd.attrib['ref'])
            node['node_refs'] = ref

        return node
    else:
        return None



'''
The following functions standardizes the phone numbers to this format '(country code)-(city code)-(phone number)'
'''

def std_phone_no(phone):
    ## removing all alphabetical characters
    phone = re.sub('[ A-Za-z\-]',"",phone)
    ## separating multiple phone numbers by a white space
    phone = re.sub('[,/]', " ", phone)
    ## Replacing all variations of country code by '+92-')
    phone = re.sub('^\+92', "+92-", phone)
    phone = re.sub('^0{0,2}92', "+92-", phone)
    phone = re.sub("^0","+92-",phone)
    ## adding islamabad city code after checking if city code is missing
    if len(phone) == 7 or re.search('^11[0-9]{7}', phone):
        phone = "+92-51"+phone
    ## adding country code after checking if phone number starts with islamabad city code
    if re.match('^51',phone):
        phone = "+92-" + phone

    ## defining RE's for variations of city codes and mobile phone codes
    mobile = re.compile('^\+92-3[0-9]{2}')
    islamabad_attock = re.compile('^\+92-5[17]')
    jhelum = re.compile('^\+92-544')
    abbotabad = re.compile('^\+92-992')

    area_codes = [mobile, islamabad_attock, jhelum, abbotabad]

    ## seperating the number from city code by a '-'
    for area_code in area_codes:
        if re.search(area_code, phone):
            repl = re.search(area_code, phone).group() + "-"
            phone = re.sub(area_code, repl, phone)

    ## turning phone numbers field into an array if there are multiple phone numbers separated by whitespace
    ## and reapplying the function to every element of an array
    if re.search(" ", phone):
        new_phone = []
        phone = str.split(phone)
        for i in phone:
            new_phone.append(std_phone_no(i))
        phone = new_phone

    return phone


## The following function cleans and removes inconsistencies from the street addresses and phone no.s
def clean_element(element):
    if type(element) is dict:
        if "address" in element.keys():
            if "street" in element['address'].keys():
                ## Replacing all variations of road with 'Road'
                street_add = element["address"]["street"]
                if re.search(' [Rr](.){0,2}[Dd](\.)?', street_add):
                    element["address"]["street"] = re.sub('[Rr](.){0,2}[Dd](\.)*$', "Road", street_add)
                ## Standardizing the way streets are represented (Street followed by number)
                if re.search('(?<=[Ss]treet)(.*)(?=[0-9])', street_add):
                    street_useless_chars = re.sub('[0-9]+',"",re.search('(?<=[Ss]treet)(.*)(?=[0-9]+)', street_add).group())
                    element["address"]["street"] = str.strip(re.sub("[Ss]treet", "Street", re.sub(street_useless_chars, " ", street_add)))
                ## Standardizing the sectors of Islamabad (sample format F-6/3)
                if re.search('(?<=[D-I])([ -/]){0,1}(?=[0-9])', street_add):
                    sector_sep = re.search('(?<=[D-I])([ -/]){0,1}(?=[0-9])', street_add).group()
                    element["address"]["street"] = re.sub('(?<=[D-I])([ -/]){0,1}(?=[0-9])', "-", street_add)
                ## Adding String 'Street' before any number
                if re.match('^[0-9]{1,3}[A-Z]?.*$', street_add):
                    street_no = re.match('^[0-9]{1,3}[A-Z]?.*$', street_add).group()
                    element["address"]["street"] = "Street " + street_no
                ## removing parenthesis
                element["address"]["street"] = re.sub('[)()]',"",element["address"]["street"])

            """
            Getting sector name from full address and adding it to street address if street address doesn't contain it
            """
            if "street" in element['address'].keys() and "full" in element['address'].keys():
                full_add = element["address"]["full"]
                street_add = element["address"]["street"]
                if re.search('[D-I]-[1-9]/[1-4]?', full_add) and not(re.search('[D-I]-[1-9]/[1-4]?', street_add)):
                    element["address"]["street"] = street_add + ", " + re.search('[D-I]-[1-9]/[1-4]?', full_add).group()

        ## fixing phone numbers
        if "phone" in element.keys():
            element['phone'] = std_phone_no(element['phone'])
    return element


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            el = clean_element(el)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data
