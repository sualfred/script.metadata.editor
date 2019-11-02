#!/usr/bin/python
# coding: utf-8

########################

from resources.lib.helper import *

########################

class UpdateNFO():
    def __init__(self,file,xml,value):
        self.xml = xml
        self.value = value
        self.targetfile = file

        if xbmcvfs.exists(self.targetfile):
            self.root = self.read_file()

            if self.root:
                if xml == 'uniqueid':
                    self.add_uniqueid()
                else:
                    self.add_elem()

                self.write_file()

    def read_file(self):
        file = xbmcvfs.File(self.targetfile)
        cur_buf = []
        content = ''

        while True:
            buf = file.read(1024)
            cur_buf.append(buf)
            if not buf:
                content = ''.join(cur_buf)
                break

        file.close()

        if content:
            tree = ET.ElementTree(ET.fromstring(content))
            root = tree.getroot()
            return root

    def write_file(self):
        xml_prettyprint(self.root)
        content = ET.tostring(self.root, encoding='UTF-8')

        file = xbmcvfs.File(self.targetfile, 'w')
        file.write(content)
        file.close()

    def add_elem(self):
        for elem in self.root.findall(self.xml):
            self.root.remove(elem)

        if isinstance(self.value, list):
            for item in self.value:
                elem = ET.SubElement(self.root, self.xml)
                elem.text = item

        else:
            elem = ET.SubElement(self.root, self.xml)
            elem.text = str(self.value)

    def add_uniqueid(self):
        for item in self.value:
            id_type = item
            value = self.value.get(id_type)

        # <uniqueid> fields
        for elem in self.root.findall('uniqueid'):
            if elem.get('type') == id_type:
                self.root.remove(elem)

        if value:
            elem = ET.SubElement(self.root, self.xml)
            elem.set('type', id_type)
            elem.text = value
            if id_type == 'imdb':
                elem.set('default', 'true')

        # <imdbid>, <tmdbid>, etc.
        elem_name = id_type + 'id'

        for elem in self.root.findall(elem_name):
            self.root.remove(elem)

        if value:
            elem = ET.SubElement(self.root, elem_name)
            elem.text = value