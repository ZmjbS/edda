from django.contrib import admin

from songs.models import Phrase,Song,Sequence

class SequenceInline(admin.TabularInline):
	model = Sequence
	extra = 1

class SongAdmin(admin.ModelAdmin):
	inlines = (SequenceInline,)

admin.site.register(Phrase)
admin.site.register(Song,SongAdmin)
