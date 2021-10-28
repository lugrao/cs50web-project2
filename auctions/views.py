# from typing_extensions import ParamSpecKwargs
from typing import List
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django.db.models import Max

from .models import User, Category, Listing, Watchlist, Comment, Bid


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description",
                  "category", "image_url", "starting_bid"]


def index(request):
    listings = Listing.objects.exclude(active=False).all()
    listing_items = []

    for listing in listings:
        item = {
            "id": listing.id,
            "title": listing.title,
            "description": listing.description,
            "image_url": listing.image_url,
            "current_bid": listing.starting_bid
        }

        if listing.bids.all():
            highest_bid = listing.bids.aggregate(Max("bid_ammount"))[
                "bid_ammount__max"]
            # print(highest_bid)
            if highest_bid >= listing.starting_bid:
                item["current_bid"] = highest_bid

        listing_items.append(item)

    return render(request, "auctions/index.html", {
        "listing_items": listing_items
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=request.user.id)
            partial_listing = Listing(seller=user, active=True)
            listing = ListingForm(request.POST, instance=partial_listing)
            listing.save()
            return HttpResponseRedirect(reverse("index"))

    form = ListingForm()
    return render(request, "auctions/create-listing.html", {
        "form": form
    })


def listing(request, id):
    listing = Listing.objects.get(id=id)
    current_bid = listing.starting_bid

    if listing.bids.all():
        highest_bid = listing.bids.aggregate(Max("bid_ammount"))[
            "bid_ammount__max"]
        if highest_bid >= current_bid:
            current_bid = highest_bid

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "current_bid": current_bid
    })
