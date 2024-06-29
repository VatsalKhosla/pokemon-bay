from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Category, Listing, Comment, Bid 

def listing(request,id):
    listingdata=Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingdata.watchlist.all()
    allComments=Comment.objects.filter(listing=listingdata)
    isOwner=request.user.username==listingdata.owner.username
    return render(request, "auctions/listing.html",{
        "listing":listingdata,
        "isListingInWatchlist":isListingInWatchlist,
        "allComments":allComments,
        "isOwner": isOwner
    })
def closeAuction(request,id):
    listingdata=Listing.objects.get(pk=id)
    listingdata.isActive=False
    listingdata.save()
    isOwner=request.user.username==listingdata.owner.username
    isListingInWatchlist = request.user in listingdata.watchlist.all()
    allComments=Comment.objects.filter(listing=listingdata)
    return render(request, "auctions/listing.html",{
        "listing":listingdata,
        "isListingInWatchlist":isListingInWatchlist,
        "allComments":allComments,
        "isOwner": isOwner,
        "update":True,
        "message":"Congratulations! Your Auction is closed."
    })

def addBid(request, id):
    newBid=request.POST["newBid"]
    listingdata=Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingdata.watchlist.all()
    allComments=Comment.objects.filter(listing=listingdata)
    isOwner=request.user.username==listingdata.owner.username
    if int(newBid)>listingdata.price.bid:
        updateBid=Bid(user=request.user,bid=int(newBid))
        updateBid.save()
        listingdata.price=updateBid
        listingdata.save()
        return render(request,"auctions/listing.html",{
          "listing":listingdata,
          "message":"Bid was updated successfully",
          "update": True,
          "isListingInWatchlist":isListingInWatchlist,
          "allComments":allComments,
           "isOwner": isOwner
        })
    else:
        return render(request,"auctions/listing.html",{
          "listing":listingdata,
          "message":"Bid updated failed",
          "update": False,
          "isListingInWatchlist":isListingInWatchlist,
          "allComments":allComments,
          "isOwner": isOwner
        })
        

def addComment(request, id):
    currentUser=request.user
    listingdata=Listing.objects.get(pk=id)
    message=request.POST['newComment']

    newComment=Comment(
        author=currentUser,
        listing=listingdata,
        message=message
    )
    newComment.save()

    return HttpResponseRedirect(reverse("listing",args=(id, )))


def displayWatchlist(request):
    currentUser=request.user
    listings=currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html",{
        "listings":listings
    })

def removeWatchlist(request,id):
    listingdata=Listing.objects.get(pk=id)
    currentUser=request.user
    listingdata.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(id, )))

def addWatchlist(request,id):
    listingdata=Listing.objects.get(pk=id)
    currentUser=request.user
    listingdata.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(id, )))
    
def index(request):
    activeListings=Listing.objects.filter(isActive=True)
    allCategories=Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings":activeListings,
        "categories":allCategories
    })

def displayCategory(request):
    if request.method=="POST":
        categoryform=request.POST['category']
        category=Category.objects.get(categoryName=categoryform)
        activeListings=Listing.objects.filter(isActive=True, category=category)
        allCategories=Category.objects.all()
        return render(request, "auctions/index.html",{
        "listings":activeListings,
        "categories":allCategories
      })

def createListing(request):
    if request.method=="GET":
        allCategories=Category.objects.all()
        return render(request,"auctions/create.html",
        {"categories":allCategories
        })
    else:
        title=request.POST["title"]
        description=request.POST["description"]
        imageurl=request.POST["imageurl"]
        price=request.POST["price"]
        category=request.POST["category"]       
        currentUser=request.user

        categorydata=Category.objects.get(categoryName=category)
        
        bid=Bid(bid=int(price),user=currentUser)
        bid.save()

        newListing=Listing(
            Title=title,
            description=description,
            imageUrl=imageurl,
            price=bid,
            category=categorydata,
            owner=currentUser
        )

        newListing.save()

        return HttpResponseRedirect(reverse(index))
        return render(request,"auctions/create.html")


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
