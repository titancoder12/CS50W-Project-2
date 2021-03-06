from unicodedata import name
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    name = models.CharField(max_length=100)
    discription = models.TextField()
    starting_bid = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings")
    img_URL = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    status = models.BooleanField(default=True)
    datetime_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}: ${self.starting_bid}"

class Bid(models.Model):
    amount = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.amount}"


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    user =  models.ForeignKey(User, on_delete=models.PROTECT, related_name="comments")
    datetime_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} commented '{self.text}' on {self.listing}."

class Watchlist(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlistitems")
    user =  models.ForeignKey(User, on_delete=models.PROTECT, related_name="watchlistitems")
    status = models.BooleanField(default=True)