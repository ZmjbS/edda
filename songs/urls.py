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
from songs.views import display_song_stuff, upload_file, tm_to_json, download_tm

urlpatterns = [
    url(r'^$', display_song_stuff),
    url(r'^upload/$', upload_file),
    url(r'^api/tm/$', tm_to_json, name='tm_to_json'),
	url(r'^prufa/$', download_tm),
]
