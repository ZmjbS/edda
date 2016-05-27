from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from songs.models import Song, Phrase, SongPhrase
from .forms import UploadFileForms
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import datetime

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
		phrase_list = list(song.phrases.all())
		#phrase_list = list(song.phrases.filter(songs__is_transition=False))
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
			# Remove the row and column
			tm = np.delete(tm,num,0)
			tm = np.delete(tm,num,1)
			# Remove the phrase from the all_phrases list
			all_phrases = all_phrases[:num] + all_phrases[num+1:]
		else:
			num += 1

	phrase_totals = list(np.sum(tm, axis=1))
	print(phrase_totals)	

	''' Order the matrix. '''
	neworder = np.zeros( len(all_phrases) )
	# Move the Start to the start:
	#print(all_phrases)
	#print(type(all_phrases))
	'''
	newidx = 0
	oldidx = all_phrases.index(Phrase.objects.get(name='Start'))
	neworder[newidx] = oldidx
	'''

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
	#neworder = [ 3,  21, 18, 19, 4,  15, 16, 17, 5,  22, 23, 9,  0,  1,  2,  20,  6,  7,  10, 12, 11,  13, 14, 8 ]
	#tm = tm[neworder,:]
	#tm = tm[:,neworder]
	#all_phrases = [ all_phrases[i] for i in neworder ]

	old_err_state = np.seterr(divide='raise')
	ignored_states = np.seterr(**old_err_state)
	percentages = np.divide(tm,phrase_totals)

	print(percentages)

	return tm, all_phrases

def display_song_stuff(request):

	songs = Song.objects.all()
	## Range A
	#range_begin = datetime.date(2011, 1,27)
	#range_end = datetime.date(2011, 2, 2)
	## Range B
	#range_begin = datetime.date(2011, 2, 5)
	#range_end = datetime.date(2011, 2, 10)
	## Range C
	#range_begin = datetime.date(2011, 2,18)
	#range_end = datetime.date(2011, 2, 25)
	## Range D
	#range_begin = datetime.date(2011, 3, 2)
	#range_end = datetime.date(2011, 3, 12)
	#songs = Song.objects.filter(time_begin__range = (range_begin, range_end))
	#print(songs)

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

def phrases_to_json(request):
	from django.http import JsonResponse
	from django.core import serializers
	phrases = Phrase.objects.all()
	phrase_info = []
	for phrase in phrases:
		print(phrase.name, phrase.count())
		phrase_info.append({ 'phrase': phrase.name, 'count': phrase.count(), 'durations': str(phrase.durations()), })
	#	print(phrase_info)
	print(phrase_info)
	#return JsonResponse(serializers.serialize('json', phrase_info), safe=False)
	return JsonResponse(phrase_info, safe=False)
	#return JsonResponse(phrase_info)
	#return JsonResponse(serializers.serialize('json', phrases), safe=False)
	#return JsonResponse({'phrase': 'test', })#, safe=False)
	#return JsonResponse(serializers.serialize('json', phrases), safe=False)

def upload_songs(request):

	''' First and second stages of file upload. Firstly, this generates the
	form and passes to templates/songs/upload_songs.html. Secondly receives the
	filled-in form, loads the data in the data-file into a list and passes this
	back to the same template to display the file contents (or upload a new
	file).

	Third stage: upload_review()
	Fourth stage: upload_save()
	'''

	if request.method != 'POST':

		''' If the request isn't POST, we just return the upload interface. '''

		form = UploadFileForms()
		return render(request, 'songs/upload_songs.html', { 'form': form })

	else:

		''' If request is POST, we're receiving a file upload for pre-
		processing (selecting headers etc.). If we confirm the pre-processed
		file we send it for processing where it gets written into the database.
		'''

		print('upload_songs: is post')
		form = UploadFileForms(request.POST, request.FILES)
		print(form)

		if not form.is_valid():
			print('form is invalid.')
			return render(request, 'songs/upload_songs.html', { 'form': form })
		else:
			print('is valid')

			''' Display form data for pre-processing and confirmation. '''

			import csv, datetime
			from dateutil import parser
			import tempfile
			import io

			with tempfile.TemporaryFile('w+t') as datafile:
				for chunk in request.FILES['file'].chunks():
					''' When we read from the datafile using csv.DictReader()
					it expects a text string, so we need to decode() the
					bytestring to turn it into a text string before writing it
					to datafile. '''
					datafile.write(chunk.decode())
					print(chunk.decode())
				datafile.seek(0)

				''' These are the fields that we need to be able to populate
				the database. The user may upload a file with more fields or
				give the columns funny names so we have to add a step where the
				user matches these fields with the headers in the uploaded
				file. '''
				required_fields = [
					('songphrase-time_begin', 'Time of the phrase beginning, in seconds, from the beginning of the recording.'),
					('songphrase-time_end', 'Time of the phrase sequence end, in seconds.'),
					('song-phrases', 'Phrase-sequence string.'),
					('song-singer', 'The column which identifies the singer.'),
					('song-time_begin-date', 'Date of the beginning of the recording.'),
					('song-time_begin-time', 'Time of the beginning of the recording.'),
					]

				''' Grab the first line of the datafile, strip it of leading
				and trailing spaces and split it along tabs into a list of
				available headers. Then seek back to the beginning of the file
				so that csv.DictReader has the headers to go by.'''
				headers = datafile.readline().strip().split('\t')
				datafile.seek(0)

				''' Generate a list of rows with the data to easily iterate
				over and form a table with the data in the table. '''
				rows = []
				for data in csv.DictReader(datafile, delimiter='\t'):
					row = []
					for field in headers:
						row.append(data[field])
					rows.append(row)

			return_dict= {
				# The form and the area and season which the data is associated with:
				'form': form,
				'area_and_season': request.POST['area_and_season'],
				# Headers and rows to construct the HTML table in the template:
				'headers': headers,	# A list of all headers
				'rows': rows,		# A list of all rows
				# We need the required fields for the user to match the correct headers to.
				'required_fields': required_fields,
				# Now pass the data dictionary (this is for the view):
				'data': data,
				}
			return render(request, 'songs/upload_songs.html', return_dict)

def upload_review(request):

	''' The third stage of the file upload. Receives the data table along with
	headers, parses some of the data (times, transition phrases) and displays
	one last time before committing.

	First and second stage: upload_songs()
	Fourth stage: upload_save()
	'''

	form = UploadFileForms()
	if request.method == 'POST':

		''' We need to receive this by POST as we're doing changes to the database.
		'''

		print('upload_review: is post')

		import csv, datetime
		from dateutil import parser
		import ast

		import tempfile
		with tempfile.TemporaryFile('w+t') as datafile:
			print('file open')
			print(request.POST['headers'])
			''' Write the headers and data to the temporary datafile. '''
			datafile.write(request.POST['headers'].replace('\', \'', '\t').replace('\'], [\'','')[2:-2])
			datafile.write('\n')
			datafile.write(request.POST['rows'].replace('\', \'', '\t').replace('\'], [\'','\n')[3:-3])
			datafile.seek(0)

			''' Populate datatable_headers with the required headers from the
			upload file names. '''
			datatable_headers = []
			for fieldname, fielddescription in ast.literal_eval(request.POST['required_fields']):
				if fieldname != 'song-time_begin-time':
					datatable_headers.append(request.POST[fieldname])
			datafile.seek(0)

			''' Populate a list with the required table. We also populate a
			list of phrases that the file generates '''
			datatable = []
			phrases = []
			for data in csv.DictReader(datafile, delimiter='\t'):
				print(data)
				''' Add the required fields from each row to the datatable. '''
				row = []
				for fieldname, fielddescription in ast.literal_eval(request.POST['required_fields']):
					''' Each row is a list of dictionaries with the keys
					'contents' and 'type'. The latter is so that we're able to
					loop over the phrases in the displayed table in the
					template. '''
					if fieldname == 'song-phrases':
						''' Split the transition phrases up along the '->'
						separators, strip them of surrounding spaces (these may
						occur as typos), and turn them into a list.'''
						print('here')
						print(data)
						print(data[request.POST['song-phrases']])
						transition_phrase_list = list(map(str.strip, data[request.POST['song-phrases']].split('->')))
						row.append({'contents': transition_phrase_list, 'type': 'list', })

						''' Populate the phrases list with all phrases that are
						used in this song file so that it's easier to spot
						errors in phrase names. '''
						for phrase in transition_phrase_list:
							if phrase not in phrases:
								phrases.append(phrase)
					else:
						''' Currently, Raven generates text files with the
						recording date and time in separate columns. We have to
						merge these. '''
						if fieldname == 'song-time_begin-date':
							row.append({
								'contents': parser.parse(data[request.POST['song-time_begin-date']]+' '
														+data[request.POST['song-time_begin-time']]),
								'type': 'date',
								})
						else:
							''' Since we've taken care of both the date and
							time columns above, we just do nothing for the time
							column, but for any other field we just add the
							content and call the type 'other'. '''
							if fieldname != 'song-time_begin-time':
								row.append({'contents': data[request.POST[fieldname]], 'type': 'other', })
				datatable.append(row)

			''' Sort the phrases to make them easier to read through. '''
			phrases = sorted(phrases)

		return_dict = {
			'form': form,
			'area_and_season': request.POST['area_and_season'],
			'data': datatable,
			'datatable_headers': datatable_headers,
			'phrases': phrases,
			}
		return render(request, 'songs/upload_review.html', return_dict )

	else:
		''' If we're not getting an POST request for review just redirect to
		the upload form. '''
		return HttpResponseRedirect('/songs/upload/')

def upload_save(request):

	''' Fourth and final stage of file upload. Receives the data from
	upload_review.html and then:

	* gets or creates the song
	* gets or creates the phrases
	* gets or creates the song-phrases

	Then finally redirects the user to a view that displays information on that
	area_and_season.  '''

	if request.method == 'POST':
		area_and_season = request.POST['area_and_season']

		import tempfile
		with tempfile.TemporaryFile('w+t') as datafile:
			''' Write the headers and data to the temporary datafile. '''
			datafile.write('phrase_begin\tphrase_end\tphrases\tsinger\ttime_begin\n')
			datafile.write(request.POST['data'].replace('}, {', '}\t{').replace('], [','\n')[2:-2])
			datafile.seek(0)

			import csv
			''' Run through each line of the data-"file" and get or create the corresponding song. '''
			for data in csv.DictReader(datafile, delimiter='\t'):

				singer = eval(data['singer'])['contents']
				song_begin = eval(data['time_begin'])['contents']
				phrases = eval(data['phrases'])['contents']

				print('SONG:::', area_and_season, singer, song_begin, '-----------')
				song, created = Song.objects.get_or_create(
					area_and_season=area_and_season,
					singer=singer,
					time_begin=song_begin,
					)

				phrase_begin = song_begin + datetime.timedelta(0,float(eval(data['phrase_begin'])['contents']))
				phrase_end =   song_begin + datetime.timedelta(0,float(eval(data['phrase_end'])['contents']))

				for phrasename in phrases:
					print('Phrase::: ', phrases[0], len(phrases) != 1, phrase_begin, phrase_end)
					phrase, created = Phrase.objects.get_or_create(name=phrasename.strip())
					sp, c = SongPhrase.objects.get_or_create(
						song=song,
						phrase=phrase,
						is_transition=len(phrases) == 1,
						time_begin=phrase_begin,
						time_end=phrase_end
						)

			print('done?')

		return HttpResponseRedirect('/songs/area_and_season/'+area_and_season)

def display_area_and_season(request, area_and_season):
	print(area_and_season)
	songs = Song.objects.filter(area_and_season=area_and_season)
	#print(s)
	#return_dict = {
	#	'songs': s,
	#}
	#return render(request, 'songs/area_and_season.html', return_dict )
	tm, phrases = transition_matrix(songs)
	#print(tm)
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

def download_tm(request):
	## Range A
	#range_begin = datetime.date(2011, 1,27)
	#range_end = datetime.date(2011, 2, 2)
	## Range B
	#range_begin = datetime.date(2011, 2, 5)
	#range_end = datetime.date(2011, 2, 10)
	## Range C
	#range_begin = datetime.date(2011, 2,18)
	#range_end = datetime.date(2011, 2, 25)
	## Range D
	#range_begin = datetime.date(2011, 3, 2)
	#range_end = datetime.date(2011, 3, 12)
	#songs = Song.objects.filter(time_begin__range = (range_begin, range_end))

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

def download_song_phrases(request):
	## Range A
	#range_begin = datetime.date(2011, 1,27)
	#range_end = datetime.date(2011, 2, 2)
	## Range B
	#range_begin = datetime.date(2011, 2, 5)
	#range_end = datetime.date(2011, 2, 10)
	## Range C
	#range_begin = datetime.date(2011, 2,18)
	#range_end = datetime.date(2011, 2, 25)
	## Range D
	#range_begin = datetime.date(2011, 3, 2)
	#range_end = datetime.date(2011, 3, 12)
	#songs = Song.objects.filter(time_begin__range = (range_begin, range_end))

	songs = Song.objects.all()

	#tm, phrases = transition_matrix(songs)
	#phrases = '\t'.join([ p.name for p in Phrase.objects.all() ])
	#phrases = '\t'.join([ p.name for p in phrases ])
	#print(phrases)
	songlist = []
	maxphrases = 0
	for song in songs:
		phrasestring = song.soundfile+'-'+song.singer
		for sp in song.songphrase_set.all():
			# Removes repetitions:
			if not sp.phrase.name == phrasestring.split('\t')[-1]:
				phrasestring += '\t'+sp.phrase.name
			#print(phrasestring.split('\t')[-1])
			print(phrasestring)
		phrases = phrasestring.count('\t')
		if phrases > maxphrases:
			maxphrases = phrases
		songlist.append(phrasestring)
	songlist = np.array(songlist)
	header = 'File-Singer'+'\t'.join([ 'Phr_'+str(num) for num in range(1,maxphrases) ])
	#print(songlist)
	#print(header)
	with open('tmp.txt', 'wb+') as destination:
		np.savetxt(destination, songlist, fmt="%s", delimiter='\t', header=header)
	with open('tmp.txt', 'rb+') as destination:
		response = HttpResponse(destination, content_type='text/plain')
	response['Content-disposition'] = 'attachment; filename="prufa.txt"'
	return response
