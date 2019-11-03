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

        if self.dbtype in ['movie', 'tvshow', 'season', 'episode', 'musicvideo']:
            self.library = 'Video'
            self.nfo_support = True
        else:
            self.library = 'Audio'
            self.nfo_support = False

        self.method_details = '%sLibrary.Get%sDetails' % (self.library, self.dbtype)
        self.method_setdetails = '%sLibrary.Set%sDetails' % (self.library, self.dbtype)
        self.param = '%sid' % self.dbtype
        self.key_details = '%sdetails' % self.dbtype
        self.dbkey_details = '%ss' % self.dbkey

        self.all_values = []
        self.duplicate_handler = []

        self.init()

    def init(self):
        if self.dbkey == 'genre':
            if self.dbtype in ['movie', 'tvshow', 'season', 'episode']:
                self.available_video_values()
            else:
                self.available_audio_values()

        else:
            if self.dbtype in ['movie', 'tvshow', 'season', 'episode', 'musicvideo']:
                self.available_video_values()
            else:
                self.available_audio_values()

        self.current_values()
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

        # also show musicvideo values if not listed for audio returns
        if self.dbtype == 'musicvideo' and self.dbkey == 'genre':
            for item in self.values:
                if item not in self.all_values:
                    self.all_values.append(item)

    def available_video_values(self):
        self._json_query(type='movie')
        self._json_query(type='tvshow')

        if self.dbkey != 'genre':
            self._json_query(type='musicvideo')

    def available_audio_values(self):
        self._json_query(library='Audio')

        if self.dbkey == 'genre':
            self._json_query(library='Video', type='musicvideo')

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

        if self.nfo_support and self.file:
            write_nfo(self.file, self.dbkey, self.modified, self.dbtype)

    def _json_query(self,library=None,type=None):
        if library is None:
            library = self.library

        if type is not None:
            params = {'type': type}
        else:
            params = None

        result = json_call('%sLibrary.Get%ss' % (library, self.dbkey),
                           properties=['title'],
                           params=params
                           )

        try:
            for item in result['result'][self.dbkey_details]:
                label = item['label']
                if label not in self.duplicate_handler:
                    self.all_values.append(label)
                    self.duplicate_handler.append(label)

        except KeyError:
            pass