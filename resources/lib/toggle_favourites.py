#!/usr/bin/python
# coding: utf-8

########################

from resources.lib.helper import *
from resources.lib.utils import *

########################

class ToggleFav(object):
    def __init__(self,params):
        self.dbid = params.get('dbid')
        self.dbtype = params.get('type')

        self.method_details = 'VideoLibrary.Get%sDetails' % self.dbtype
        self.method_setdetails = 'VideoLibrary.Set%sDetails' % self.dbtype
        self.param = '%sid' % self.dbtype
        self.key_details = '%sdetails' % self.dbtype

        if self.dbtype == 'movie':
            self.tag = 'Fav. Kodi Movies'

        elif self.dbtype == 'tvshow':
            self.tag = 'Fav. Kodi TV Shows'

        elif self.dbtype == 'musicvideo':
            self.tag = 'Fav. Kodi Music Videos'

        self.init()

    def init(self):
        self.check_tag()
        self.update_info()

    def check_tag(self):
        result = json_call(self.method_details,
                               properties=['tag', 'file'],
                               params={self.param: int(self.dbid)}
                               )

        result = result['result'][self.key_details]

        self.tag_list = result.get('tag', [])
        self.is_fav = True if self.tag in self.tag_list else False
        self.file = result.get('file')

    def update_info(self):
        if not self.is_fav:
            isuserfavorite = 'true'
            self.tag_list.append(self.tag)
        else:
            isuserfavorite = 'false'
            self.tag_list.remove(self.tag)

        json_call(self.method_setdetails,
                  params={self.param: int(self.dbid), 'tag': self.tag_list}
                  )

        if self.file:
            write_nfo(file=self.file,
                      elem=['tag', 'isuserfavorite'],
                      value=[self.tag_list, isuserfavorite],
                      dbtype=self.dbtype)

        #reload_widgets(reason='Fav. updated')