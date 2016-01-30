from django.shortcuts import render
from songs.models import Song, Phrase

def transition_matrix(songs, phrases=None):

	''' Takes a queryset of songs as an argument (and optionally phrases as
	well) and returns a transition matrix for the phrases. '''


	''' If we're not passed any phrases, just get them all. '''
	if phrases == None:
		phrases = Phrase.objects.all()

	''' Generate the transition matrix. Code taken from
	  http://stackoverflow.com/questions/25269476/python-transition-matrix
	  '''
	from collections import Counter

	''' Set up the matrix of the right size. '''
	tm_size = len(phrases)
	tm = [[0 for _ in range(tm_size)] for _ in range(tm_size)]

	''' Iterate through the songs and add the phrase transitions to the matrix. '''
	for song in songs:
		#phrase_list = list(song.phrase.all())
		phrase_list = list(song.phrase.order_by('time_begin'))
		for (x,y), c in Counter(zip(phrase_list, phrase_list[1:])).items():
			tm[x.id-1][y.id-1] += c

	return tm

def display_song_stuff(request):
	
	songs = Song.objects.all()
	#print(songs)

	tm = transition_matrix(songs)
	print(tm)

	phrases = Phrase.objects.all()

	return render(request, 'songs/tm.html', {'songs': songs, 'transition_matrix': tm, 'phrases': phrases, })
