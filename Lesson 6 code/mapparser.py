#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Your task is to use the iterative parsing to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data you can expect to have in the map.
The output should be a dictionary with the tag name as the key
and number of times this tag can be encountered in the map as value.

Note that your code will be tested with a different data file than the 'example.osm'
"""
import xml.etree.ElementTree as ET
import pprint

def count_tags(filename):
    # YOUR CODE HERE
    root = ET.parse(filename).getroot()
    TAGSDIC = counting_tags(root, {}, set())
    return TAGSDIC

def counting_tags(root,tag_count,tags):
    if root.tag == ET.parse('example.osm').getroot().tag:
        tag_count[root.tag] = 1
    for child in root.getchildren():
        ##print child.tag
        if child.tag in tags:
            tag_count[child.tag] += 1
        else:
            tag_count[child.tag] = 1
        tags.add(child.tag)

        ##print tags
        if child.getchildren() != []:
            counting_tags(child,tag_count,tags)
    return tag_count

def test():

    tags = count_tags('example.osm')
    pprint.pprint(tags)
    assert tags == {'bounds': 1,
                     'member': 3,
                     'nd': 4,
                     'node': 20,
                     'osm': 1,
                     'relation': 1,
                     'tag': 7,
                     'way': 1}



if __name__ == "__main__":
    test()
