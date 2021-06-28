from django.urls import path, re_path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path('categories', views.categories, name='categories'),
    path('listings/<int:listing_id>', views.listing, name='listings'),
    path('watchlist', views.watchlist, name='watchlist'),
    path('create', views.create, name='create'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
