from django.shortcuts import render
from django.urls import path
from pytube import YouTube
from .forms import YouTubeDownloadForm

def index(request):
    form = YouTubeDownloadForm()
    return render(request, 'FastConvert/index.html', {'form': form})

def DownloadYoutubeVideo(request):
    """Vista para crear un nuevo examen"""
    if request.method == 'POST':
        form = YouTubeDownloadForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['URL']
            tipo = form.cleaned_data['tipo']
            yt = YouTube(url)
            if tipo == 'MP3':
                # Lógica para descargar el video como MP3
                audio_stream = yt.streams.filter(only_audio=True).first()
                audio_stream.download(filename=f"{yt.title}.mp3")
            elif tipo == 'MP4':
                # Lógica para descargar el video como MP4
                video_stream = yt.streams.get_highest_resolution()
                video_stream.download(filename=f"{yt.title}.mp4")
            # Redirigir a una página de éxito o mostrar un mensaje
            render(request, 'FastConvert/success.html', {'video_title': yt.title})
        else:
            # Si el formulario no es válido, vuelve a mostrarlo con errores
            return render(request, 'FastConvert/index.html', {'form': form})
    else:
        form = YouTubeDownloadForm()
        return render(request, 'FastConvert/index.html', {'form': form})