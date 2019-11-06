#!/usr/bin/python
# coding: utf-8

########################

from resources.lib.helper import *
from resources.lib.nfo_updater import *

########################

def update_library(dbtype,key,value,dbid):
    if dbtype in ['song', 'album', 'artist']:
        library = 'Audio'
    else:
        library = 'Video'

    if isinstance(key, list):
        for item in key:
            json_call('%sLibrary.Set%sDetails' % (library, dbtype),
                      params={'%s' % item: value[key.index(item)], '%sid' % dbtype: int(dbid)},
                      debug=True
                      )

    else:
        json_call('%sLibrary.Set%sDetails' % (library, dbtype),
                  params={'%s' % key: value, '%sid' % dbtype: int(dbid)},
                  debug=True
                  )


def update_nfo(file,elem,value,dbtype):
    if not ADDON.getSettingBool('nfo_updating'):
        return

    if dbtype == 'tvshow':
        path = os.path.join(file,'tvshow.nfo')
    else:
        path = file.replace(os.path.splitext(file)[1], '.nfo')

    UpdateNFO(path, elem, value, dbtype)

    # support for additional movie.nfo
    if dbtype == 'movie':
        path = file.replace(os.path.basename(file), 'movie.nfo')
        UpdateNFO(path, elem, value, dbtype)


def set_ratings(ratings):
    providerlist = []
    #ratings = json.dumps(ratings)
    ratings = {str(k):(str(v) if isinstance(v, unicode) else v) for k,v in ratings.items()}
    log('old ratings ' + str(ratings))
    for item in ratings:
        providerlist.append(str(item))

    menu = DIALOG.select(xbmc.getLocalizedString(424), [ADDON.getLocalizedString(32015), ADDON.getLocalizedString(32016), ADDON.getLocalizedString(32017)])

    if menu == 0: # set default provider
        providerdefault = DIALOG.select(ADDON.getLocalizedString(32014), providerlist)

        if providerdefault >= 0:
            name = providerlist[providerdefault]

            for item in ratings:
                default = True if item == name else False
                ratings[item] = {'default': default,
                                 'rating': ratings[item].get('rating'),
                                 'votes': ratings[item].get('votes')}

    elif menu == 1: # edit votes/rating
        providerdefault = DIALOG.select(ADDON.getLocalizedString(32012), providerlist)

        if providerdefault >= 0:
            name = providerlist[providerdefault]
            cur_rating = round(ratings[name].get('rating', 0.0), 1)
            cur_votes = ratings[name].get('votes', 0)

            rating = set_float(cur_rating)
            votes = set_integer(cur_votes)

            if not rating:
                rating = 0.0

            if not votes:
                votes = 0

            ratings[name] = {'default': ratings[name].get('default'),
                             'rating': rating,
                             'votes': votes}

    elif menu == 2: # add new rating provider
        supportedlist = ['imdb', 'themoviedb', 'tomatometerallcritics', 'tomatometeravgcritics', 'tomatometerallaudience', 'tomatometeravgaudience', 'metacritic']

        for item in supportedlist:
            if item in providerlist:
                supportedlist.remove(item)

        newprovider = DIALOG.select(ADDON.getLocalizedString(32013), supportedlist)

        if newprovider >= 0:
            name = supportedlist[newprovider]
            rating = set_float(heading='Enter rating (floating number - min 0.1 / max 10.0)')

            if not rating or float(rating) > 10:
                DIALOG.ok(xbmc.getLocalizedString(257), ADDON.getLocalizedString(32018))

            else:
                votes = set_integer()
                if not votes:
                    votes = 0

                if not DIALOG.yesno(ADDON.getLocalizedString(32019), ADDON.getLocalizedString(32020)):
                    default = False
                else:
                    default = True

                    for item in ratings:
                        ratings[item] = {'default': False,
                                         'rating': ratings[item].get('rating'),
                                         'votes': ratings[item].get('votes')}

                ratings[name] = {'default': default,
                                 'rating': rating,
                                 'votes': votes}

    return ratings


def set_array(preset,dbid,dbtype,key):
    actionlist = [ADDON.getLocalizedString(32005), ADDON.getLocalizedString(32006)]

    if key in ['genre', 'tag']:
        actionlist.append(ADDON.getLocalizedString(32007))

    array_action = DIALOG.select(xbmc.getLocalizedString(14241), actionlist)

    if array_action == 0:
        array = preset.replace('; ',';').split(';')

        keyboard = xbmc.Keyboard()
        keyboard.doModal()

        if keyboard.isConfirmed():
            new_item = keyboard.getText()

            if new_item not in array:
                array.append(new_item)

        return remove_empty(array)

    elif array_action == 1:
        keyboard = xbmc.Keyboard(preset)
        keyboard.doModal()

        if keyboard.isConfirmed():
            array = keyboard.getText()
        else:
            array = preset

        array = array.replace('; ',';').split(';')
        return remove_empty(array)

    elif array_action == 2:
        from resources.lib.dialog_selectvalue import SelectValue

        array = SelectValue(params={'dbid': dbid, 'type': dbtype, 'key': key},
                            editor=True)

        return eval(str(array))

    else:
        array = preset.replace('; ',';').split(';')
        return remove_empty(array)


def set_integer(preset=''):
    preset = str(preset)
    if preset == '0':
        preset = ''

    value = xbmcgui.Dialog().numeric(0, xbmc.getLocalizedString(16028), preset)

    if not value:
        return None

    return int(value)


def set_float(preset='',heading=ADDON.getLocalizedString(32011)):
    try:
        preset = float(preset)
        preset = round(preset,1)

    except Exception:
        preset = ''

    keyboard = xbmc.Keyboard(str(preset))
    keyboard.setHeading(heading)
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

    return preset


def set_time(preset):
    value = xbmcgui.Dialog().numeric(2, xbmc.getLocalizedString(16028), preset)

    if value:
        return value

    return preset


def set_string(preset):
    keyboard = xbmc.Keyboard(preset)
    keyboard.doModal()

    if keyboard.isConfirmed():
        value = keyboard.getText()
        return value

    return preset


def set_integer_range(preset, maximum):
    preset = int(preset) if preset else 0
    rangelist = []

    for i in range(0, maximum):
        rangelist.append(str(i))

    value = DIALOG.select(xbmc.getLocalizedString(424), rangelist, preselect=preset)

    if value >= 0:
        return value

    return preset


def set_status(preset):
    statuslist = ['Continuing', 'Ended']

    if preset == ADDON.getLocalizedString(32022):
        preset = ''

    value = DIALOG.select(xbmc.getLocalizedString(126), statuslist)

    if value >= 0:
        return statuslist[value]

    return preset