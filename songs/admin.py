from django.contrib import admin

from songs.models import Phrase,Song,SongPhrase

class SongPhraseInline(admin.TabularInline):
	model = SongPhrase
	extra = 1

class SongAdmin(admin.ModelAdmin):
	inlines = (SongPhraseInline,)

admin.site.register(Phrase)
admin.site.register(Song,SongAdmin)
