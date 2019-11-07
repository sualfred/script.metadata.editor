#!/usr/bin/python

########################

from resources.lib.helper import *
from resources.lib.dialog_metadata import *
from resources.lib.dialog_selectvalue import *
from resources.lib.toggle_favourites import *

########################

class Main:
    def __init__(self):
        self.action = False
        self._parse_argv()
        dbid = self.params.get('dbid')
        dbtype = self.params.get('type')

        if not dbid or not dbtype:
            DIALOG.ok(xbmc.getLocalizedString(257), ADDON.getLocalizedString(32024))

        elif self.action == 'togglefav':
            ToggleFav({'dbid': dbid, 'type': dbtype})

        elif self.action == 'setgenre':
            SelectValue({'dbid': dbid, 'type': dbtype, 'key': 'genre'})

        elif self.action == 'settags':
            SelectValue({'dbid': dbid, 'type': dbtype, 'key': 'tag'})

        else:
            EditDialog(self.params)

    def _parse_argv(self):
        args = sys.argv

        for arg in args:
            if arg == ADDON_ID:
                continue
            if arg.startswith('action='):
                self.action = arg[7:].lower()
            else:
                try:
                    self.params[arg.split("=")[0].lower()] = "=".join(arg.split("=")[1:]).strip()
                except:
                    self.params = {}

if __name__ == '__main__':
    Main()
