from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, add_dealer_review_to_db
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import random

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
# Cloud function url

def about(request):
    """ About View"""
    context = {}
    if request.method == "GET":
        about_view = render(request, 'djangoapp/about.html', context)
    return about_view

# Create a `contact` view to return a static contact page


def contact(request):
    """ Contact View """
    context = {}
    if request.method == "GET":
        contact_view = render(request, 'djangoapp/contact.html', context)
    return contact_view

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        # Get dealers from the URL
        dealerships = get_dealers_from_cf('https://06e36d79.us-south.apigw.appdomain.cloud/api/dealerships')
        context['dealerships'] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = 'https://06e36d79.us-south.apigw.appdomain.cloud/api/reviews'
        reviews = get_dealer_reviews_from_cf(url)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        # return HttpResponse(dealer_names)
        context['reviews'] = filter(lambda x: x.dealership == dealer_id, reviews)
        context['dealer_id'] = dealer_id
        dealer = get_dealer_detail_infos(dealer_id)
        context['dealers'] = dealer 
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_dealer_review(request, dealer_id):
    """ Add Review View """
    if request.method == "GET":
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        context = {"cars": cars, "dealer_id": dealer_id
                   }
        add_review_view = render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST" and request.user.is_authenticated:
        form = request.POST
        review = {
            "review_id": random.randint(0, 100),
            "reviewer_name": form["fullname"],
            "dealership": dealer_id,
            "review": form["review"]
        }
        if form.get("purchase"):
            review["purchase"] = True
            review["purchase_date"] = form["purchasedate"]
            car = get_object_or_404(CarModel, pk=form["car"])
            review["car_make"] = car.carmake.name
            review["car_model"] = car.name
            review["car_year"] = car.year
        json_result = add_dealer_review_to_db(review)
        add_review_view = redirect(
            'djangoapp:dealer_details', dealer_id=dealer_id)
    return add_review_view


def get_dealer_detail_infos(dealer_id):
    url = 'https://06e36d79.us-south.apigw.appdomain.cloud/api/dealerships'
    dealerships = get_dealers_from_cf(url)
    return next(filter(lambda x: x.id == dealer_id, dealerships))
