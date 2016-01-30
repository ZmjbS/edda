from django import forms

class UploadFileForms(forms.Form):
	filename = forms.CharField(max_length=32)
	datetime = forms.DateTimeField()
	file = forms.FileField()
