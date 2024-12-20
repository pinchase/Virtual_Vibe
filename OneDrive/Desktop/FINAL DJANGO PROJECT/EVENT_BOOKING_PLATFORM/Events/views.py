# Step 5: Create views in booking/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Event, Booking
from django.contrib.auth.models import User

from django.http import  JsonResponse
import requests
from requests.auth import HTTPBasicAuth
from django.http import HttpResponse, HttpResponseRedirect
import json
from . credentials import MpesaAccessToken, LipanaMpesaPpassword
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
def event_list(request):
    events = Event.objects.all()  # Fetch all events
    return render(request, 'event_list.html', {'events': events})

@login_required
def book_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        print("POST request received.")
        number_of_tickets = int(request.POST['number_of_tickets'])
        total_price = event.price * number_of_tickets if event.price > 0 else 0

        # Create and save the booking object
        booking = Booking(
            event=event,
            user_name=request.POST['user_name'],
            user_email=request.POST['user_email'],
            number_of_tickets=number_of_tickets,
            price=total_price  # Ensure the Booking model supports a 'price' field
        )
        booking.save()

        # Store total_price in the session for use in the pay view
        request.session['total_price'] = float(total_price)  # Convert to float for JSON serialization

        # Redirect to the pay view with the event_id
        return redirect('pay', event_id=event.id)

    # For GET request, render the template
    print("GET request received.")
    return render(request, 'book_event.html', {'event': event})

from django.shortcuts import render, redirect, get_object_or_404

def pay(request, event_id):
    # Assume the total price is already calculated and stored in the session
    total_price = request.session.get('total_price')
    if not total_price:
        # Redirect to a previous page if the total price is missing
        return redirect('book_event', event_id=event_id)

    # Retrieve the event or return a 404 if it doesn't exist
    event = get_object_or_404(Event, id=event_id)

    # Pass both total_price and event_id to the template
    return render(request, 'pay.html', {'total_price': total_price, 'event': event})




def stk(request):
    return render(request, 'pay.html')


def about(request):
    return render(request, 'about.html')

def index(request):
    return render(request, 'base.html')

def contact(request):
    return render(request, 'contact_us.html')


def  register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1!= password2:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            messages.success(request, 'Registration successfull!. Please log in')
            return redirect('login')


    return render(request,'register.html')



def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('event_list')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')



def process_payment(request):
    if request.method == 'POST':
        mpesa_number = request.POST.get('mpesa_number')
        total_price = request.session.get('total_price', None)

        if not mpesa_number or not total_price:
            return JsonResponse({'error': 'Invalid payment details.'}, status=400)

        # Safaricom M-Pesa API credentials
        consumer_key = 'your_consumer_key'
        consumer_secret = 'your_consumer_secret'
        access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        stk_push_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

        # Step 1: Get access token
        response = requests.get(
            access_token_url,
            auth=(consumer_key, consumer_secret)
        )
        access_token = response.json().get('access_token')

        if not access_token:
            return JsonResponse({'error': 'Unable to authenticate with M-Pesa.'}, status=500)

        # Step 2: Send STK Push
        headers = {'Authorization': f'Bearer {access_token}'}
        payload = {
            "BusinessShortCode": 174379,
            "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjQxMjA5MDA0MjI1",
            "Timestamp": "20241209004225",
            "TransactionType": "CustomerPayBillOnline",
            "Amount": total_price,
            "PartyA": 254708374149,
            "PartyB": 174379,
            "PhoneNumber": 254708374149,
            "CallBackURL": "https://mydomain.com/path",
            "AccountReference": "Event Booking",
            "TransactionDesc": "Ticket Payment"
        }

        mpesa_response = requests.post(stk_push_url, json=payload, headers=headers)

        if mpesa_response.status_code == 200:
            return redirect('payment_success')  # Redirect to success page
        else:
            return JsonResponse({'error': 'Payment failed. Please try again later.'}, status=500)


def submit_contact(request):
    if request.method == 'POST':
        # Handle form submission here (e.g., save data)
        return HttpResponse("Contact form submitted successfully!")

    # Redirect to the same view with a trailing slash if accessed without one
    if not request.path.endswith('/'):
        return HttpResponseRedirect(request.path + '/')

    return render(request, 'contact_us.html')

def payment_callback(request):
    if request.method == 'POST':
        data = request.body
        # Process the callback data from M-Pesa
        print(data)  # For debugging; you should log this in production
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})


@login_required
def user_dashboard(request):
    # Get the logged-in user's bookings
    user = request.user
    recent_bookings = Booking.objects.filter(user=user).order_by('-date')[:5]  # Fetch the 5 most recent bookings

    # Other user details (e.g., name, email)
    user_details = {
        "username": user.username,
        "email": user.email,
    }

    context = {
        "user_details": user_details,
        "recent_bookings": recent_bookings,
    }
    return render(request, 'dashboard.html', context)