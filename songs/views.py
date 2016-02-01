from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from songs.models import Song, Phrase, SongPhrase
from .forms import UploadFileForms
from django.views.decorators.csrf import csrf_exempt
import numpy as np

def transition_matrix(songs, phrases=None):

	''' Takes a queryset of songs as an argument (and optionally phrases as
	well) and returns a transition matrix for the phrases. '''

	all_phrases = Phrase.objects.all()

	''' Generate the transition matrix. Code taken from
	  http://stackoverflow.com/questions/25269476/python-transition-matrix
	'''
	from collections import Counter

	''' Set up the matrix of the right size. '''
	tm_size = len(all_phrases)
	#tm = [[0 for _ in range(tm_size)] for _ in range(tm_size)]
	tm = np.zeros( (tm_size, tm_size) , dtype="int64")

	''' Iterate through the songs and add the phrase transitions to the matrix. '''
	for song in songs:
		phrase_list = list(song.phrase.all())
		''' The zip command creates a list of tuples of the form
		  (<Phrase: 13a>, <Phrase: 5>)
		Counter then returns a dictionary with the tuple as key and the number
		of times that the tuple appears in the list as the value:
		  {(<Phrase: 13a>, (<Phrase: 5>): 4, ... }
		'''
		for (x,y), c in Counter(zip(phrase_list, phrase_list[1:])).items():
			if x != y:
				tm[x.id-1][y.id-1] += c

	''' Remove unwanted phrases if any. '''
	if phrases != None:
		for phrase in all_phrases:
			if phrase not in phrases:
				tm = np.delete(tm, phrase.id, 0)
				tm = np.delete(tm, phrase.id, 1)

	return tm

def display_song_stuff(request):
	
	songs = Song.objects.all()

	#all_phrases = list(Phrase.objects.all())
	#phrases = all_phrases[0:0] + all_phrases[1:]
	#tm = transition_matrix(songs, phrases)
	tm = transition_matrix(songs)
	print(tm)
	#maximum = max([max(l) for l in tm])
	maximum = 0
	for rn, row in enumerate(tm):
		for cn, cell in enumerate(row):
			if rn != cn and cell > maximum:
				maximum = cell

	''' Create colourised output.'''
	rgb = []
	for row in tm:
		rmax = max(row)
		rgbrow = []
		for cell in row:
			if rmax == 0:
				red=0
				green=0
				blue=255
			else:
				red=int(cell*255/rmax)
				green=int(cell*255/maximum)
				blue=int(255-cell*255/rmax)
			rgbrow.append('rgb('+str(red)+','+str(green)+','+str(blue)+')')
		rgb.append(rgbrow)

	phrases = Phrase.objects.all()

	return render(request, 'songs/tm.html', {'songs': songs, 'transition_matrix': tm, 'phrases': phrases, 'colour_matrix': rgb, })

def tm_to_json(request):
	from django.http import JsonResponse
	songs = Song.objects.all()
	tm = transition_matrix(songs)
	return JsonResponse(tm.tolist(), safe=False)

def process_file(file):
	import csv, datetime
	with open('tmp.txt', 'wb+') as destination:
		for chunk in file.chunks():
			destination.write(chunk)
	with open('tmp.txt', 'r') as datafile:
		#for fields in csv.reader(datafile, delimiter='\t'):
		for data in csv.DictReader(datafile, delimiter='\t'):
			if data['Phrase'] != 'Phrase':

				''' Begin with getting or creating the song '''
				song_begin = datetime.datetime.strptime('2014 12 30 15:00:42', '%Y %m %d %H:%M:%S')
				song_end = song_begin + datetime.timedelta(0,600)
				song, created = Song.objects.get_or_create(soundfile=data['Begin File'], singer=data['Singer'], time_begin=song_begin, time_end=song_end)

				''' Now look up the phrase and create the corresponding song phrase. '''
				phrase_begin = song_begin + datetime.timedelta(0,float(data['Begin Time (s)']))
				phrase_end =   song_begin + datetime.timedelta(0,float(data['End Time (s)']))

				phrasenames = []
				phrasenames = data['Phrase'].split('->')
				for phrasename in phrasenames:
					try:
						phrase = Phrase.objects.get(name=phrasename.strip())
					except:
						print('Could not retrieve phrase object. No phrase named x'+phrasename.strip()+'x')
				try:
					print(len(phrasenames))
					if len(phrasenames) == 1:
						sp, c = SongPhrase.objects.get_or_create(song=song, phrase=phrase, is_transition=False, time_begin=phrase_begin, time_end=phrase_end)
					else:
						sp, c = SongPhrase.objects.get_or_create(song=song, phrase=phrase, is_transition=True, time_begin=phrase_begin, time_end=phrase_end)
				except:
					print('Failed to create song phrase')
	return 'f'

@csrf_exempt
def upload_file(request):
	if request.method == 'POST':
		form = UploadFileForms(request.POST, request.FILES)
		if form.is_valid():
			process_file(request.FILES['file'])
			#return HttpResponseRedirect('/songs/file/'+request.POST['filename'])
			return HttpResponseRedirect('/songs/')
	else:
		form = UploadFileForms()
	return render(request, 'songs/upload.html', { 'form': form })

def download_tm(request):
	songs = Song.objects.all()
	tm = transition_matrix(songs)
	phrases = '\t'.join([ p.name for p in Phrase.objects.all() ])
	print(phrases)
	with open('tmp.txt', 'wb+') as destination:
		np.savetxt(destination, tm, fmt='%i', delimiter='\t', header=phrases)
	with open('tmp.txt', 'rb+') as destination:
		response = HttpResponse(destination, content_type='text/plain')
	response['Content-disposition'] = 'attachment; filename="prufa.txt"'
	return response
