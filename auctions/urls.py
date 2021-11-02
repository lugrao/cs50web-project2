from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-listing", views.create_listing, name="create_listing"),
    path("listing/<str:id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("add-to-watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove-from-watchlist", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category_name>", views.category, name="category")
]
