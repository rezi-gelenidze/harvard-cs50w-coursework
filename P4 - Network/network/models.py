from django.contrib.auth.models import AbstractUser
from django.db import models


# User model
class User(AbstractUser):
    pass


# Post model with content textfield, timestamp datetimefield and author FK
class Post(models.Model):
    content = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def serialize(self):
        return {
            'pk':self.id,
            'content':self.content,
            'timestamp':self.timestamp,
            'author':self.author
        }

    def __str__(self):
        return f'post {self.pk} of {self.author}'


# Like user and post many to many relaitonship
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} like post #{self.post.pk}'


# Follow user and another user many to many relationship
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    def __str__(self):
        return f'{self.follower.username} following {self.following.username}'