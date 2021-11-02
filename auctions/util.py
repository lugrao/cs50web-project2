from django.db.models import Max


def get_active_listings(listings):
    active_listings = []

    for listing in listings:
        active_listing = {
            "id": listing.id,
            "title": listing.title,
            "description": listing.description,
            "image_url": listing.image_url,
            "current_bid": listing.starting_bid
        }

        # Get highest bid
        if listing.bids.all():
            highest_bid = listing.bids.aggregate(Max("bid_ammount"))[
                "bid_ammount__max"]
            if highest_bid >= listing.starting_bid:
                active_listing["current_bid"] = highest_bid

        active_listings.append(active_listing)

    return active_listings
