"""edda URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from songs.views import display_song_stuff, upload_songs, upload_review, upload_save, tm_to_json, download_tm, songs_to_json, download_song_phrases, phrases_to_json

urlpatterns = [
    url(r'^$', display_song_stuff),
    url(r'^area_and_season/(?P<area_and_season>.*)$', display_song_stuff),
	# APIs that return data rather than pages.
    url(r'^api/tm/$', tm_to_json, name='tm_to_json'),
    url(r'^api/tm/(?P<area_and_season>.*)$', tm_to_json),
    url(r'^api/songs/$', songs_to_json, name='songs_to_json'),
    url(r'^api/songs/(?P<area_and_season>.*)$', songs_to_json),
    url(r'^api/phrases/$', phrases_to_json, name='phrases_to_json'),
    url(r'^api/phrases/(?P<area_and_season>.*)$', phrases_to_json),
	# Downloads
	url(r'^api/download/transition_matrix/$', download_tm, name='download_transition_matrix'),
	url(r'^api/download/transition_matrix/(?P<area_and_season>.*)$', download_tm),
	url(r'^api/download/song_phrases/$', download_song_phrases, name='download_song_phrases'),
	url(r'^api/download/song_phrases/(?P<area_and_season>.*)$', download_song_phrases),
	# Uploads
    url(r'^upload/$', upload_songs),
    url(r'^upload/review$', upload_review),
    url(r'^upload/save$', upload_save),
]
