from django.shortcuts import render
from django.http import HttpResponseRedirect
from songs.models import Song, Phrase, Sequence
from .forms import UploadFileForms
from django.views.decorators.csrf import csrf_exempt

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
		phrase_list = list(song.phrase.all())
		#phrase_list = list(song.phrase.order_by('time_begin'))
		#phrase_list = list(song.sequence_set.order_by('time_begin'))
		print(phrase_list)
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

def process_file(file):
	import csv, datetime
	with open('tmp.txt', 'wb+') as destination:
		for chunk in file.chunks():
			destination.write(chunk)
	with open('tmp.txt', 'r') as datafile:
		#for fields in csv.reader(datafile, delimiter='\t'):
		for data in csv.DictReader(datafile, delimiter='\t'):
			''' Begin with getting or creating the song '''
			song_begin = datetime.datetime.strptime('2014 12 30 15:00:42', '%Y %m %d %H:%M:%S')
			song_end = song_begin + datetime.timedelta(0,600)
			song, created = Song.objects.get_or_create(soundfile=data['Begin File'], singer=data['Singer'], time_begin=song_begin, time_end=song_end)
			''' Now look up the phrase and create the corresponding sequence. '''
			p_string = data['Phrase'].split('->')
			#print(p_string[0], type(p_string[0]))
			try:
				phrase = Phrase.objects.get(name=p_string[0])
			except:
				print('Could not retrieve phrase object. No phrase named x'+p_string[0]+'x')
			try:
				#transit = Phrase.objects.get(name=p_string[1]) if len(p_string) > 0 else None
				transit = None
			except:
				print('Could not retrieve transition object. No phrase named '+p_string[0])
			phrase_begin = song_begin + datetime.timedelta(0,float(data['Begin Time (s)']))
			phrase_end =   song_begin + datetime.timedelta(0,float(data['End Time (s)']))

			#print(song, type(song))
			#print(phrase, type(phrase))
			#print(transit, type(transit))
			#print(phrase_begin, type(phrase_begin))
			#print(phrase_end, type(phrase_end))
			try:
				sequence = Sequence.objects.create(song=song, phrase=phrase, transitions_to=transit, time_begin=phrase_begin, time_end=phrase_end)
				#print(sequence)
			except:
				print('Failed to create sequence')
	return 'f'

@csrf_exempt
def upload_file(request):
	if request.method == 'POST':
		form = UploadFileForms(request.POST, request.FILES)
		if form.is_valid():
			process_file(request.FILES['file'])
			return HttpResponseRedirect('/songs/file/'+request.POST['filename'])
	else:
		form = UploadFileForms()
	return render(request, 'songs/upload.html', { 'form': form })
