#!/usr/bin/python
# coding: utf-8

########################

from resources.lib.helper import *
from resources.lib.utils import *

########################

class SelectValue(object):
    def __init__(self,params):
        self.dbid = params.get('dbid')
        self.dbtype = params.get('type')
        self.dbkey = params.get('key')

        self.method_details = 'VideoLibrary.Get%sDetails' % self.dbtype
        self.method_setdetails = 'VideoLibrary.Set%sDetails' % self.dbtype
        self.param = '%sid' % self.dbtype
        self.key_details = '%sdetails' % self.dbtype
        self.dbkey_details = '%ss' % self.dbkey

        self.init()

    def init(self):
        self.current_values()
        self.available_values()
        self.select_dialog()
        self.update_data()

    def current_values(self):
        result = json_call(self.method_details,
                           properties=[self.dbkey, 'file'],
                           params={self.param: int(self.dbid)}
                           )

        result = result['result'][self.key_details]

        self.values = result.get(self.dbkey, [])
        self.file = result.get('file')

    def available_values(self):
        self.all_values = []
        duplicate_handler = []

        movies = json_call('VideoLibrary.Get%ss' % self.dbkey,
                           properties=['title'],
                           params={'type': 'movie'}
                           )

        tvshows = json_call('VideoLibrary.Get%ss' % self.dbkey,
                            properties=['title'],
                            params={'type': 'tvshow'}
                            )

        try:
            for item in movies['result'][self.dbkey_details]:
                label = item['label']
                self.all_values.append(label)
                duplicate_handler.append(label)

        except KeyError:
            pass

        try:
            for item in tvshows['result'][self.dbkey_details]:
                label = item['label']
                if label not in duplicate_handler:
                    self.all_values.append(label)
                    duplicate_handler.append(label)

        except KeyError:
            pass

    def select_dialog(self):
        preselectlist = []
        self.modified = []

        self.values.sort()
        self.all_values.sort()

        for item in self.values:
            preselectlist.append(self.all_values.index(item))

        selectdialog = DIALOG.multiselect(ADDON.getLocalizedString(32002), self.all_values, preselect=preselectlist)

        if selectdialog == -1 or not selectdialog:
            self.modified = []
        else:
            for index in selectdialog:
                self.modified.append(self.all_values[index])

    def update_data(self):
        json_call(self.method_setdetails,
                  params={self.param: int(self.dbid), self.dbkey: self.modified}
                  )

        if self.file:
            write_nfo(self.file, self.dbkey, self.modified, self.dbtype)