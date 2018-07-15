from django import forms


class AlbumForm(forms.Form):
    album_name = forms.CharField(label='Titel', max_length=100, required=True)
    album_description = forms.CharField(label='Beschrijving', widget=forms.Textarea)
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
