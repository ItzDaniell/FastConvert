from django.shortcuts import render
from .forms import YouTubeDownloadForm
from urllib.parse import urlparse, parse_qs
from django.http import StreamingHttpResponse, HttpResponseBadRequest
from django.http import FileResponse
import subprocess
import tempfile
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
        cookies_path = '/src/cookies.txt'
        if not os.path.exists(cookies_path):
            return HttpResponseBadRequest("No se encontró el archivo de cookies para autenticación con YouTube.")

        # Obtener título
        info_command = [
            'yt-dlp',
            '--cookies', cookies_path,
            '--get-title',
            normalized_url
        ]
        result = subprocess.run(info_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        title = result.stdout.strip().replace('"', '').replace("'", '').replace(" ", "_")

        # Crear archivo temporal
        with tempfile.TemporaryDirectory() as tmpdir:
            if tipo == 'MP3':
                ext = 'mp3'
                filename = os.path.join(tmpdir, f"{title}.{ext}")
                command = [
                    'yt-dlp',
                    '--cookies', cookies_path,
                    '-f', 'bestaudio',
                    '--extract-audio',
                    '--audio-format', 'mp3',
                    '--audio-quality', '192K',
                    '-o', filename,
                    normalized_url
                ]
                content_type = 'audio/mpeg'
            else:
                ext = 'mp4'
                filename = os.path.join(tmpdir, f"{title}.{ext}")
                command = [
                    'yt-dlp',
                    '--cookies', cookies_path,
                    '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                    '--recode-video', 'mp4',
                    '-o', filename,
                    normalized_url
                ]
                content_type = 'video/mp4'

            # Ejecutar descarga
            subprocess.run(command, check=True)

            # Responder el archivo como descarga
            response = FileResponse(open(filename, 'rb'), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{title}.{ext}"'
            return response

    except Exception as e:
        return HttpResponseBadRequest(f"Error al procesar el video: {e}")

def faq(request):
    return render(request, 'FastConvert/faq.html')

def aboutMe(request):
    return render(request, 'FastConvert/aboutme.html')
