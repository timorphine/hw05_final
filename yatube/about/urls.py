from django.urls import path

from . import views

app_name = 'about'

urlpatterns = [
    path('author/', views.author.as_view(), name='author'),
    path('tech/', views.tech.as_view(), name='tech'),
]
