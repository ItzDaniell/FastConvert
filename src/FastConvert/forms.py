from django import forms

class YouTubeDownloadForm(forms.Form):
    URL = forms.URLField(
        label='URL del Video',
        widget=forms.TextInput(attrs={
            'class': 'input-form', 'id': 'url-input',
            'placeholder': 'Introduce aquí la URL del video'
        })
    )
    tipo = forms.ChoiceField(
        choices=[('MP3', 'MP3'), ('MP4', 'MP4')],
        widget=forms.Select(attrs={'class': 'select-form', 'id': 'tipo-select'})
    )