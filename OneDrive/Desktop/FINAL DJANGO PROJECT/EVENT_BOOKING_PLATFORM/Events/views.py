# Step 5: Create views in booking/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Event, Booking
from django.contrib.auth.models import User

from django.http import HttpResponse
import requests
from requests.auth import HTTPBasicAuth
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

        booking = Booking(
            event=event,
            user_name=request.POST['user_name'],
            user_email=request.POST['user_email'],
            number_of_tickets=number_of_tickets,
            price=total_price
        )
        booking.save()

        return redirect('event_list')

    # For GET request, render the template
    print("GET request received.")
    return render(request, 'book_event.html', {'event': event})



def pay(request):
    # return render(request, 'pay.html', {'event_id': event_id})
    if request.method == "POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create the request payload
        payload = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://yourserver.com/callback",  # Update with your actual callback URL
            "AccountReference": "kagiri Peterson",
            "TransactionDesc": "Event payment Charges"
        }
        return render(request, 'pay.html', )
        # Send the request to the API
        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code == 200:
            return HttpResponse("success")
        else:
            return HttpResponse(f"Error: {response.text}", status=response.status_code)

    return HttpResponse("Invalid request method", status=405)

    # response = requests.post(api_url, json=request, headers=headers)
    # return HttpResponse("success")



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