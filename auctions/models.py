from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class Listing(models.Model):
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=5000)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="listings")
    image_url = models.URLField(blank=True)
    starting_bid = models.PositiveIntegerField()
    active = models.BooleanField()

    def __str__(self):
        return f"{self.title} | User: {self.seller.username}"


class Watchlist(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="+")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f"{self.listing.title} being watched by {self.user.username}"


class Comment(models.Model):
    comment = models.TextField(max_length=280)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"Comment by {self.user.username} in {self.listing.title}"


class Bid(models.Model):
    item = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids")
    bid_ammount = models.PositiveIntegerField()
    bidder = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.item.title} | Bid: ${self.bid_ammount} | User: {self.bidder.username}"
