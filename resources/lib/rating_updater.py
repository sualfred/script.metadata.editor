#!/usr/bin/python
# coding: utf-8

########################

from __future__ import division

from resources.lib.helper import *
from resources.lib.functions import *

########################

class UpdateAllRatings(object):
    def __init__(self,params):
        self.dbtype = params.get('type')

        all_items = json_call('VideoLibrary.Get%ss' % self.dbtype,
                              properties=['title', 'year']
                              )

        try:
        	self.items = all_items['result']['%ss' % self.dbtype]
        	self.total_items = len(self.items)
        	self.run()

        except Exception:
        	pass

    def run(self):
        winprop('UpdatingRatings.bool', True)

        if self.dbtype == 'movie':
            heading = ADDON.getLocalizedString(32033)
        else:
            heading = ADDON.getLocalizedString(32034)

        processed_items = 0
        progress = 0
        percentage = self.total_items / 100

        progressdialog = xbmcgui.DialogProgress()
        progressdialog.create(heading, '')

        for item in self.items:
            if progressdialog.iscanceled():
                break

            label = item.get('title')
            if item.get('year'):
                label = label + ' (' + str(item.get('year')) + ')'

            progressdialog.update(int(progress), label, str(processed_items) + ' / ' + str(self.total_items))

            UpdateRating({'dbid': item.get('%sid' % self.dbtype),
                          'type': self.dbtype,
                          'done_msg': False})

            processed_items += 1

            if processed_items > percentage:
                progress = progress + 1
                percentage = percentage + percentage

        progressdialog.close

        winprop('UpdatingRatings', clear=True)


class UpdateRating(object):
    def __init__(self,params):
        self.dbid = params.get('dbid')
        self.dbtype = params.get('type')
        self.done_msg = True if params.get('done_msg', True) else False
        self.tmdb_type = 'movie' if self.dbtype == 'movie' else 'tv'
        self.tmdb_tv_status = None
        self.update_uniqueid = False

        self.method_details = 'VideoLibrary.Get%sDetails' % self.dbtype
        self.method_setdetails = 'VideoLibrary.Set%sDetails' % self.dbtype
        self.param = '%sid' % self.dbtype
        self.key_details = '%sdetails' % self.dbtype

        self.init()

    def init(self):
        # get stored IDs that are used to call TMDb and OMDb
        self.get_details()

        if not self.uniqueid:
            return

        self.imdb = self.uniqueid.get('imdb')
        self.tmdb = self.uniqueid.get('tmdb')
        self.tvdb = self.uniqueid.get('tvdb')

        # get the default used rating
        self.default_rating = None
        for rating in self.ratings:
            if self.ratings[rating].get('default'):
                self.default_rating = rating
                break

        # get TMDb ID (if not available) by using the ID of IMDb or TVDb
        if not self.tmdb and self.imdb:
            self.get_tmdb_externalid(self.imdb)

        elif not self.tmdb and self.tvdb:
            self.get_tmdb_externalid(self.tvdb)

        # get TMDb rating and IMDb number if not available
        if self.tmdb:
            self.get_tmdb()

        # get Rotten, Metacritic and IMDb ratings of OMDb
        self.get_omdb()

        # update db + nfo
        self.update_info()

        if self.done_msg:
            DIALOG.notification(ADDON.getLocalizedString(32030), xbmc.getLocalizedString(19256), icon='special://home/addons/script.metadata.editor/resources/icon.png')

    def get_details(self):
        json_query = json_call(self.method_details,
                               properties=['title', 'originaltitle', 'year', 'uniqueid', 'ratings', 'file', 'tag'],
                               params={self.param: int(self.dbid)}
                               )
        try:
            self.uniqueid = json_query['result'][self.key_details].get('uniqueid')
            self.ratings = json_query['result'][self.key_details].get('ratings')
            self.file = json_query['result'][self.key_details].get('file')
            self.year = json_query['result'][self.key_details].get('year')
            self.title = json_query['result'][self.key_details].get('title')
            self.original_title = json_query['result'][self.key_details].get('originaltitle') or self.title
            self.tags = json_query['result'][self.key_details].get('tag')

        except KeyError:
            self.uniqueid = None
            self.ratings = None
            self.file = None
            self.year = None
            self.title = None
            self.original_title = None
            self.tags = None

    def get_tmdb(self):
        result = tmdb_call(action=self.tmdb_type,
                           call=str(self.tmdb),
                           )

        # set IMDb ID if not available in the library
        if not self.imdb:
            self.imdb = result.get('imdb_id')

            if self.imdb:
                self._update_uniqueid_dict('imdb', self.imdb)

        self.tmdb_rating = result.get('vote_average')
        self.tmdb_votes = result.get('vote_count')
        self.original_title = result.get('original_name')

        if self.tmdb_type == 'tv':
            year = result.get('first_air_date')
            self.tmdb_tv_status = result.get('status')

            # update TV status as well
            if self.tmdb_tv_status:
                self._set_value('status', self.tmdb_tv_status)

        else:
            year = result.get('release_date')

        self.year = year[:4] if year else ''

        if self.tmdb_rating:
            self._update_ratings_dict(key='themoviedb', rating=self.tmdb_rating, votes=self.tmdb_votes)

    def get_tmdb_externalid(self,external_id):
        result = tmdb_call(action='find',
                           call=str(external_id),
                           params={'external_source': 'imdb_id' if external_id.startswith('tt') else 'tvdb_id'}
                           )

        try:
            if self.dbtype == 'movie':
                self.tmdb = result['movie_results'][0].get('id')

            elif self.dbtype == 'tvshow':
                self.tmdb = result['tv_results'][0].get('id')

            if self.tmdb:
                self._update_uniqueid_dict('tmdb', self.tmdb)

        except Exception:
            pass

    def get_omdb(self):
        omdb = omdb_call(imdbnumber=self.imdb,
                         title=self.original_title,
                         year=self.year)

        if not omdb:
            return

        tree = ET.ElementTree(ET.fromstring(omdb))
        root = tree.getroot()

        for child in root:
            # imdb ratings
            imdb_rating = child.get('imdbRating')
            imdb_votes = child.get('imdbVotes', 0)

            if imdb_rating and imdb_rating != 'N/A':
                votes = imdb_votes.replace(',', '') if imdb_votes != 'N/A' else 0
                self._update_ratings_dict(key='imdb',
                                          rating=float(imdb_rating),
                                          votes=int(votes)
                                          )

                # Emby For Kodi is storing the rating as 'default'
                if 'default' in self.ratings:
                    self._update_ratings_dict(key='default',
                                              rating=float(imdb_rating),
                                              votes=int(votes)
                                              )

            # regular rotten rating
            tomatometerallcritics = child.get('tomatoMeter')
            tomatometerallcritics_votes = child.get('tomatoReviews', 0)

            if tomatometerallcritics and tomatometerallcritics != 'N/A':
                tomatometerallcritics = int(tomatometerallcritics) / 10
                votes = tomatometerallcritics_votes if tomatometerallcritics_votes != 'N/A' else 0
                self._update_ratings_dict(key='tomatometerallcritics',
                                          rating=tomatometerallcritics,
                                          votes=int(votes))

            # user rotten rating
            tomatometeravgcritics = child.get('tomatoUserMeter')
            tomatometeravgcritics_votes = child.get('tomatoUserReviews', 0)

            if tomatometeravgcritics and tomatometeravgcritics != 'N/A':
                tomatometeravgcritics = int(tomatometeravgcritics) / 10
                votes = tomatometeravgcritics_votes if tomatometeravgcritics_votes != 'N/A' else 0
                self._update_ratings_dict(key='tomatometeravgcritics',
                                          rating=tomatometeravgcritics,
                                          votes=int(votes))

            # metacritic
            metacritic = child.get('metascore')

            if metacritic and metacritic != 'N/A':
                metacritic = int(metacritic) / 10
                self._update_ratings_dict(key='metacritic',
                                          rating=metacritic,
                                          votes=0)

            # TMDb doesn't store IMDb numbers for shows so store the one found via OMDb
            if not self.imdb and child.get('imdbID') and child.get('imdbID') != 'N/A':
                self.imdb = child.get('imdbID')
                self._update_uniqueid_dict('imdb', child.get('imdbID'))

            break


    def update_info(self):
        json_call('VideoLibrary.Set%sDetails' % self.dbtype,
                  params={'ratings': self.ratings, '%sid' % self.dbtype: int(self.dbid)},
                  debug=LOG_JSON
                  )

        if self.update_uniqueid:
            json_call('VideoLibrary.Set%sDetails' % self.dbtype,
                      params={'uniqueid': self.uniqueid, '%sid' % self.dbtype: int(self.dbid)},
                      debug=LOG_JSON
                      )

        if self.file:
            elems = ['ratings', 'uniqueid']
            values = [self.ratings, [self.uniqueid, None]]

            if self.tmdb_tv_status:
                elems.append('status')
                values.append(self.tmdb_tv_status)

            # write tags to nfo in case they weren't there to trigger Emby to add them
            if self.tags:
                elems.append('tag')
                values.append(self.tags)

            update_nfo(file=self.file,
                       elem=elems,
                       value=values,
                       dbtype=self.dbtype,
                       dbid=self.dbid)

    def _update_ratings_dict(self,key,rating,votes):
        self.ratings[key] = {'default': True if key == self.default_rating else False,
                             'rating': rating,
                             'votes': votes}

    def _update_uniqueid_dict(self,key,value):
        self.uniqueid[key] = str(value)
        self.update_uniqueid = True

    def _set_value(self,key,value):
        json_call('VideoLibrary.Set%sDetails' % self.dbtype,
                  params={key: value, '%sid' % self.dbtype: int(self.dbid)},
                  debug=LOG_JSON
                  )