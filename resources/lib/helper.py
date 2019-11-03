#!/usr/bin/python
# coding: utf-8

########################

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import xbmcplugin
import json
import time
import datetime
import os
import sys
import hashlib
import xml.etree.ElementTree as ET

''' Python 2<->3 compatibility
'''
try:
    import urllib2 as urllib
except ImportError:
    import urllib.request as urllib

########################

PYTHON3 = True if sys.version_info.major == 3 else False

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_DATA_PATH = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % ADDON_ID))
ADDON_DATA_IMG_PATH = os.path.join(xbmc.translatePath("special://profile/addon_data/%s/img" % ADDON_ID))
ADDON_DATA_IMG_TEMP_PATH = os.path.join(xbmc.translatePath("special://profile/addon_data/%s/img/tmp" % ADDON_ID))

NOTICE = xbmc.LOGNOTICE
WARNING = xbmc.LOGWARNING
DEBUG = xbmc.LOGDEBUG
ERROR = xbmc.LOGERROR

DIALOG = xbmcgui.Dialog()

########################

def log(txt,loglevel=NOTICE,force=True):
    if loglevel in [DEBUG, WARNING, ERROR] or force:

        if not PYTHON3 and isinstance(txt, str):
            txt = txt.decode('utf-8')

        message = u'[ %s ] %s' % (ADDON_ID,txt)

        if not PYTHON3:
            xbmc.log(msg=message.encode('utf-8'), level=loglevel)
        else:
            xbmc.log(msg=message, level=loglevel)


def remove_quotes(label):
    if not label:
        return ''

    if label.startswith("'") and label.endswith("'") and len(label) > 2:
        label = label[1:-1]
        if label.startswith('"') and label.endswith('"') and len(label) > 2:
            label = label[1:-1]
        elif label.startswith('&quot;') and label.endswith('&quot;'):
            label = label[6:-6]

    return label


def get_joined_items(item):
    if len(item) > 0 and item is not None:
        item = '; '.join(item)
        item = item + ';'
    else:
        item = ''

    return item

def get_key_item(items,key):
    try:
        return items.get(key)
    except Exception:
        return

def get_rounded_value(item):
    item = float(item)
    item = round(item,1)

    return item

def get_date(date_time):
    date_time_obj = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    date_obj = date_time_obj.date()

    return date_obj

def remove_empty(array):
    for item in array:
        if not item:
            array.remove(item)

    return array

def execute(cmd):
    log('Execute: %s' % cmd, DEBUG)
    xbmc.executebuiltin(cmd)


def condition(condition):
    return xbmc.getCondVisibility(condition)


def encode_string(string):
    if not PYTHON3:
        string = string.encode('utf-8')
    return string

def decode_string(string):
    if not PYTHON3:
        string = string.decode('utf-8')
    return string


def url_quote(string):
    if not PYTHON3:
        string = string.encode('utf-8')
    return urllib.quote(string)


def url_unquote(string):
    return urllib.unquote(string)


def winprop(key, value=None, clear=False, window_id=10000):
    window = xbmcgui.Window(window_id)

    if clear:
        window.clearProperty(key.replace('.json', '').replace('.bool', ''))

    elif value is not None:

        if key.endswith('.json'):
            key = key.replace('.json', '')
            value = json.dumps(value)

        elif key.endswith('.bool'):
            key = key.replace('.bool', '')
            value = 'true' if value else 'false'

        window.setProperty(key, value)

    else:
        result = window.getProperty(key.replace('.json', '').replace('.bool', ''))

        if result:
            if key.endswith('.json'):
                result = json.loads(result)
            elif key.endswith('.bool'):
                result = result in ('true', '1')

        return result


def json_call(method,properties=None,sort=None,query_filter=None,limit=None,params=None,item=None,options=None,limits=None,debug=False):
    json_string = {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': {}}

    if properties is not None:
        json_string['params']['properties'] = properties

    if limit is not None:
        json_string['params']['limits'] = {'start': 0, 'end': int(limit)}

    if sort is not None:
        json_string['params']['sort'] = sort

    if query_filter is not None:
        json_string['params']['filter'] = query_filter

    if options is not None:
        json_string['params']['options'] = options

    if limits is not None:
        json_string['params']['limits'] = limits

    if item is not None:
        json_string['params']['item'] = item

    if params is not None:
        json_string['params'].update(params)

    jsonrpc_call = json.dumps(json_string)
    result = xbmc.executeJSONRPC(jsonrpc_call)

    if not PYTHON3:
        result = unicode(result, 'utf-8', errors='ignore')
    result = json.loads(result)

    if debug:
        log('--> JSON CALL: ' + json_prettyprint(json_string))
        log('--> JSON RESULT: ' + json_prettyprint(result))

    return result


def json_prettyprint(string):
    return json.dumps(string, sort_keys=True, indent=4, separators=(',', ': '))


def xml_prettyprint(root,level=0):
    i = '\n' + level * '    '

    if len(root):
        if not root.text or not root.text.strip():
            root.text = i + '    '

        if not root.tail or not root.tail.strip():
            root.tail = i

        for root in root:
            xml_prettyprint(root, level+1)

        if not root.tail or not root.tail.strip():
            root.tail = i

    else:
        if level and (not root.tail or not root.tail.strip()):
            root.tail = i