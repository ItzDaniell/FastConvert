from django.shortcuts import render
from .forms import YouTubeDownloadForm
from urllib.parse import urlparse, parse_qs
from django.http import StreamingHttpResponse, HttpResponseBadRequest
import subprocess
import os

def index(request):
    form = YouTubeDownloadForm()
    return render(request, 'FastConvert/index.html', {'form': form})

def normalize_youtube_url(url):
    parsed = urlparse(url)
    netloc = parsed.netloc.replace('www.', '')

    if netloc == 'youtu.be':
        vid = parsed.path[1:]
        return f"https://www.youtube.com/watch?v={vid}"
    if netloc == 'youtube.com':
        qs = parse_qs(parsed.query)
        v = qs.get('v')
        if v:
            return f"https://www.youtube.com/watch?v={v[0]}"
    return None

def DownloadYoutubeVideo(request):
    if request.method != 'POST':
        form = YouTubeDownloadForm()
        return render(request, 'FastConvert/index.html', {'form': form})

    form = YouTubeDownloadForm(request.POST)
    if not form.is_valid():
        return render(request, 'FastConvert/index.html', {'form': form})

    url = form.cleaned_data['URL']
    tipo = form.cleaned_data['tipo']
    normalized_url = normalize_youtube_url(url)
    if not normalized_url:
        return HttpResponseBadRequest("URL no válida. Usa un link de YouTube correcto.")

    try:
        # Ruta al archivo cookies.txt compartido (ajústala según tu entorno)
        cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')

        # Extraer título (para el nombre del archivo)
        info_command = [
            'yt-dlp',
            '--cookies', cookies_path,
            '--get-title',
            normalized_url
        ]
        result = subprocess.run(info_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        title = result.stdout.strip().replace('"', '').replace("'", '').replace(" ", "_")

        ext = 'mp3' if tipo == 'MP3' else 'mp4'
        content_type = 'audio/mpeg' if tipo == 'MP3' else 'video/mp4'

        command = [
            'yt-dlp',
            '--cookies', cookies_path,
            '-f', 'bestaudio' if tipo == 'MP3' else 'bestvideo+bestaudio/best',
            '--extract-audio' if tipo == 'MP3' else '',
            '--audio-format', 'mp3' if tipo == 'MP3' else '',
            '--audio-quality', '192K' if tipo == 'MP3' else '',
            '-o', '-',  # Output por stdout
            normalized_url
        ]
        # Eliminar strings vacíos del comando
        command = [arg for arg in command if arg]

        filename = f"{title}.{ext}"

        process = subprocess.Popen(command, stdout=subprocess.PIPE)

        response = StreamingHttpResponse(
            streaming_content=process.stdout,
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        return HttpResponseBadRequest(f"Error al procesar el video: {e}")

def faq(request):
    return render(request, 'FastConvert/faq.html')

def aboutMe(request):
    return render(request, 'FastConvert/aboutme.html')