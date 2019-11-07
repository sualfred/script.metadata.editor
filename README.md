# script.metadata.editor

Kodi script to edit basic metadata information of library items with support to automatically update the .nfo file.


## Supported .nfo types

The updating of .nfo items is only possible for video library items, because the JSON result doesn't return any path for music entries.

Supported .nfo namings:

* %Filename%.nfo
* tvshow.nfo
* movie.nfo


## Run the script / context menu

The script can be called with the context menu or RunScript() commands (useful for skinners).

Context menu entries:

* `Metadata Editor` / `Open Editor` = Editor dialog or sub menu if more options are available
* `Add/remove available genres` = Quickly edit the genres which the item belongs to
* `Add/remove available tags` = Quickly edit the tags which the item belongs to
* `Add/remove favourite tag` = Shortcut to toggle the library tags `Movie Watchlist`, `TV Show Watchlist` and `Music Video Watchlist`. Can be used to create custom splitted favourite widgets (like a watchlist).


RunScript calls:

*  `RunScript(script.metadata.editor,dbid=$INFO[ListItem.DBID],type=$INFO[ListItem.DBType])` = opens editor
*  `RunScript(script.metadata.editor,action=setgenres,dbid=$INFO[ListItem.DBID],type=$INFO[ListItem.DBType])` = opens genre selector
*  `RunScript(script.metadata.editor,action=settags,dbid=$INFO[ListItem.DBID],type=$INFO[ListItem.DBType])` = opens tags selector
*  `RunScript(script.metadata.editor,action=togglefav,dbid=$INFO[ListItem.DBID],type=$INFO[ListItem.DBType])` = toggle fav. tag