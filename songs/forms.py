from django import forms

class UploadFileForms(forms.Form):
	area_and_season = forms.CharField(max_length=32)
	file = forms.FileField()
