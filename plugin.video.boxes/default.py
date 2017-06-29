# -*- coding: utf-8 -*-
#------------------------------------------------------------
# XBMC Add-on for RuYa IPTV
# Version 1.1.2
#------------------------------------------------------------

import os
import sys
import urlparse
import plugintools
import api
import re

SKIN_VIEW_FOR_MOVIES="500"
SKIN_VIEW_FOR_TVSHOWS="500"
SKIN_VIEW_FOR_EPISODES="512"
SKIN_VIEW_FOR_LIVETV="512"

THUMBNAIL_PATH = os.path.join( plugintools.get_runtime_path() , "resources" , "img" )
MAX_ITEMS_PER_PAGE = 10
plugintools.module_log_enabled = (plugintools.get_setting("debug")=="true")
plugintools.http_debug_log_enabled = (plugintools.get_setting("debug")=="true")

# Entry point
def run():
    plugintools.log("boxes.run")
    
    # Get params
    params = plugintools.get_params()
    
    if params.get("action") is None:
        main_list(params)
    else:
        action = params.get("action")
        exec action+"(params)"

    plugintools.close_item_list()

# Main menu
def main_list(params):
    plugintools.log("boxes.main_list "+repr(params))

    if plugintools.get_setting("username")=="":
        settings(params)

    token = api.login( plugintools.get_setting("server") , plugintools.get_setting("username") , plugintools.get_setting("password") )

    if token!="":
        plugintools.set_setting("token",token)
        import os
        plugintools.add_item( action="movies",   title="[COLOR ff05f1ff]Movies[/COLOR]" , thumbnail = "http://www.boxes.com.mt/addonsrc/movies_thumb.jpg" , fanart="http://www.boxes.com.mt/addonsrc/movies_art.jpg" , folder=True )
        plugintools.add_item( action="tvshows",  title="[COLOR ff05f1ff]TV Shows[/COLOR]" , thumbnail = "http://www.boxes.com.mt/addonsrc/tvshows_thumb.jpg" , fanart="http://www.boxes.com.mt/addonsrc/tvshows_art.jpg" , folder=True )
        plugintools.add_item( action="livetv",   title="[COLOR ff05f1ff]Live TV[/COLOR]" , thumbnail = "http://www.boxes.com.mt/addonsrc/live_thumb.jpg" , fanart="http://www.boxes.com.mt/addonsrc/live_art.jpg" , folder=True )
    else:
        plugintools.message("BOXES","Invalid login, check your account in add-on settings")

    import os
    plugintools.add_item( action="settings", title="[COLOR ff05f1ff]Settings[/COLOR]" , thumbnail = "http://www.boxes.com.mt/addonsrc/settings_thumb.jpg" , fanart="http://www.boxes.com.mt/addonsrc/settings_art.jpg" , folder=False )

    if plugintools.get_setting("force_advancedsettings")=="true":
        # Ruta del advancedsettings
        import xbmc,xbmcgui,os
        advancedsettings = xbmc.translatePath("special://userdata/advancedsettings.xml")

        if not os.path.exists(advancedsettings):
            # Copia el advancedsettings.xml desde el directorio resources al userdata
            fichero = open( os.path.join(plugintools.get_runtime_path(),"resources","advancedsettings.xml") )
            texto = fichero.read()
            fichero.close()
            
            fichero = open(advancedsettings,"w")
            fichero.write(texto)
            fichero.close()

            plugintools.message("plugin", "A new file userdata/advancedsettings.xml","has been created for optimal streaming")

    if token!="" and plugintools.get_setting("check_for_updates")=="true":
        import updater
        updater.check_for_updates()

    plugintools.set_view( plugintools.LIST )

# Settings dialog
def settings(params):
    plugintools.log("boxes.settings "+repr(params))

    if plugintools.get_setting("pincode")!="":
        text = plugintools.keyboard_input(default_text="", title="Enter PIN Code")

        if text==plugintools.get_setting("pincode"):
            plugintools.open_settings_dialog()

    else:
        plugintools.open_settings_dialog()

# Movies
def movies(params):
    plugintools.log("boxes.movies "+repr(params))

    plugintools.add_item( action="movies_latest_releases", title="[COLOR ff05f1ff]Latest releases[/COLOR]" , thumbnail = os.path.join(THUMBNAIL_PATH,"hot.png") , fanart="http://www.boxes.com.mt/addonsrc/art0.jpg" , folder=True )
    plugintools.add_item( action="movies_recent", title="[COLOR ff05f1ff]Recent[/COLOR]" , thumbnail = os.path.join(THUMBNAIL_PATH,"recent.png") , fanart="http://www.boxes.com.mt/addonsrc/art0.jpg" , folder=True )
    plugintools.add_item( action="movies_az",     title="[COLOR ff05f1ff]A-Z[/COLOR]" , thumbnail = os.path.join(THUMBNAIL_PATH,"letter.png") , fanart="http://www.boxes.com.mt/addonsrc/art0.jpg" , folder=True )
    plugintools.add_item( action="movies_genres", title="[COLOR ff05f1ff]Genres[/COLOR]" , thumbnail = os.path.join(THUMBNAIL_PATH,"genres.png") , fanart="http://www.boxes.com.mt/addonsrc/art0.jpg" , folder=True )
    plugintools.add_item( action="movies_search", title="[COLOR ff05f1ff]Search[/COLOR]" , thumbnail = os.path.join(THUMBNAIL_PATH,"genres.png") , fanart="http://www.boxes.com.mt/addonsrc/art0.jpg" , folder=True )

    plugintools.set_view( plugintools.LIST )

def movies_search(params):
    plugintools.log("boxes.movies_search "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    current_page , next_page = get_current_and_next_page(params.get("page"))

    if params.get("url")=="":
        terms = plugintools.keyboard_input(default_text="", title="Enter search terms")
    else:
        terms = params.get("url")

    items = api.movie_search(token,terms=terms,num_page=current_page)
    for item in items:
        if item["title"].endswith("(3D)"):
            item["title"] = item["title"].replace("(3D)","[COLOR red](3D)[/COLOR]")
        plugintools.add_item( action="play_movie", title=item["title"] , url=item["url"] , plot=item["plot"], thumbnail=item["thumbnail"], fanart=item["fanart"], isPlayable=True, folder=False )

    if len(items)>=MAX_ITEMS_PER_PAGE:
        plugintools.add_item( action="movies_search", title=">> Next page" , url=terms, page=next_page, fanart="http://www.boxes.com.mt/addonsrc/art0.jpg" , folder=True )

    plugintools.set_view( plugintools.MOVIES )
    #import xbmcplugin
    #xbmcplugin.setContent( int(sys.argv[1]) ,"Movies" )
    #xbmc.executebuiltin("Container.SetViewMode("+SKIN_VIEW_FOR_MOVIES+")") # Wall

def movies_latest_releases(params):
    plugintools.log("boxes.movies_latest_releases "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    current_page , next_page = get_current_and_next_page(params.get("page"))

    items = api.get_latest_releases(token,num_page=current_page)
    for item in items:
        if item["title"].endswith("(3D)"):
            item["title"] = item["title"].replace("(3D)","[COLOR red](3D)[/COLOR]")
        plugintools.add_item( action="play_movie", title=item["title"] , url=item["url"] , plot=item["plot"], thumbnail=item["thumbnail"], fanart=item["fanart"], isPlayable=True, folder=False )

    if len(items)>=MAX_ITEMS_PER_PAGE:
        plugintools.add_item( action="movies_latest_releases", title=">> Next page" , page=next_page, fanart="http://www.boxes.com.mt/addonsrc/art0.jpg" , folder=True )

    #import xbmcplugin
    #xbmcplugin.setContent( int(sys.argv[1]) ,"Movies" )
    #xbmc.executebuiltin("Container.SetViewMode("+SKIN_VIEW_FOR_MOVIES+")") # Wall
    plugintools.set_view( plugintools.MOVIES )

def movies_recent(params):
    plugintools.log("boxes.movies_recent "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    current_page , next_page = get_current_and_next_page(params.get("page"))

    items = api.get_recent_movies(token,num_page=current_page)
    for item in items:
        if item["title"].endswith("(3D)"):
            item["title"] = item["title"].replace("(3D)","[COLOR red](3D)[/COLOR]")
        plugintools.add_item( action="play_movie", title=item["title"] , url=item["url"] , plot=item["plot"], thumbnail=item["thumbnail"], fanart=item["fanart"], isPlayable=True, folder=False )

    if len(items)>=MAX_ITEMS_PER_PAGE:
        plugintools.add_item( action="movies_recent", title=">> Next page" , page=next_page, fanart="http://www.boxes.com.mt/addonsrc/art0.jpg" , folder=True )

    #import xbmcplugin
    #xbmcplugin.setContent( int(sys.argv[1]) ,"Movies" )
    #xbmc.executebuiltin("Container.SetViewMode("+SKIN_VIEW_FOR_MOVIES+")") # Wall
    plugintools.set_view( plugintools.MOVIES )

def movies_az(params):
    plugintools.log("boxes.movies_az "+repr(params))

    for letra in ['0-9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']:
        plugintools.add_item( action="movies_by_letter", title=letra, url=letra, fanart="http://www.boxes.com.mt/addonsrc/art0.jpg" , folder=True )

    plugintools.set_view( plugintools.LIST )

def movies_by_letter(params):
    plugintools.log("boxes.movies_az "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    current_page , next_page = get_current_and_next_page(params.get("page"))

    letter = params.get("url")

    items = api.get_movies_by_letter(token,letter,num_page=current_page)
    for item in items:
        if item["title"].endswith("(3D)"):
            item["title"] = item["title"].replace("(3D)","[COLOR red](3D)[/COLOR]")
        plugintools.add_item( action="play_movie", title=item["title"] , url=item["url"] , plot=item["plot"], thumbnail=item["thumbnail"], fanart=item["fanart"], isPlayable=True, folder=False )

    if len(items)>=MAX_ITEMS_PER_PAGE:
        plugintools.add_item( action="movies_by_letter", title=">> Next page" , url=letter , page=next_page, fanart="http://www.boxes.com.mt/addonsrc/art0.jpg" , folder=True )

    plugintools.set_view( plugintools.MOVIES )

def movies_genres(params):
    plugintools.log("boxes.movies_az "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    items = api.get_movie_genres(token)
    for item in items:
        plugintools.add_item( action="movies_by_genre", title=item["title"] , url=item["title"], fanart="http://www.boxes.com.mt/addonsrc/art0.jpg" , folder=True )

    plugintools.set_view( plugintools.LIST )

def movies_by_genre(params):
    plugintools.log("boxes.movies_az "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    current_page , next_page = get_current_and_next_page(params.get("page"))

    genre = params.get("url")

    items = api.get_movies_by_genre(token,genre,num_page=current_page)
    for item in items:
        if item["title"].endswith("(3D)"):
            item["title"] = item["title"].replace("(3D)","[COLOR red](3D)[/COLOR]")
        plugintools.add_item( action="play_movie", title=item["title"] , url=item["url"] , plot=item["plot"], thumbnail=item["thumbnail"], fanart=item["fanart"], isPlayable=True, folder=False )

    if len(items)>=MAX_ITEMS_PER_PAGE:
        plugintools.add_item( action="movies_by_genre", title=">> Next page" , url=genre , page=next_page, fanart="http://www.boxes.com.mt/addonsrc/art0.jpg" , folder=True )

    plugintools.set_view( plugintools.MOVIES )

# TV Shows
def tvshows(params):
    plugintools.log("boxes.tvshows "+repr(params))

    plugintools.add_item( action="tvshows_recent_episodes", title="[COLOR ff05f1ff]Latest episodes[/COLOR]" , thumbnail = os.path.join(THUMBNAIL_PATH,"recent.png") , fanart="http://www.boxes.com.mt/addonsrc/art1.jpg" , folder=True )
    plugintools.add_item( action="tvshows_updated",         title="[COLOR ff05f1ff]Updated TV Shows[/COLOR]" , thumbnail = os.path.join(THUMBNAIL_PATH,"updated.png") , fanart="http://www.boxes.com.mt/addonsrc/art1.jpg" , folder=True )
    plugintools.add_item( action="tvshows_az",              title="[COLOR ff05f1ff]A-Z[/COLOR]" , thumbnail = os.path.join(THUMBNAIL_PATH,"letter.png") , fanart="http://www.boxes.com.mt/addonsrc/art1.jpg" , folder=True )
    plugintools.add_item( action="tvshows_genres",          title="[COLOR ff05f1ff]Genres[/COLOR]" , thumbnail = os.path.join(THUMBNAIL_PATH,"genres.png") , fanart="http://www.boxes.com.mt/addonsrc/art1.jpg" , folder=True )
    plugintools.add_item( action="tvshows_search",          title="[COLOR ff05f1ff]Search[/COLOR]" , thumbnail = os.path.join(THUMBNAIL_PATH,"genres.png") , fanart="http://www.boxes.com.mt/addonsrc/art1.jpg" , folder=True )

    plugintools.set_view( plugintools.LIST )

def tvshows_search(params):
    plugintools.log("boxes.tvshows_search "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    current_page , next_page = get_current_and_next_page(params.get("page"))

    if params.get("url")=="":
        terms = plugintools.keyboard_input(default_text="", title="Enter search terms")
    else:
        terms = params.get("url")

    items = api.tvshow_search(token,terms,num_page=current_page)
    for item in items:
        plugintools.add_item( action="tvshow_seasons", title=item["title"] , url=item["title"] , plot=item["plot"], thumbnail=item["thumbnail"], fanart=item["fanart"], folder=True )

    if len(items)>=MAX_ITEMS_PER_PAGE:
        plugintools.add_item( action="tvshows_search", title=">> Next page" , url=terms , page=next_page, fanart="http://www.boxes.com.mt/addonsrc/art1.jpg" , folder=True )

    plugintools.set_view( plugintools.TV_SHOWS )

def tvshows_recent_episodes(params):
    plugintools.log("boxes.tvshows_recent_episodes "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    current_page , next_page = get_current_and_next_page(params.get("page"))

    items = api.get_recent_episodes(token,num_page=current_page)
    for item in items:
        plugintools.add_item( action="play_episode", title=item["title"] , url=item["url"] , plot=item["plot"], thumbnail=item["thumbnail"], fanart="http://www.boxes.com.mt/addonsrc/art1.jpg" , isPlayable=True, folder=False )

    if len(items)>=MAX_ITEMS_PER_PAGE:
        plugintools.add_item( action="tvshows_recent_episodes", title=">> Next page" , page=next_page, fanart="http://www.boxes.com.mt/addonsrc/art1.jpg" , folder=True )

    plugintools.set_view( plugintools.EPISODES )

def tvshows_updated(params):
    plugintools.log("boxes.tvshows_updated "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    current_page , next_page = get_current_and_next_page(params.get("page"))

    items = api.get_updated_tvshows(token,num_page=current_page)
    for item in items:
        plugintools.add_item( action="tvshow_seasons", title=item["title"] , url=item["title"] , plot=item["plot"], thumbnail=item["thumbnail"], fanart=item["fanart"], folder=True )

    if len(items)>=MAX_ITEMS_PER_PAGE:
        plugintools.add_item( action="tvshows_updated", title=">> Next page" , page=next_page, fanart="http://www.boxes.com.mt/addonsrc/art1.jpg" , folder=True )

    plugintools.set_view( plugintools.TV_SHOWS )

def tvshows_az(params):
    plugintools.log("boxes.tvshows_az "+repr(params))

    for letra in ['0-9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']:
        plugintools.add_item( action="tvshows_by_letter", title=letra, url=letra, fanart="http://www.boxes.com.mt/addonsrc/art1.jpg" , folder=True )

    plugintools.set_view( plugintools.LIST )

def tvshows_by_letter(params):
    plugintools.log("boxes.tvshows_by_letter "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    current_page , next_page = get_current_and_next_page(params.get("page"))

    letter = params.get("url")

    items = api.get_tvshows_by_letter(token,letter,num_page=current_page)
    for item in items:
        plugintools.add_item( action="tvshow_seasons", title=item["title"] , url=item["title"] , plot=item["plot"], thumbnail=item["thumbnail"], fanart=item["fanart"], folder=True )

    if len(items)>=MAX_ITEMS_PER_PAGE:
        plugintools.add_item( action="tvshows_by_letter", title=">> Next page" , url=letter , page=next_page, fanart="http://www.boxes.com.mt/addonsrc/art1.jpg" , folder=True )

    plugintools.set_view( plugintools.TV_SHOWS )

def tvshows_genres(params):
    plugintools.log("boxes.tvshows_genres "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    items = api.get_tvshow_genres(token)
    for item in items:
        plugintools.add_item( action="tvshows_by_genre", title=item["title"] , url=item["title"], fanart="http://www.boxes.com.mt/addonsrc/art1.jpg" , folder=True )

    plugintools.set_view( plugintools.LIST )

def tvshows_by_genre(params):
    plugintools.log("boxes.tvshows_by_genre "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    current_page , next_page = get_current_and_next_page(params.get("page"))

    genre = params.get("url")

    items = api.get_tvshows_by_genre(token,genre,num_page=current_page)
    for item in items:
        plugintools.add_item( action="tvshow_seasons", title=item["title"] , url=item["title"] , plot=item["plot"], thumbnail=item["thumbnail"], fanart=item["fanart"], folder=True )

    if len(items)>=MAX_ITEMS_PER_PAGE:
        plugintools.add_item( action="tvshows_by_genre", title=">> Next page" , url=genre , page=next_page, fanart="http://www.boxes.com.mt/addonsrc/art1.jpg" , folder=True )

    plugintools.set_view( plugintools.TV_SHOWS )

def tvshow_seasons(params):
    plugintools.log("boxes.tvshow_episodes "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    items = api.get_tvshow_seasons(token,params.get("url"))
    for item in items:
        plugintools.add_item( action="tvshow_episodes", title=item["title"] , url=item["title"] , plot=item["plot"], thumbnail=item["thumbnail"], fanart=item["fanart"], extra=params.get("title"), folder=True )

    plugintools.set_view( plugintools.SEASONS )

def tvshow_episodes(params):
    plugintools.log("boxes.tvshow_episodes "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    tvshow = params.get("extra")
    season = params.get("url")
    items = api.get_tvshow_episodes(token,tvshow,season)
    for item in items:
        plugintools.add_item( action="play_episode", title=item["title"] , url=item["url"] , plot=item["plot"], thumbnail=item["thumbnail"], fanart=item["fanart"], isPlayable=True, folder=False )

    plugintools.set_view( plugintools.EPISODES )

# Live TV
def livetv(params):
    plugintools.log("boxes.livetv "+repr(params))

    plugintools.add_item( action="livetv_all", title="[COLOR ff05f1ff]All Channels[/COLOR]" , thumbnail = "http://www.boxes.com.mt/addonsrc/all_channels_thumb.jpg" , fanart="http://www.boxes.com.mt/addonsrc/art2.jpg" , folder=True )
    plugintools.add_item( action="livetv_packages", title="[COLOR ff05f1ff]Packages[/COLOR]" , thumbnail = "http://www.boxes.com.mt/addonsrc/packages_thumb.jpg" , fanart="http://www.boxes.com.mt/addonsrc/art2.jpg" , folder=True )
    plugintools.add_item( action="livetv_genres", title="[COLOR ff05f1ff]Categories[/COLOR]" , thumbnail = "http://www.boxes.com.mt/addonsrc/categories_thumb.jpg" , fanart="http://www.boxes.com.mt/addonsrc/art2.jpg" , folder=True )

    plugintools.set_view( plugintools.LIST )

def format_title(title):
    partes = title.split(" (Now")
    if len(partes)==2:
        new_title = "  [COLOR ff05f1ff]"+partes[0]+"[/COLOR]"+" (Now"+partes[1]
    else:
        if title.strip().startswith("---"):
            new_title = "[COLOR ff05f1ff]"+re.compile("[\-]+",re.DOTALL).sub("",title).strip()+"[/COLOR]"
        else:
            new_title = "  [COLOR ff05f1ff]"+title+"[/COLOR]"

    return new_title

def livetv_all(params):
    plugintools.log("boxes.livetv_all "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    items = api.get_all_livetv_channels(token)
    for item in items:
        if is_adult_content(item):
            if plugintools.get_setting("show_adult")=="true":
                plugintools.add_item( action="play_livetv", title=format_title(item["title"]) , url=item["url"] , thumbnail=item["thumbnail"], plot=item["plot"], fanart="http://www.boxes.com.mt/addonsrc/art2.jpg" , extra=item["fanart"], isPlayable=True, folder=False )
        else:
            plugintools.add_item( action="play_livetv", title=format_title(item["title"]) , url=item["url"] , thumbnail=item["thumbnail"], plot=item["plot"], fanart="http://www.boxes.com.mt/addonsrc/art2.jpg" , extra=item["fanart"], isPlayable=True, folder=False )

    plugintools.set_view( plugintools.EPISODES )

def livetv_genres(params):
    plugintools.log("boxes.livetv_genres "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    items = api.get_livetv_genres(token)
    for item in items:
        if is_adult_content(item):
            if plugintools.get_setting("show_adult")=="true":
                plugintools.add_item( action="livetv_by_genre", title=item["title"] , url=item["title"], fanart="http://www.boxes.com.mt/addonsrc/art2.jpg" , folder=True )
        else:
            plugintools.add_item( action="livetv_by_genre", title=item["title"] , url=item["title"], fanart="http://www.boxes.com.mt/addonsrc/art2.jpg" , folder=True )

    plugintools.set_view( plugintools.LIST )

def is_adult_content(item):
    return item["title"].lower()=="adult" or item["title"].lower()=="xxx" or item["title"].replace("-","").strip().lower()=="adult"

def livetv_packages(params):
    plugintools.log("boxes.livetv_packages "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    items = api.get_livetv_packages(token)
    for item in items:

        if is_adult_content(item):
            if plugintools.get_setting("show_adult")=="true":
                plugintools.add_item( action="livetv_by_package", title=item["title"] , url=item["title"], thumbnail=api.get_base_url()+"img/package/"+item["title"]+".png", fanart="http://www.boxes.com.mt/addonsrc/art2.jpg" , folder=True )
        else:
            plugintools.add_item( action="livetv_by_package", title=item["title"] , url=item["title"], thumbnail=api.get_base_url()+"img/package/"+item["title"]+".png", fanart="http://www.boxes.com.mt/addonsrc/art2.jpg" , folder=True )

    plugintools.set_view( plugintools.LIST )

def livetv_by_genre(params):
    plugintools.log("boxes.livetv_by_genre "+repr(params))

    if is_adult_content({"title":params.get("title")}):
        if plugintools.get_setting("pincode_adult")!="":
            text = plugintools.keyboard_input(default_text="", title="Enter PIN Code")

            if text!=plugintools.get_setting("pincode_adult"):
                return

    token = plugintools.get_setting("token")
    if token=="":
        return

    genre = params.get("url")

    items = api.get_livetv_channels_by_genre(token,genre)
    for item in items:
        plugintools.add_item( action="play_livetv", title=format_title(item["title"]).strip() , url=item["url"] , thumbnail=item["thumbnail"], plot=item["plot"], fanart="http://www.boxes.com.mt/addonsrc/art2.jpg" , isPlayable=True, folder=False )

    plugintools.set_view( plugintools.EPISODES )

def livetv_by_package(params):
    plugintools.log("boxes.livetv_by_package "+repr(params))

    if is_adult_content({"title":params.get("title")}):
        if plugintools.get_setting("pincode_adult")!="":
            text = plugintools.keyboard_input(default_text="", title="Enter PIN Code")

            if text!=plugintools.get_setting("pincode_adult"):
                return

    token = plugintools.get_setting("token")
    if token=="":
        return

    package = params.get("url")

    items = api.get_livetv_channels_by_package(token,package)
    for item in items:
        plugintools.add_item( action="play_livetv", title=format_title(item["title"]) , url=item["url"] , thumbnail=item["thumbnail"], plot=item["plot"], fanart="http://www.boxes.com.mt/addonsrc/art2.jpg" , isPlayable=True, folder=False )

    plugintools.set_view( plugintools.EPISODES )

def play_movie(params):
    plugintools.log("boxes.play_movie "+repr(params))

    mediaurl = params.get("url")

    if "|" in params.get("url"):

        if plugintools.get_setting("quality_selector")=="0":
            selected = plugintools.selector(["Watch in SD","Watch in HD"],"Select quality")
            if selected==-1:
                return
        elif plugintools.get_setting("quality_selector")=="1":
            selected = 0
        elif plugintools.get_setting("quality_selector")=="2":
            selected = 1

        mediaurl = params.get("url").split("|")[selected]

    plugintools.play_resolved_url( mediaurl )

def play_episode(params):
    return play_movie(params)

def play_livetv(params):
    plugintools.log("boxes.play_livetv "+repr(params))

    token = plugintools.get_setting("token")
    if token=="":
        return

    plugintools.log("boxes.play_livetv adult="+repr(params.get("extra")))
    if params.get("extra")=="true":
        if plugintools.get_setting("pincode_adult")!="":
            text = plugintools.keyboard_input(default_text="", title="Enter PIN Code")

            if text!=plugintools.get_setting("pincode_adult"):
                return

    mediaurl = params.get("url")
    plugintools.log("boxes.play_livetv mediaurl="+repr(mediaurl))
    
    if "|" in params.get("url"):

        if plugintools.get_setting("quality_selector_live")=="0":
            plugintools.log("boxes.play_livetv asking for quality")
            selected = plugintools.selector(["Watch in SD","Watch in HD"],"Select quality")
            if selected==-1:
                return
        elif plugintools.get_setting("quality_selector_live")=="1":
            plugintools.log("boxes.play_livetv default to SD quality")
            selected = 0
        elif plugintools.get_setting("quality_selector_live")=="2":
            plugintools.log("boxes.play_livetv default to HD quality")
            selected = 1

        mediaurl = params.get("url").split("|")[selected]
        plugintools.log("boxes.play_livetv mediaurl="+repr(mediaurl))

    mediaurl = api.get_livetv_url(token,mediaurl)
    plugintools.play_resolved_url( mediaurl )

def get_current_and_next_page(current_page):
    if current_page=="":
        current_page="0"

    next_page = str(int(current_page)+1)

    return current_page,next_page

run()