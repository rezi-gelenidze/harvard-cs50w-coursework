from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

class Categories(models.Model):
    category = models.CharField(max_length=40)
    icon = models.CharField(max_length=50)

    def __str__(self):
        return self.category
        

class Listings(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Seller')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=700)
    date = models.DateTimeField(default=timezone.now)
    url = models.URLField(blank=True)
    category = models.ForeignKey(Categories, verbose_name='Category', on_delete=models.DO_NOTHING)
    price = models.FloatField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Watchlist(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    listing_id = models.ForeignKey(Listings, on_delete=models.CASCADE)
    watched = models.BooleanField(default=True)

    def __str__(self):
        return f'User {self.user_id} : Listing {self.listing_id}'


class Comments(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    post = models.ForeignKey(Listings, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'User {self.author}'


class Bid(models.Model):
    listing_id = models.ForeignKey(Listings, on_delete=models.CASCADE)
    bidder_id = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.FloatField()

    def __str__(self):
        return f'Bidder {self.bidder_id} on Listing {self.listing_id}'