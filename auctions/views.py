from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Category, Listing, Watchlist, Comment, Bid
from .util import get_active_listings


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description",
                  "category", "image_url", "starting_bid"]


def index(request):
    listings = Listing.objects.exclude(active=False).all()
    active_listings = get_active_listings(listings)
    return render(request, "auctions/index.html", {
        "active_listings": active_listings
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

    # Data that will be passed to template:
    context = {
        "listing": listing,
        "starting_bid": listing.starting_bid,
        "current_bid": None,
        "highest_bidder": None,
        "watchlisted": False,
        "is_owner": listing.seller.id == request.user.id,
        "comments": Comment.objects.filter(listing=listing)
    }

    # Get listing's highest bid
    if listing.bids.all():
        highest_bid = listing.bids.order_by("bid_ammount").last()
        if highest_bid.bid_ammount >= context["starting_bid"]:
            context["current_bid"] = highest_bid.bid_ammount
            context["highest_bidder"] = highest_bid.bidder

    # Handle things with logged in user
    if request.user.is_authenticated:

        # Check if listing is in user's watchlist
        user = User.objects.get(id=request.user.id)

        # Check if listing is in user's watchlist
        try:
            for item in user.watchlist.values():
                if item['listing_id'] == int(id):
                    context["watchlisted"] = True
                    break
        except Watchlist.DoesNotExist:
            pass

        # Post requests
        if request.method == "POST":

            # Handle bid
            try:
                bid_ammount = int(request.POST["bid"])
                error = None

                # Check if bid can be placed
                if not listing.bids.all():
                    if bid_ammount < context["starting_bid"]:
                        error = "Your bid must be higher than or equal to the starting bid."
                else:
                    if bid_ammount <= context["current_bid"]:
                        error = "Your bid must be higher than the current bid."

                if error == None:
                    # Place user's bid
                    bid = Bid(item=listing,
                              bid_ammount=bid_ammount, bidder=user)
                    bid.save()
                    context["bid_placed"] = True
                    context["current_bid"] = bid.bid_ammount
                    return render(request, "auctions/listing.html", context)
                else:
                    context["bid_error"] = error
                    return render(request, "auctions/listing.html", context)
            except Exception:
                pass

            # Handle auction closing
            try:
                request.POST["close-auction"]
                listing.active = False
                listing.save()
                return render(request, "auctions/listing.html", context)
            except Exception:
                pass

            # Handle comment post
            try:
                if request.POST["comment"]:
                    comment = Comment(
                        comment=request.POST["comment"], user=user, listing=listing)
                    comment.save()
                    return render(request, "auctions/listing.html", context)
                else:
                    context["comment_error"] = True
                    return render(request, "auctions/listing.html", context)
            except Exception:
                pass

    return render(request, "auctions/listing.html", context)


def watchlist(request):
    user = User.objects.get(id=request.user.id)
    items = user.watchlist.all()
    listings = [i.listing for i in items]
    active_listings = get_active_listings(listings)
    return render(request, "auctions/watchlist.html", {
        "active_listings": active_listings
    })


def add_to_watchlist(request):
    listing_id = request.POST['add-to-watchlist']
    user = User.objects.get(id=request.user.id)
    listing = Listing.objects.get(id=listing_id)
    watchlist = Watchlist(user=user, listing=listing)
    watchlist.save()
    if request.POST["page"] == "listing":
        return HttpResponseRedirect(reverse("listing", kwargs={"id": listing_id}))
    return HttpResponseRedirect(reverse("watchlist"))


def remove_from_watchlist(request):
    listing_id = request.POST['remove-from-watchlist']
    watchlist = Watchlist.objects.filter(
        user_id=request.user.id, listing_id=listing_id)
    watchlist.delete()
    if request.POST["page"] == "listing":
        return HttpResponseRedirect(reverse("listing", kwargs={"id": listing_id}))
    return HttpResponseRedirect(reverse("watchlist"))


def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category(request, category_name):
    category = Category.objects.get(name=category_name)
    listings = category.listings.filter(active=True).all()
    active_listings = get_active_listings(listings)
    return render(request, "auctions/category.html", {
        "category": category,
        "active_listings": active_listings
    })


