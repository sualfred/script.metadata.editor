#!/usr/bin/python
# coding: utf-8

########################

from resources.lib.helper import *
from resources.lib.nfo_updater import *

########################

def write_db(value_type,dbid,dbtype,string,preset,xml,details,file,update_nfo):
    preset = preset.replace('N/A','')

    if dbtype in ['song', 'album', 'artist']:
        library = 'Audio'
    else:
        library = 'Video'

    if value_type == 'array':
        value = write_array(preset)

    elif value_type == 'string':
        value = write_string(preset)

    elif value_type == 'integer':
        value = write_integer(preset)

    elif value_type == 'float':
        value = write_float(preset)

    elif value_type == 'date':
        value = write_date(preset)

    elif value_type.startswith('uniqueid'):
        value = write_string(preset)
        if not value:
            value = None
        value = {value_type[9:]: value}

    json_call('%sLibrary.Set%sDetails' % (library, dbtype.capitalize()),
              params={'%s' % string: value, '%sid' % dbtype: int(dbid)},
              debug=True
              )

    if update_nfo:
        UpdateNFO(file,xml,value)


def write_array(preset):
    keyboard = xbmc.Keyboard(preset)
    keyboard.doModal()

    if keyboard.isConfirmed():
        array = keyboard.getText()
    else:
        array = preset

    array = array.replace('; ',';').split(';')

    for item in array:
        if not item:
            array.remove(item)

    values = json.dumps(array)

    return eval(values)


def write_integer(preset):
    value = xbmcgui.Dialog().numeric(0, xbmc.getLocalizedString(16028), str(preset))

    if not value:
        return 0

    return int(value)


def write_float(preset):
    preset = float(preset)
    preset = round(preset,1)
    keyboard = xbmc.Keyboard(str(preset))
    keyboard.doModal()

    if keyboard.isConfirmed():
        try:
            value = float(keyboard.getText())
            value = round(value,1)
            return value

        except Exception:
            write_float(preset)

    return preset


def write_date(preset):
    try:
        conv = time.strptime(preset,'%Y-%m-%d')
        conv = time.strftime('%d/%m/%Y',conv)

    except Exception:
        conv = '01/01/1900'

    value = xbmcgui.Dialog().numeric(1, xbmc.getLocalizedString(16028), conv)

    if value:
        value = value.replace(' ','0')
        value = time.strptime(value,'%d/%m/%Y')
        value = time.strftime('%Y-%m-%d',value)
        return value

    else:
        return preset

def write_string(preset):
    keyboard = xbmc.Keyboard(preset)
    keyboard.doModal()

    if keyboard.isConfirmed():
        value = keyboard.getText()
        return value

    return preset