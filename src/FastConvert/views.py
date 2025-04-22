from django.shortcuts import render
from .forms import YouTubeDownloadForm
from urllib.parse import urlparse, parse_qs
from django.http import StreamingHttpResponse, HttpResponseBadRequest
import subprocess

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
        # Formato y nombre según tipo
        if tipo == 'MP3':
            ext = 'mp3'
            content_type = 'audio/mpeg'
            command = [
                'yt-dlp',
                '-f', 'bestaudio',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '192K',
                '-o', '-',  # enviar a stdout
                normalized_url
            ]
        else:  # MP4
            ext = 'mp4'
            content_type = 'video/mp4'
            command = [
                'yt-dlp',
                '-f', 'bestvideo+bestaudio/best',
                '-o', '-',  # enviar a stdout
                normalized_url
            ]

        # Extraer título (para el nombre del archivo)
        info_command = [
            'yt-dlp',
            '--get-title',
            normalized_url
        ]
        result = subprocess.run(info_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        title = result.stdout.strip().replace('"', '').replace("'", '').replace(" ", "_")

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