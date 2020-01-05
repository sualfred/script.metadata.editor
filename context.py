#!/usr/bin/python
# coding: utf-8

#################################################################################################

import xbmc
import sys

from resources.lib.helper import *
from resources.lib.json_map import *
from resources.lib.editor import *
from resources.lib.rating_updater import *

#################################################################################################

class ContextMenu(object):
    def __init__(self,dbid,dbtype):
        self.dbid = dbid
        self.dbtype = dbtype

        db = Database(self.dbid, self.dbtype)
        getattr(db, self.dbtype)()
        self.details = db.result().get(self.dbtype)[0]

        self.menu()

    def menu(self):
        itemlist = [ADDON.getLocalizedString(32010)]

        if 'genre' in self.details and self.dbtype != 'song':
            itemlist.append(ADDON.getLocalizedString(32004))

        if 'tag' in self.details:
            itemlist.append(ADDON.getLocalizedString(32003))

            if 'Watchlist' in self.details.get('tag'):
                itemlist.append(ADDON.getLocalizedString(32008))
            else:
                itemlist.append(ADDON.getLocalizedString(32009))

        if self.dbtype in ['movie', 'tvshow', 'episode']:
            itemlist.append(ADDON.getLocalizedString(32039))

        if len(itemlist) > 1:
            contextdialog = DIALOG.contextmenu(itemlist)

            if contextdialog == 0:
                self._editor()

            elif contextdialog == 1 and self.dbtype == 'episode':
                self._ratings()

            elif contextdialog == 1:
                self._set(key='genre', valuetype='select')

            elif contextdialog == 2:
                self._set(key='tag', valuetype='select')

            elif contextdialog == 3:
                self._set(key='tag', valuetype='watchlist')

            elif contextdialog == 4:
                self._ratings()

        else:
            self._editor()

    def _set(self,key,valuetype):
        editor = EditDialog(dbid=self.dbid, dbtype=self.dbtype)
        editor.set(key=key, type=valuetype)

    def _editor(self):
        editor = EditDialog(dbid=self.dbid, dbtype=self.dbtype)
        editor.editor()

    def _ratings(self):
        update_ratings(dbid=self.dbid, dbtype=self.dbtype)


if __name__ == "__main__":
    listitem = sys.listitem.getVideoInfoTag()
    dbid = listitem.getDbId()
    dbtype = listitem.getMediaType()

    if not dbid or not dbtype:
        listitem = sys.listitem.getMusicInfoTag()
        dbid = listitem.getDbId()
        dbtype = listitem.getMediaType()

    ContextMenu(dbid, dbtype)