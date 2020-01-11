# script.metadata.editor

Kodi script to edit basic metadata information of library items with support to automatically update the .nfo file.

## Used scraper APIs
The script is using TMDb (free) and OMDb.

I already have included a TMDb API key (hardcoded).

For OMDb please visit https://omdbapi.com/ and create your own API key and add it to the addon settings.
Please note that the free available OMDb API key is limited to 1.000 calls a day. I highly recommend to become a patreon of the creator of OMDb.
For $1 a month your daily limit gets increased to 100.000 calls / day. Support it and benefit.


## Supported .nfo types

The updating of .nfo items is only possible for video library items, because the JSON result doesn't return any path for music entries.

Supported .nfo namings:

* %Filename%.nfo
* tvshow.nfo
* movie.nfo

## Creating of missing .nfo files

By default the script is creating a .nfo if missing. This can be disabled in the settings.


## MPAA and rating region handling

You can configure the preferred MPAA rating in the addon settings.
It's also possible to skip "not rated" or to enable/disable the fallback to US ratings


## Used scrapers

TMDb scraper (not used for episodes, because of different global airing dates and episode orders):
* Rating + votes
* MPAA
* Premiered year
* TV show status
* External unique IDs (IMDb, TVDb)

OMDb scraper:
* Rotten ratings (all four of them incl. votes)
* Metacritic (just rating, no votes available)
* IMDb (ID + rating + votes)

Note:
There is a experimental setting available to use title + year for the OMDb call, if the IMDb ID is not available. It's disabled by default, because there is a high chance for false positive returnings and wrong fetched metadata. I do not recommend to enable it.


## Additional features of the rating updater

The rating updater also updates MPAA, TV show status, missing uniqueid's (IMDb ID, TMDb ID, TVDb ID, etc.), missing original title


## Run the script / context menu

The script can be called with the context menu or RunScript() commands (useful for skinners).
A library updating task can be started by starting the addon itself.

Context menu entries:

* `Metadata Editor` / `Open Editor` = Editor dialog or sub menu if more options are available
* `Add/remove available genres` = Quickly edit the genres which the item belongs to
* `Add/remove available tags` = Quickly edit the tags which the item belongs to
* `Add/remove favourite tag` = Shortcut to toggle the library tag `Watchlist`. Can be used to create custom splitted favourite widgets.
* `Update ratings` = Will update ratings by using the OMDb and TMDb API


RunScript calls:

*  `RunScript(script.metadata.editor,dbid=$INFO[ListItem.DBID],type=$INFO[ListItem.DBType])` = opens editor
*  `RunScript(script.metadata.editor,action=setuserrating,dbid=$INFO[ListItem.DBID],type=$INFO[ListItem.DBType])` = sets user rating and updates the nfo if enabled
*  `RunScript(script.metadata.editor,action=setgenres,dbid=$INFO[ListItem.DBID],type=$INFO[ListItem.DBType])` = opens genre selector
*  `RunScript(script.metadata.editor,action=settags,dbid=$INFO[ListItem.DBID],type=$INFO[ListItem.DBType])` = opens tags selector
*  `RunScript(script.metadata.editor,action=togglewatchlist,dbid=$INFO[ListItem.DBID],type=$INFO[ListItem.DBType])` = toggle watchlist tag

RunScript calls for updating ratings:
*  `RunScript(script.metadata.editor)` = Shows select dialog to update movies, shows and episodes or all of them
*  `RunScript(script.metadata.editor,action=updaterating,dbid=$INFO[ListItem.DBID],type=$INFO[ListItem.DBType])` = Updates rating for the requested item
*  `RunScript(script.metadata.editor,action=updaterating,content=movies)` = Updates all ratings for movies (combination of available TMDb, TVDb, IMDb IDs)
*  `RunScript(script.metadata.editor,action=updaterating,content=tvshows)` = Updates all ratings for TV shows (combination of available TMDb, TVDb, IMDb IDs)
*  `RunScript(script.metadata.editor,action=updaterating,content=episodes)` = Updates all ratings for TV shows (only if IMDb is available)
*  `RunScript(script.metadata.editor,action=updaterating,content=movies+tvshows+episodes)` = Updates all ratings for provided content. Values are splitted by '+'