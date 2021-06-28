from django.contrib import admin

from .models import User, Post, Follow, Like

# registering models
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Follow)