
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('following', views.following, name='following'),
    path("profile/<str:username>", views.profile, name='profile'),  # profile view

    # API for like, edit and follow
    path('edit', views.edit, name='edit'),
    path('like', views.like, name='like'),
    path('follow', views.follow, name='follow'),
]
