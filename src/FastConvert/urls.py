from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('descargar/', views.DownloadYoutubeVideo, name='descargar'),
    path('faq/', views.faq, name='faq'),
    path('aboutme/', views.aboutMe, name='aboutme'),
]