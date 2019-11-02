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
        value = set_array(preset)

    elif value_type == 'string':
        value = set_string(preset)

    elif value_type == 'integer':
        value = set_integer(preset)

    elif value_type == 'float':
        value = set_float(preset)

    elif value_type == 'date':
        value = set_date(preset)

    elif value_type.startswith('uniqueid'):
        value = set_string(preset)
        if not value:
            value = None
        value = {value_type[9:]: value}

    json_call('%sLibrary.Set%sDetails' % (library, dbtype.capitalize()),
              params={'%s' % string: value, '%sid' % dbtype: int(dbid)},
              debug=True
              )

    if update_nfo and file:
        if dbtype == 'tvshow':
            write_nfo(os.path.join(file,'tvshow.nfo'), xml, value)
        else:
            write_nfo(file.replace(os.path.splitext(file)[1], '.nfo'), xml, value)

        if dbtype == 'movie':
            write_nfo(file.replace(os.path.basename(file), 'movie.nfo'), xml, value)


def write_nfo(path,xml,value):
    UpdateNFO(path,xml,value)


def set_array(preset):
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


def set_integer(preset):
    value = xbmcgui.Dialog().numeric(0, xbmc.getLocalizedString(16028), str(preset))

    if not value:
        return 0

    return int(value)


def set_float(preset):
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
            set_float(preset)

    return preset


def set_date(preset):
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

def set_string(preset):
    keyboard = xbmc.Keyboard(preset)
    keyboard.doModal()

    if keyboard.isConfirmed():
        value = keyboard.getText()
        return value

    return preset