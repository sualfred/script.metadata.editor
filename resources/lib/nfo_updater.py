#!/usr/bin/python
# coding: utf-8

########################

from resources.lib.helper import *

########################

class UpdateNFO():
    def __init__(self,file,elem,value):
        self.elems = elem
        self.values = value
        self.targetfile = file

        self.init()

    def init(self):
        if xbmcvfs.exists(self.targetfile):
            self.root = self.read_file()

            if len(self.root):
                if isinstance(self.elems, list):
                    for elem in self.elems:
                        self.elem = elem
                        self.value = self.values[self.elems.index(elem)]
                        self.update_elem()

                else:
                    self.elem = self.elems
                    self.value = self.values
                    self.update_elem()

                self.write_file()

    def update_elem(self):
        if self.elem == 'uniqueid':
            self.add_uniqueid()
        else:
            self.add_elem()

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
        for elem in self.root.findall(self.elem):
            self.root.remove(elem)

        if isinstance(self.value, list):
            for item in self.value:
                elem = ET.SubElement(self.root, self.elem)
                elem.text = item

        else:
            elem = ET.SubElement(self.root, self.elem)
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
            elem = ET.SubElement(self.root, self.elem)
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