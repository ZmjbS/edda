from django.contrib import admin

from songs.models import Phrase,Song,SongPhrase

class SongPhraseInline(admin.TabularInline):
	model = SongPhrase
	extra = 1

class SongAdmin(admin.ModelAdmin):
	inlines = (SongPhraseInline,)
	list_display = ('__str__', 'area_and_season', 'singer')
	list_filter = ('area_and_season', 'time_begin')

admin.site.register(Phrase)
admin.site.register(Song,SongAdmin)
