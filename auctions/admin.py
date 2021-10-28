from django.contrib import admin

from .models import User, Bid, Comment, Listing, Category, Watchlist

# Register your models here.

admin.site.register(User)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(Watchlist)
