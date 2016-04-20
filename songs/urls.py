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
from songs.views import display_song_stuff, upload_songs, upload_review, upload_process, tm_to_json, download_tm, songs_to_json, download_song_phrases, phrases_to_json

urlpatterns = [
    url(r'^$', display_song_stuff),
    url(r'^upload/$', upload_songs),
    url(r'^upload/review$', upload_review),
    url(r'^upload/process$', upload_process),
    url(r'^api/tm/$', tm_to_json, name='tm_to_json'),
    url(r'^api/songs/$', songs_to_json, name='songs_to_json'),
    url(r'^api/phrases/$', phrases_to_json, name='phrases_to_json'),
	url(r'^api/download/tm$', download_tm, name='download_transition_matrix'),
	url(r'^api/download/song_phrases$', download_song_phrases, name='download_song_phrases'),
]
