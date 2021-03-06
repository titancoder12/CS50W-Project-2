from unicodedata import category
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Bid, Category, Listing, Comment, Watchlist

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(status=True)
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
        if len(request_name.replace(" ", "")) > 100:
            return render(request, "auctions/create.html", {
            "categories": Category.objects.all(),
            "alert": True,
            "alert_message": "The title for your listing is too long!",
            "alert_submessage": "Make sure it is 60 characters long at most.",
            "alert_type": "warning"
            })
        request_discription = request.POST.get("discription")
        request_starting_bid = request.POST.get("starting_bid")
        if not request_name or not request_discription or not request_starting_bid:
            return render(request, "auctions/create.html", {
                "categories": Category.objects.all(),
                "alert": True,
                "alert_message": "You forgot to include a field!",
                "alert_submessage": "Make sure you include all fields except the category and the image URL.",
                "alert_type": "warning"
            })
        if request.POST.get("category") == None:
            request_category = Category.objects.get(name="Miscellaneous")
        else:
            request_category = Category.objects.get(name=request.POST.get("category"))
        request_category = request_category.id
        request_img_URL = request.POST.get("img_URL")
        if ("https://" or "http://") not in request_img_URL:
            request_img_URL = "https://thumbs.dreamstime.com/b/no-image-available-icon-photo-camera-flat-vector-illustration-132483141.jpg"
        request_user = request.user.id
        
        #Listing(name=request_name, discription=request_discription, starting_bid=request_starting_bid, category=request_category, img_URL=request_img_URL, user=request_user, status=False)
        listing = Listing(name=request_name, discription=request_discription, starting_bid=int(request_starting_bid), category=Category(request_category), img_URL=request_img_URL, user=User(request_user), status=True)
        listing.save()
        return HttpResponseRedirect(reverse(index))
    else:
        return render(request, "auctions/create.html", {
            "categories": Category.objects.all(),
        })

def listing(request, id):
    listing_id = request.POST.get("listing")
    user_id = request.user.id
    listing = Listing.objects.get(id=id)
    bids = listing.bids.order_by("-amount")
    num_of_bids = int(bids.count())
    highest_bid = bids.first()
    amount = str(request.POST.get("amount"))
    if highest_bid != None:
        highest_bid_amount = highest_bid.amount
    else:
        highest_bid_amount = 0
    
    watchlistitem = Watchlist.objects.filter(listing=Listing(id), user=User(request.user.id))
    watchlistitemstatus = True
    if str(watchlistitem) != "<QuerySet []>":
        watchlistitem = Watchlist.objects.get(listing=Listing(id), user=User(request.user.id))
        if watchlistitem.status == True:
            watchlistitemstatus = True
        else:
            watchlistitemstatus = False
    else:
        watchlistitemstatus = False
    
    if request.method == "POST":
        comments = listing.comments.all()
        if request.POST.get("bid"):
            if listing.status == False:
                return render(request, "auctions/listing.html", {
                "comments": comments,
                "listing": listing,
                "highest_bid": highest_bid_amount,
                "num_of_bids": num_of_bids,
                "alert": True,
                "alert_type": "danger",
                "alert_message": "This listing is closed.",
                "watchliststatus": watchlistitemstatus
                })
            if amount == None or amount == "":
                return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "highest_bid": highest_bid_amount,
                "num_of_bids": num_of_bids,
                "alert": True,
                "alert_type": "warning",
                "alert_message": "Enter an amount to bid for this item.",
                "watchliststatus": watchlistitemstatus
                })
            elif int(amount) < int(listing.starting_bid):
                return render(request, "auctions/listing.html", {
                "comments": comments,
                "listing": listing,
                "highest_bid": highest_bid_amount,
                "num_of_bids": num_of_bids,
                "alert": True,
                "alert_type": "warning",
                "alert_message": "Your bid is too small!",
                "alert_submessage": f"Your bid must be the same or more than the starting bid.",
                "watchliststatus": watchlistitemstatus
                })
            if int(amount) <= highest_bid_amount:
                return render(request, "auctions/listing.html", {
                    "comments": comments,
                    "listing": listing,
                    "highest_bid": highest_bid_amount,
                    "num_of_bids": num_of_bids,
                    "alert": True,
                    "alert_type": "warning",
                    "alert_message": "Your bid is too small!",
                    "alert_submessage": f"Your bid must be more than the current highest bid.",
                    "watchliststatus": watchlistitemstatus
                })
            
            bid = Bid(amount=amount, user=User(user_id), listing=Listing(listing_id))
            bid.save()
            listing = Listing.objects.get(id=id)
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "highest_bid": amount,
                "num_of_bids": num_of_bids+1,
                "comments": comments,
                "alert": True,
                "alert_type": "success",
                "alert_message": "Bid created.",
                "alert_submessage": f"You won't be able to find this in the 'active listings' section when it is closed. Add to <a href=\"{reverse(watchlist)}\">watchlist</a>?",
                "watchliststatus": watchlistitemstatus
            })
        elif request.POST.get("postcomment"):
            comment_text = str(request.POST.get("comment_text"))
            if (comment_text is not "") or (comment_text is not None):
                comment = Comment(user=User(user_id), listing=Listing(id), text=comment_text)
                comment.save()
            comments = listing.comments.all()
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "highest_bid": highest_bid_amount,
                "num_of_bids": num_of_bids,
                "comments": comments,
                "alert": True,
                "alert_type": "success",
                "alert_message": "Comment created.",
                "watchliststatus": watchlistitemstatus
            })
        elif request.POST.get("closelisting"):
            listing.status = False
            listing.save()
            highest_bid.status = True
            highest_bid.save()
            listing = Listing.objects.get(id=id)
            comments = listing.comments.all()
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "highest_bid": highest_bid_amount,
                "num_of_bids": num_of_bids,
                "comments": comments,
                "alert": True,
                "alert_type": "success",
                "alert_message": "Closed listing.",
                "highest_bid_object": highest_bid,
                "watchliststatus": watchlistitemstatus
            })
        elif request.POST.get("addtowatchlist"):
            watchlistitem = Watchlist.objects.filter(listing=Listing(id), user=User(request.user.id))
            if str(watchlistitem) == "<QuerySet []>":
                watchlistitem = Watchlist(listing=Listing(id), user=User(request.user.id))
                watchlistitem.save()
            else:
                watchlistitem = Watchlist.objects.get(listing=Listing(id), user=User(request.user.id))
                watchlistitem.status = True
                watchlistitem.save()
            alert_message = "Added listing to watchlist"

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "highest_bid": highest_bid_amount,
                "num_of_bids": num_of_bids,
                "comments": comments,
                "alert": True,
                "alert_type": "success",
                "alert_message": alert_message,
                "highest_bid_object": highest_bid,
                "watchliststatus": True
            })
        elif request.POST.get("removefromwatchlist"):
            watchlistitem = Watchlist.objects.get(listing=Listing(id), user=User(request.user.id))
            watchlistitem.status = False
            print(watchlistitem.status)
            watchlistitem.save()
            alert_message = "Removed listing from watchlist."
                    
            return render(request, "auctions/listing.html", {
                "watchliststatus": watchlistitem.status,
                "listing": listing,
                "highest_bid": highest_bid_amount,
                "num_of_bids": num_of_bids,
                "comments": comments,
                "alert": True,
                "alert_type": "success",
                "alert_message": alert_message,
                "highest_bid_object": highest_bid,
                "watchliststatus": False
            })
            
        
    else:
        watchlistitem = Watchlist.objects.filter(listing=Listing(id), user=User(request.user.id))
        if str(watchlistitem) != "<QuerySet []>":
            watchlistitem = Watchlist.objects.get(listing=Listing(id), user=User(request.user.id))
            if watchlistitem.status == True:
                watchlistitemstatus = True
            else:
                watchlistitemstatus = False
        else:
            watchlistitemstatus = False
    
        listing = Listing.objects.get(id=id)
        comments = listing.comments.all()
        #bids = listing.bids.order_by("-amount")
        #num_of_bids = int(bids.count())
        #highest_bid = bids.first()
        if listing.status == False:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "highest_bid": highest_bid_amount,
                "num_of_bids": num_of_bids,
                "comments": comments,
                "alert": True,
                "alert_type": "secondary",
                "alert_message": "This listing is not active anymore",
                "highest_bid_object": highest_bid,
                "watchliststatus": watchlistitemstatus
            })
            
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "highest_bid": highest_bid_amount,
            "num_of_bids": num_of_bids,
            "comments": comments,
            "watchliststatus": watchlistitemstatus
        })

def watchlist(request):
    watchlist = Watchlist.objects.filter(user=User(request.user.id))
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })

def category(request, id):
    category = Category.objects.get(id=id)
    listings = category.listings.all()
    return render(request, "auctions/category.html", {
        "category": category,
        "listings": listings
    })

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories,
    })
