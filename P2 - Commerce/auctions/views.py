from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from .models import *
from .forms import *
from . import app_utils


def index(request):
    # check if category id is passed
    category_id = request.GET.get('category_id', None)
    category_name = None
    if category_id:
        # get all active listings by category
        all_listings = Listings.objects.filter(active=True, category=category_id)
        category_name = Categories.objects.get(pk=category_id).category
    else:
        # get all active listings
        all_listings = Listings.objects.filter(active=True)

    # assign formated and correct price and shorten title and description if needed
    #  to each listing function is defined in app_utils.py
    for listing in all_listings:
        listing.price = app_utils.get_price(listing.pk)
        listing.title = app_utils.shorten_text(listing.title, 'title')
        listing.description = app_utils.shorten_text(listing.description, 'description')

    return render(request, "auctions/index.html", {
        'listings': all_listings,
        'category_name': category_name,
        'empty_message' : "No active listings",
        'header' : 'Active listings'
    })


def listing(request, listing_id):
    if request.method == "GET":
        listing = app_utils.retrieve_listing(listing_id, request.user)
        if listing:
            # if listing is not active
            if not listing['listing'].active:
                winner = app_utils.determine_winner(listing_id)
                # check if viewer is winner
                if winner == request.user:
                    message = 'Congratulations, You won this auction!'
                else:
                    if winner:
                        message = f'Auction winner is: {winner.username}'
                    else:
                        message = 'There is no winner (No one has placed any bids)'
                listing['message'] = message

            return render(request, 'auctions/listing.html', listing)
        else:
            return render(request, 'auctions/404.html', status=404)
    # POST request
    if request.user.is_authenticated:
        # get all possible parameters
        bid = request.POST.get('bid', None)
        comment = request.POST.get('comment', None)
        close = request.POST.get('close', False)

        # close listing ajax request handler
        if close:
            listing = Listings.objects.get(pk=listing_id)
            if listing.seller == request.user:
                listing.active = False
                listing.save()
                return JsonResponse({}, status=200)
            else:
                return JsonResponse({}, status=400)

        # if comment form id submitted
        if comment:
            new_comment = Comments(
                author=request.user,
                text=comment,
                post=Listings.objects.get(pk=listing_id)
            )
            new_comment.save()

            # redirect to the same listing
            return HttpResponseRedirect(reverse('listings', kwargs={
                'listing_id' : listing_id
            }))
        elif bid:
            # if bid form is submitted, validate and save bid
            validated_bid = app_utils.validate_bid(bid, listing_id)

            if validated_bid:
                new_bid = Bid(
                    listing_id=Listings.objects.get(pk=listing_id),
                    bidder_id=request.user,
                    bid=validated_bid
                )
                new_bid.save()
                return HttpResponseRedirect(reverse('listings', kwargs={
                    'listing_id' : listing_id
                }))
            else:
                # if bid is invalid, create error message
                error = "Invalid bid. (bid must be positive number that's higher than current price)"
                # render current listing page with error message
                listing = app_utils.retrieve_listing(listing_id, request.user)
                if listing:
                    listing['error'] = error
                return render(request, 'auctions/listing.html', listing)
        else:
            return HttpResponseRedirect(reverse('listings', kwargs={
                    'listing_id' : listing_id
                }))
    # if unauthenticated user  has requested POST, redirect to login page
    return HttpResponseRedirect(reverse('login'))


@login_required(login_url='/login')
def watchlist(request):
    if request.method == "POST":
        # get data
        listing_id = request.POST.get('listing_id')
        user_id = request.user

        # if data exists
        if listing_id and user_id:
            try:
                # check if there are any rows of the given user and listing
                result = Watchlist.objects.get(user_id=user_id, listing_id=listing_id)
            except:
                result = None

            # if row exists
            if result:
                # switch False to True or True to False
                if result.watched:
                    result.watched = False
                    watching = False
                else:
                    result.watched = True
                    watching = True
                result.save()
            else:
                # if there are no rows, create new one with True 
                new = Watchlist(
                    listing_id=Listings.objects.get(pk=listing_id),
                    user_id=user_id
                    )
                new.save()
                watching = True
            # success
            return JsonResponse({"watching" : watching}, status=200)
        else:
            # bad request
            return JsonResponse({}, status=400)
    
    # GET request
    # get all watched listings
    user_id = request.user
    # get list of results
    results = list(Watchlist.objects.filter(
        user_id=user_id,
        watched=True
    ))

    # iterate over results, format listing and replace each watchlist result with listing object,
    for i in range(len(results)):
        listing = results[i].listing_id

        # assign formated and correct price and shorten title and description if needed
        # to each listing function is defined in app_utils.py
        listing.price = app_utils.get_price(listing.pk)
        listing.title = app_utils.shorten_text(listing.title, 'title')
        listing.description = app_utils.shorten_text(listing.description, 'description')

        # replace watchlist object with listing object
        results[i] = listing

    return render(request, "auctions/index.html", {
        'listings' : results,
        'empty_message' : "No watched listings.",
        'header' : 'Watchlisted'
    })


@login_required(login_url='/login')
def create(request):
    if request.method == 'POST':
        form = NewListingForm(request.POST)
        if form.is_valid():
            # create model row and save
            listing = Listings(
                seller = request.user,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                url = form.cleaned_data['url'],
                category = Categories.objects.get(pk=int(form.cleaned_data['category'])),
                price = form.cleaned_data['price']
            )
            listing.save()
            # redirect to the new listing
            return HttpResponseRedirect(reverse('listings', args=(listing.pk,)))
    else:
        # if GET, render new blank form
        form = NewListingForm()

    return render(request, 'auctions/create.html', {
        'form' : form
    })


def categories(request):
    # get all category names and icon URLs
    all_categories = Categories.objects.all()
    return render(request, 'auctions/categories.html', {
        'categories' : all_categories
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


@login_required(login_url='/login')
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


def error_404(request, exception):
        return render(request,'auctions/404.html', exception)


def error_500(request):
        return render(request,'auctions/500.html')