#!/usr/bin/python
# coding: utf-8

########################

from resources.lib.helper import *
from resources.lib.json_map import *

########################

class Database(object):
    def __init__(self,dbid=None,dbtype=None,append=''):
        self.dbid = dbid
        self.append = append
        self.data = {}

        if dbtype:
            if dbtype in ['movie', 'tvshow', 'season', 'episode', 'musicvideo']:
                library = 'Video'
                self.data['nfo'] = True
            else:
                library = 'Audio'
                self.data['nfo'] = False

            self.set_details = '%sLibrary.Set%sDetails' % (library, dbtype)
            self.param = '%sid' % dbtype
            self.key_details = '%sdetails' % dbtype
            self.properties = eval('%s_properties' % dbtype)

    def result(self):
        return self.data

    def set(self,key,value):
        if not isinstance(key, list):
            key = [key]
            value = [value]

        for k in key:
            json_call(self.set_details,
                      params={'%s' % k: value[key.index(k)], self.param: int(self.dbid)},
                      debug=LOG_JSON
                      )

    def movies(self):
        movies = json_call('VideoLibrary.GetMovies',
                           properties=['title', 'year']
                           )

        self.data['movie'] = movies.get('result', {}).get('movies', [])

    def movie(self):
        tvshow = json_call('VideoLibrary.GetMovieDetails',
                           properties=movie_properties,
                           params={'movieid': int(self.dbid)}
                           )
        self.data['movie'] = [tvshow.get('result', {}).get('moviedetails')]

    def tvshows(self):
        tvshows = json_call('VideoLibrary.GetTVShows',
                            properties=['title', 'year']
                            )
        self.data['tvshow'] = tvshows.get('result', {}).get('tvshows', [])

    def tvshow(self):
        tvshow = json_call('VideoLibrary.GetTVShowDetails',
                           properties=tvshow_properties,
                           params={'tvshowid': int(self.dbid)}
                           )
        tvshow_details = tvshow.get('result', {}).get('tvshowdetails')
        self.data['tvshow'] = [tvshow_details]

        if tvshow_details:
            if 'episodes' in self.append:
                tvshowid = tvshow_details.get('tvshowid')
                episodes = json_call('VideoLibrary.GetEpisodes',
                                     properties=['title', 'showtitle'],
                                     params={'tvshowid': int(tvshowid)}
                                     )
                self.data['episode'] = episodes.get('result', {}).get('episodes', [])

    def episode(self):
        episode = json_call('VideoLibrary.GetEpisodeDetails',
                            properties=episode_properties,
                            params={'episodeid': int(self.dbid)}
                            )
        self.data['episode'] = [episode.get('result', {}).get('episodedetails')]

    def episodes(self):
        episodes = json_call('VideoLibrary.GetEpisodes',
                             properties=['title', 'showtitle']
                             )
        self.data['episode'] = episodes.get('result', {}).get('episodes', [])

    def musicvideo(self):
        musicvideo = json_call('VideoLibrary.GetMusicVideoDetails',
                           properties=musicvideo_properties
                           )
        self.data['musicvideo'] = [musicvideo.get('result', {}).get('muiscvideodetails')]

    def musicvideos(self):
        musicvideos = json_call('VideoLibrary.GetMusicVideos',
                           properties=['title', 'year']
                           )
        self.data['musicvideo'] = musicvideos.get('result', {}).get('musicvideos', [])

    def genre(self):
        movie = []
        tvshow = []
        musicvideo = []
        music = []
        video = []
        audio = []

        # video db
        for i in ['movie', 'tvshow', 'musicvideo']:
            genres = json_call('VideoLibrary.GetGenres',
                               properties=['title'],
                               params={'type': i}
                               )
            genres = genres.get('result', {}).get('genres', [])

            for genre in genres:
                eval(i).append(genre.get('label'))

        # audio db
        genres = json_call('AudioLibrary.GetGenres',
                           properties=['title']
                           )
        genres = genres.get('result', {}).get('genres', [])

        for genre in genres:
            music.append(genre.get('label'))

        self.data['moviegenres'] = movie
        self.data['tvshowgenres'] = tvshow
        self.data['musicvideogenres'] = musicvideo
        self.data['musicgenres'] = audio
        self.data['videogenres'] = list(set(movie + tvshow + musicvideo))
        self.data['audiogenres'] = list(set(music + musicvideo))

    def tags(self):
        tags = json_call('VideoLibrary.GetTags',
                         properties=['title']
                         )
        self.data['tags'] = tags.get('result', {}).get('tags', [])
