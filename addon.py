# -*- coding: utf-8 -*-
# Module: default
# Author: joen, bodems
# Created on: 24.08.2017
# License: MIT

from __future__ import print_function

import json
import operator
import routing
import sys
import urllib
from urllib import urlencode
import urllib2
import urlparse
from urlparse import parse_qsl
import cookielib
import xbmcgui
import xbmcplugin
import xbmcaddon

addon = xbmcaddon.Addon('plugin.video.streama')
streamaurl = addon.getSetting('url')
username = addon.getSetting('username')
password = addon.getSetting('password')

# Initialize the authentication
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
login_data = urllib.urlencode({'username' : username, 'password' : password, 'remember_me' : 'on'})
# Authenticate
opener.open(streamaurl + '/login/authenticate', login_data)

cookiestring = str(cj).split(" ")
sessionid = cookiestring[1].split("JSESSIONID=")
remember_me = cookiestring[5].split("streama_remember_me=")

VIDEOS = {'Shows': [],
            'Movies': [],
            'Generic Videos': [],
            'Genres': [],
            'New Releases': []}


# Get the list of Movies from Streama
# movies = opener.open(streamaurl + '/dash/listMovies.json')
# Put the list of movies into the category list
# VIDEOS['Movies'] = json.loads(movies.read())

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

# Initialize the authentication
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
login_data = urllib.urlencode({'username' : username, 'password' : password, 'remember_me' : 'on'})
# Authenticate
opener.open(streamaurl + '/login/authenticate', login_data)

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_categories():
    """
    Get the list of video categories.

    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or server.

    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :return: The list of video categories
    :rtype: list
    """
    # return the list of categories
    return VIDEOS.iterkeys()


def get_videos(category):
    """
    Get the list of videofiles/streams.

    Here you can insert some parsing code that retrieves
    the list of video streams in the given category from some site or server.

    .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :param category: Category name
    :type category: str
    :return: the list of videos in the category
    :rtype: list
    """

    if category == 'Shows':
        items = opener.open(streamaurl + '/dash/listShows.json')
        videolist = json.loads(items.read())
        return videolist
    elif category == 'Movies':
        items = opener.open(streamaurl + '/dash/listMovies.json')
        videolist = json.loads(items.read())
        return videolist
    elif category == 'Generic Videos':
        items = opener.open(streamaurl + '/dash/listGenericVideos.json')
        videolist = json.loads(items.read())
        return videolist
    elif category == 'Genres':
        items = opener.open(streamaurl + '/dash/listGenres.json')
        videolist = json.loads(items.read())
        return videolist
    elif category == 'New Releases':
        items = opener.open(streamaurl + '/dash/listNewReleases.json')
        videolist = json.loads(items.read())
        return videolist
    else:
        items = []
        videolist = json.loads(items.read())
        return videolist


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Get video categories
    categories = get_categories()
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        # list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
        #                  'icon': VIDEOS[category][0]['thumb'],
        #                  'fanart': VIDEOS[category][0]['thumb']})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # http://mirrors.xbmc.org/docs/python-docs/15.x-isengard/xbmcgui.html#ListItem-setInfo
        list_item.setInfo('video', {'title': category, 'genre': category})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    # Get the list of videos in the category.
    videos = get_videos(category)

    if category == 'Shows':
        for video in videos:
            list_item = xbmcgui.ListItem(label=video['name'])
            list_item.setArt({'thumb': 'https://image.tmdb.org/t/p/w500//' + video['poster_path'], 'icon': 'https://image.tmdb.org/t/p/w500//' + video['poster_path']})
            id = video['id']
            url = get_url(action='play', video=id)
            is_folder = True
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    elif category == 'Movies':
        # Iterate through videos.
        for video in videos:
            # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=video['title'])
            # Set additional info for the list item.
            list_item.setInfo('video', {'title': video['title'], 'genre': 'Test'})
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            # Here we use the same image for all items for simplicity's sake.
            # In a real-life plugin you need to set each image accordingly.
            list_item.setArt({'thumb': 'https://image.tmdb.org/t/p/w500//' + video['poster_path'], 'icon': 'https://image.tmdb.org/t/p/w500//' + video['poster_path'], 'fanart': 'https://image.tmdb.org/t/p/w1280//' + video['backdrop_path']})
            # Set 'IsPlayable' property to 'true'.
            # This is mandatory for playable items!
            list_item.setProperty('IsPlayable', 'true')
            # Create a URL for a plugin recursive call.
            # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
            # videosrc = 'https://upload.wikimedia.org/wikipedia/commons/transcoded/c/c0/Big_Buck_Bunny_4K.webm/Big_Buck_Bunny_4K.webm.720p.webm'
            #movie = opener.open(streamaurl + '/video/show.json?id=' + str(video['id']))
            #movie_json = json.loads(movie.read())
            #videosrc = movie_json['files'][0]['src'])
            id = video['id']

        
            url = get_url(action='play', video=id)
        
            # Add the list item to a virtual Kodi folder.
            # is_folder = False means that this item won't open any sub-list.
            is_folder = False
            # Add our item to the Kodi virtual folder listing.
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    elif category == 'Generic Videos':
        for video in videos:
            # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=video['title'])
            # Set additional info for the list item.
            list_item.setInfo('video', {'title': video['title'], 'genre': 'Test'})
            #list_item.setArt({'thumb': 'https://image.tmdb.org/t/p/w500//' + video['poster_path'], 'icon': 'https://image.tmdb.org/t/p/w500//' + video['poster_path'], 'fanart': 'https://image.tmdb.org/t/p/w1280//' + video['backdrop_path']})
            list_item.setProperty('IsPlayable', 'true')
            id = video['id']

            url = get_url(action='play', video=id)
            is_folder = False
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    elif category == 'Genres':
        for video in videos:
            list_item = xbmcgui.ListItem(label=video['name'])
            id = video['id']
            url = get_url(action='play', video=id)
            is_folder = True
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    elif category == 'New Releases':
        for video in videos:
            try:
                list_item = xbmcgui.ListItem(label=video['movie']['title'])
                id = video['movie']['id']
                is_folder = False
            except:
                foo = 23
            try:
                list_item =xbmcgui.ListItem(label=video['tvShow']['name'])
                id = video['tvShow']['id']
                is_folder = True
            except:
                foo = 42
            list_item.setProperty('IsPlayable', 'true')
            url = get_url(action='play', video=id)
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def play_video(id):
    """
    Play a video by the provided id.

    :param id: Streama video id
    :type id: int
    """
    # Get the JSON for the corresponding video from Streama
    movie = opener.open(streamaurl + '/video/show.json?id=' + id)
    # Create the path from resulting info
    movie_json = json.loads(movie.read())
    path = movie_json['files'][0]['src']

    # if path contains streamaurl, append sessionid-cookie and remember_me-cookie for auth
    if path.find(streamaurl) != -1:
        path = path + '|Cookie=JSESSIONID%3D' + sessionid[1] + '%3Bstreama_remember_me%3D' + remember_me[1] + '%3B'
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
