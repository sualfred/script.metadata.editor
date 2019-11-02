#!/usr/bin/python
# coding: utf-8

#################################################################################################

import xbmc
import sys

from resources.lib.dialog import *

#################################################################################################

class Context(object):
    def __init__(self):
        listitem = sys.listitem.getVideoInfoTag()
        self.dbid = listitem.getDbId()
        self.dbtype = listitem.getMediaType()
        EditDialog({'dbid': self.dbid, 'type': self.dbtype})

if __name__ == "__main__":
    Context()