#!/usr/bin/python
# coding: utf-8

########################

from resources.lib.helper import *

########################

class UpdateNFO():
    def __init__(self,file,elem,value,dbtype):
        ''' Key conversion/cleanup if nfo element has a different naming.
            If Emby is using different elements, key + value will be
            converted to a list to cover both.
        '''
        if elem == 'plotoutline':
            elem = 'outline'

        elif elem == 'writer':
            elem = ['writer', 'credits']
            value = [value, value]

        elif elem == 'firstaired':
            elem = 'aired'

        elif isinstance(elem, list) and len(elem) > 1 and elem[0] == 'uniqueid':
            # remove unrequired <imdbnumber> field
            del elem[1]
            del value[1]

        self.elems = elem
        self.values = value
        self.targetfile = file
        self.dbtype = dbtype

        self.run()

    def run(self):
        with busy_dialog():
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
        if self.elem == 'ratings':
            self.handle_ratings()

        elif self.elem == 'uniqueid':
            self.handle_uniqueid()

        else:
            self.handle_elem()

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

    def handle_elem(self):
        for elem in self.root.findall(self.elem):
            self.root.remove(elem)

        if isinstance(self.value, list):
            for item in self.value:
                elem = ET.SubElement(self.root, self.elem)
                if item:
                    elem.text = item

        else:
            elem = ET.SubElement(self.root, self.elem)
            if self.value:
                elem.text = str(self.value)

    def handle_ratings(self):
        for elem in self.root.findall('ratings'):
            self.root.remove(elem)

        elem = ET.SubElement(self.root, 'ratings')

        for item in self.values:
            rating = str(round(self.values[item].get('rating', 0.0), 1))
            votes = str(self.values[item].get('votes', 0))

            subelem = ET.SubElement(elem, 'rating')
            subelem.set('name', item)
            subelem.set('max', '10')

            if self.values[item].get('default'):
                subelem.set('default', 'true')

                # <votes>, <rating>
                for key in ['rating', 'votes']:
                    for defaultelem in self.root.findall(key):
                        self.root.remove(defaultelem)

                    defaultelem = ET.SubElement(self.root, key)
                    defaultelem.text = eval(key)

            else:
                subelem.set('default', 'false')

            rating_elem = ET.SubElement(subelem, 'value')
            rating_elem.text = rating

            votes_elem = ET.SubElement(subelem, 'votes')
            votes_elem.text = votes

            # Emby <criticrating> Rotten ratings
            if item == 'tomatometerallcritics':
                normalized_rating = int(float(rating) * 10)
                if normalized_rating > 100:
                    normalized_rating = ''

                for emby_elem in self.root.findall('criticrating'):
                    self.root.remove(emby_elem)

                emby_rotten = ET.SubElement(self.root, 'criticrating')
                emby_rotten.text = str(normalized_rating)

    def handle_uniqueid(self):
        for item in self.value:
            id_type = item
            value = self.value.get(id_type)

        # <uniqueid> fields
        old_default = None
        for default in self.root.findall('uniqueid'):
            if default.get('default'):
                old_default = default.get('type')
                break

        for elem in self.root.findall('uniqueid'):
            if elem.get('type') == id_type:
                self.root.remove(elem)

        if value:
            elem = ET.SubElement(self.root, self.elem)
            elem.set('type', id_type)
            elem.text = value

            ''' If no default is defined in nfo, we wil have to set one.
                If replaced element was the default before, set the default
                tag again.
            '''
            if old_default == id_type:
                elem.set('default', 'true')

            elif old_default is None:
                if id_type in ['imdb', 'tmdb'] and self.dbtype == 'movie':
                    elem.set('default', 'true')

                elif id_type in ['tvdb', 'tmdb'] and self.dbtype == 'tvshow':
                    elem.set('default', 'true')

        # Emby <imdbid>, <tmdbid>, etc.
        elem_name = id_type + 'id'

        for elem in self.root.findall(elem_name):
            self.root.remove(elem)

        if value:
            elem = ET.SubElement(self.root, elem_name)
            elem.text = value

    def write_file(self):
        xml_prettyprint(self.root)
        content = ET.tostring(self.root, encoding='UTF-8')

        file = xbmcvfs.File(self.targetfile, 'w')
        file.write(content)
        file.close()