from unicodedata import category
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Bid, Category, Listing, Comment

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
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

@login_required
def create(request):
    if request.method == "POST":
        request_name = request.POST.get("name")
        request_discription = request.POST.get("discription")
        request_starting_bid = request.POST.get("starting_bid")
        if request.POST.get("category") == None:
            request_category = Category.objects.get(name="Miscellaneous")
        else:
            request_category = Category.objects.get(name=request.POST.get("category"))
        request_category = request_category.id
        print(request_category)
        request_img_URL = request.POST.get("img_URL")
        if ("https://" or "http://") not in request_img_URL:
            request_img_URL = "https://thumbs.dreamstime.com/b/no-image-available-icon-photo-camera-flat-vector-illustration-132483141.jpg"
        request_user = request.user.id
        
        #Listing(name=request_name, discription=request_discription, starting_bid=request_starting_bid, category=request_category, img_URL=request_img_URL, user=request_user, status=False)
        listing = Listing(name=request_name, discription=request_discription, starting_bid=request_starting_bid, category=Category(request_category), img_URL=request_img_URL, user=User(request_user), status=False)
        listing.save()
        return HttpResponseRedirect(reverse(index))
    else:
        return render(request, "auctions/create.html", {
            "categories": Category.objects.all()
        })

def listing(request, id):
    listing = Listing.objects.get(id=id)
    bids = Listing.bids
    comments = Listing.comments

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": bids,
        "comments": comments
    })

#def comment(request, text, listing):

    
