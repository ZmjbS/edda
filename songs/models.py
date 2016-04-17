from django.db import models
#from django.contrib.gis.db import models

class Phrase(models.Model):

	''' This is the fundamental part of a song; sort of like a word. Each
	phrase is identified with a name. Phrases are strung into songs. '''

	name = models.CharField(max_length=8)
	# TODO: It would be nice to have a spectrogram of each phrase.

	def count(self):
		''' Returns the number of times this phrase appears. '''
		return self.songs.count()

	def durations(self):
		''' Returns a list of durations that the phrase takes. '''
		return [ sp.duration() for sp in self.song_phrases.all() ]

	def __str__(self):
		return self.name

class Song(models.Model):

	''' Each song is identified by the soundfile on which it is recorded and
	the singer. The singer is usually identified by an upper case letter of the
	alphabet, in order of which the singer appears in the recording.

	The beginning and ending time of each song is recorded.

	Songs consist of phrases which are referenced through the SongPhrase model.
	'''

	soundfile = models.CharField(max_length=64)
	singer = models.CharField(max_length=4)
	time_begin = models.DateTimeField()
	time_end = models.DateTimeField()

#	position = models.PointField(blank=True, null=True)
#	objects = models.GeoManager()

	phrases = models.ManyToManyField(Phrase,through='SongPhrase', through_fields=('song', 'phrase'), related_name='songs')

	def __str__(self):
		phrasestring = ''
		#for phrase in self.phrase.all():
			#phrasestring += ', '+str(phrase)+str(phrase.is_transition)
		for sp in self.songphrase_set.all():
			if sp.is_transition:
				phrasestring += ', ('+str(sp.phrase)+')'
			else:
				phrasestring += ', '+str(sp.phrase)
		return self.soundfile + '-' + self.singer + ':' + phrasestring[1:]

class SongPhrase(models.Model):

	''' The through-model that ties each song to it's phrases.

	Phrases can occur in songs as pure or as versions of two where the phrase
	is really neither one, but sort of appears as a transition between two
	phrases. This is recorded in the boolean is_transition.

	Each song phrase has a beginning and an end. As there can be interesting
	observations about a particular song phrase, there is a comment field as
	well. '''

	song = models.ForeignKey(Song)
	phrase = models.ForeignKey(Phrase, related_name='song_phrases')
	is_transition = models.BooleanField(default=False)
	time_begin = models.DateTimeField()
	time_end = models.DateTimeField()
	comment = models.TextField(blank=True, null=True)

	def duration(self):
		''' Returns the duration of the song phrase. '''
		return self.time_end - self.time_begin
