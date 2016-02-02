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
	#tm_size = len(all_phrases)
	# Set up the matrix to the maximum size.
	tm_size = Phrase.objects.latest('id').id
	#tm = [[0 for _ in range(tm_size)] for _ in range(tm_size)]
	tm = np.zeros( (tm_size, tm_size) , dtype="int64")

	print(len(all_phrases))
	''' Iterate through the songs and add the phrase transitions to the matrix. '''
	for song in songs:
		phrase_list = list(song.phrase.all())
		#phrase_list = list(song.phrase.filter(songs__is_transition=False))
		''' The zip command creates a list of tuples of the form
		  (<Phrase: 13a>, <Phrase: 5>)
		Counter then returns a dictionary with the tuple as key and the number
		of times that the tuple appears in the list as the value:
		  {(<Phrase: 13a>, (<Phrase: 5>): 4, ... }
		'''
		start_phrase = Phrase.objects.get(name='start')
		if start_phrase in phrase_list:
			print('start')
		for (x,y), c in Counter(zip(phrase_list, phrase_list[1:])).items():
			if x != y:
				tm[x.id-1][y.id-1] += c

	''' Remove unwanted phrases if any. '''
	if phrases != None:
		for phrase in all_phrases:
			if phrase not in phrases:
				tm = np.delete(tm, phrase.id, 0)
				tm = np.delete(tm, phrase.id, 1)

	''' Remove unused rows and columns where none are used. '''
	num = 0
	for row in tm:
		if not np.any(row!=0) and not np.any(tm[:,num]!=0):
			print(num, row)
			tm = np.delete(tm,num,0)
			tm = np.delete(tm,num,1)
			all_phrases = all_phrases[:num] + all_phrases[num+1:]
			print(all_phrases)
		else:
			num += 1

	''' Order the matrix. '''
	neworder = np.zeros( len(all_phrases) )
	# Move the Start to the start:
	print(all_phrases)
	print(type(all_phrases))
	newidx = 0
	oldidx = all_phrases.index(Phrase.objects.get(name='Start'))
	neworder[newidx] = oldidx

	# create a list of the order of the phrases:
	'''
	for i in neworder[1:]:
		newidx += 1
		countlist = list(tm[oldidx,:])
		oldidx = countlist.index(max(countlist))

		neworder[newidx] = oldidx
		#neworder[newidx]= list(tm[oldidx,:]).index(max(list(tm[oldidx,:])))
		#print(tm[num-1,:])
		#neworder[num] = list(tm[num-1,:]).index(max(tm[num-1,:]))
		#print(all_phrases.index(max(tm[num,:])))
		num += 1
		print(neworder)
		'''
	neworder = [ 3,  21, 18, 19, 4,  15, 16, 17, 5,  22, 23, 9,  0,  1,  2,  20,  6,  7,  10, 12, 11,  13, 14, 8 ]
	tm = tm[neworder,:]
	tm = tm[:,neworder]
	all_phrases = [ all_phrases[i] for i in neworder ]

	return tm, all_phrases

def display_song_stuff(request):
	
	songs = Song.objects.all()

	#all_phrases = list(Phrase.objects.all())
	#phrases = all_phrases[0:0] + all_phrases[1:]
	#tm = transition_matrix(songs, phrases)
	tm, phrases = transition_matrix(songs)
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

	#phrases = Phrase.objects.all()

	return render(request, 'songs/tm.html', {'songs': songs, 'transition_matrix': tm, 'phrases': phrases, 'colour_matrix': rgb, })

def tm_to_json(request):
	from django.http import JsonResponse
	songs = Song.objects.all()
	tm, phrases= transition_matrix(songs)
	return JsonResponse(tm.tolist(), safe=False)

def songs_to_json(request):
	from django.http import JsonResponse
	from django.core import serializers
	songs = Song.objects.all()
	#tm, phrases= transition_matrix(songs)
	print(songs)
	return JsonResponse(serializers.serialize('json', songs), safe=False)

def process_file(file):
	import csv, datetime
	with open('tmp.txt', 'wb+') as destination:
		for chunk in file.chunks():
			destination.write(chunk)
	with open('tmp.txt', 'r') as datafile:
		for data in csv.DictReader(datafile, delimiter='\t'):
			''' Begin with getting or creating the song '''
			song_begin = datetime.datetime.strptime(data['Date']+'-'+data['Time'], '%d.%m.%Y-%H:%M:%S.%f')
			song_end = song_begin + datetime.timedelta(0,600)
			song, created = Song.objects.get_or_create(soundfile=data['Begin File'], singer=data['Singer'], time_begin=song_begin, time_end=song_end)

			''' Now look up the phrase and create the corresponding song phrase. '''
			phrase_begin = song_begin + datetime.timedelta(0,float(data['Begin Time (s)']))
			phrase_end =   song_begin + datetime.timedelta(0,float(data['End Time (s)']))

			phrasenames = []
			phrasenames = data['PhrasesForDatabase'].split('->')
			for phrasename in phrasenames:
				phrase, created = Phrase.objects.get_or_create(name=phrasename.strip())

				if len(phrasenames) == 1:
					sp, c = SongPhrase.objects.get_or_create(song=song, phrase=phrase, is_transition=False, time_begin=phrase_begin, time_end=phrase_end)
				else:
					sp, c = SongPhrase.objects.get_or_create(song=song, phrase=phrase, is_transition=True, time_begin=phrase_begin, time_end=phrase_end)
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
	tm, phrases = transition_matrix(songs)
	#phrases = '\t'.join([ p.name for p in Phrase.objects.all() ])
	phrases = '\t'.join([ p.name for p in phrases ])
	print(phrases)
	with open('tmp.txt', 'wb+') as destination:
		np.savetxt(destination, tm, fmt='%i', delimiter='\t', header=phrases)
	with open('tmp.txt', 'rb+') as destination:
		response = HttpResponse(destination, content_type='text/plain')
	response['Content-disposition'] = 'attachment; filename="prufa.txt"'
	return response
