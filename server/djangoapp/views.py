from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contactus.html', context)

# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/user_login_bootstrap.html', context)
    else:
        return render(request, 'djangoapp/user_login_bootstrap.html', context)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
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
            return render(request, 'djangoapp/user_registration_bootstrap.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://f39a9d48.eu-gb.apigw.appdomain.cloud/api/dealership"
        ## Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        ## Concat all dealer's short name
        # #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # #Return a list of dealer short name
        context = {"dealerships": dealerships}
        ## Concat all dealer's short name
        # #Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = 'https://f39a9d48.eu-gb.apigw.appdomain.cloud/api/review'
        reviews =  get_dealer_reviews_from_cf(url, dealer_id)
        url2 = "https://f39a9d48.eu-gb.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url2)
        dealership = {}
        for d in dealerships:
            if d.id == dealer_id:
                dealership= d
        context = {"reviews": reviews, "dealer" : dealership}
        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = request.POST   
            review = {
                "name": request.user.username,
                "dealership": dealer_id,
                "review": form["review"],
                "purchase": form.get("purchase")=="on",
            }       
            print (review)    
            if review["purchase"]:
                review["purchase_date"] = datetime.strptime(form.get("purchase_date"), "%Y-%m-%d").isoformat()
                car = CarModel.objects.get(pk=form["car"])
                review["car_model"] = car.title
                review["car_year"]= car.date.year
                review["car_make"] =car.model.name
            json_payload = {"review": review}
            print (review)
            url = "https://f39a9d48.eu-gb.apigw.appdomain.cloud/api/review"
            post_request(url, json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else: 
            context = {
                "cars": CarModel.objects.all(),
                "dealerId": dealer_id
            }
            return render(request, 'djangoapp/add_review.html', context)
    else:
        return redirect("/djangoapp/login")
