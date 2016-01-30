from django.db import models

class Phrase(models.Model):
	name = models.CharField(max_length=8)

	def __str__(self):
		return self.name

class Song(models.Model):
	soundfile = models.CharField(max_length=64)
	singer = models.CharField(max_length=4)
	time_begin = models.DateTimeField()
	time_end = models.DateTimeField()

	phrase = models.ManyToManyField(Phrase,through='SongPhrase', through_fields=('song', 'phrase'))

	def __str__(self):
		phrasestring = ''
		for phrase in self.phrase.all():
			phrasestring += ', '+str(phrase)
		return self.soundfile + '-' + self.singer + ':' + phrasestring[1:]

class SongPhrase(models.Model):
	song = models.ForeignKey(Song)
	phrase = models.ForeignKey(Phrase, related_name='songs')
	is_transition = models.BooleanField(default=False)
	time_begin = models.DateTimeField()
	time_end = models.DateTimeField()
	comment = models.TextField(blank=True, null=True)

#	class Meta:
#		unique_together = ('order', 'song',)
