from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.index, name="wiki-index"),
    re_path(r"wiki/(?P<title>\w+)?", views.entrypage, name='wiki-entry'),
    re_path(r"edit/(?P<title>\w+)?", views.editpage, name='wiki-edit'),
    path('new/', views.newentry, name='wiki-new'),
    path('search/', views.search, name='wiki-search')
]
