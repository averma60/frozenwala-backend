from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from .models import Influencer, InfluencerRecord
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from ecomApp.models import CustomUser
from order.models import Order
from registration.serializers import MyRefferalsSerializer


@login_required(login_url='backend/login')
def influencer_list(request):
    influencers = InfluencerRecord.objects.all().order_by('-id')
    return render(request, 'backend/influencer_list.html', {'influencers': influencers})


@login_required(login_url='backend/login')
def add_influencer(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        passbook = request.POST.get('pass')
        address = request.POST.get('address')
        type = request.POST.get('type')
        commission = request.POST.get('commission')
        code = request.POST.get('code')

        Influencer.objects.create(
            name=name,
            email=email,
            phone=phone,
            password=password,
            address=address,
            type=type,
            commission=commission,
            code=code,
            passbook=passbook
        )
        return redirect('influencer_list')

    return render(request, 'backend/add_influencer.html')


@login_required(login_url='backend/login')
def edit_influencer(request, influencer_id):
    influencer = get_object_or_404(Influencer, id=influencer_id)
    if request.method == "POST":
        influencer.name = request.POST.get('name')
        influencer.email = request.POST.get('email')
        influencer.phone = request.POST.get('phone')
        influencer.password = request.POST.get('password')
        influencer.address = request.POST.get('address')
        influencer.passbook = request.POST.get('pass')
        influencer.type = request.POST.get('type')
        influencer.commission = request.POST.get('commission')
        influencer.code = request.POST.get('code')

        influencer.save()
        return redirect('influencer_list')

    return render(request, 'backend/edit_influencer.html', {'influencer': influencer})


@login_required(login_url='backend/login')
def delete_influencer(request, influencer_id):
    influencer = get_object_or_404(Influencer, id=influencer_id)
    influencer.delete()
    return redirect('influencer_list')


@login_required(login_url='backend/login')
def view_influencer(request, influencer_id):
    influencer = get_object_or_404(InfluencerRecord, id=influencer_id)
    my_references = CustomUser.objects.filter(refer_by=influencer.user.referral_code)
    references = MyRefferalsSerializer(my_references, many=True)
    return render(request, 'backend/view_influencer.html', {'influencer': influencer, "references": references.data})

@login_required(login_url='backend/login')
def update_influencer(request, influencer_id):
    influencer = get_object_or_404(Influencer, id=influencer_id)

    if request.method == "POST":
        influencer.name = request.POST.get('name')
        influencer.email = request.POST.get('email')
        influencer.phone = request.POST.get('phone')

        influencer.password=  request.POST.get('password')
        influencer.address = request.POST.get('address')
        influencer.passbook = request.POST.get('pass')
        influencer.type = request.POST.get('type')
        influencer.commission = request.POST.get('commission')
        influencer.code = request.POST.get('code')

        influencer.save()
        return redirect('influencer_list')

    return render(request, 'backend/edit_influencer.html', {'influencer': influencer})

# @login_required(login_url='backend/login')
# def view_influencer(request, influencer_id):
#     influencer = get_object_or_404(Influencer, id=influencer_id)
#     return render(request, 'backend/view_influencer.html', {'influencer': influencer})

@login_required(login_url='backend/login')
def activate_influencer(request, influencer_id):
    influencer = get_object_or_404(Influencer, id=influencer_id)
    influencer.status = True
    influencer.save()
    return redirect('influencer_list')

@login_required(login_url='backend/login')
def deactivate_influencer(request, influencer_id):
    influencer = get_object_or_404(Influencer, id=influencer_id)
    influencer.status = False
    influencer.save()
    return redirect('influencer_list')


from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import Influencer

class InfluencerBackend(BaseBackend):
    def authenticate(self, request, phone=None, password=None, **kwargs):
        try:
            influencer = Influencer.objects.get(phone=phone)
            if password == influencer.password:
                return influencer
        except Influencer.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Influencer.objects.get(pk=user_id)
        except Influencer.DoesNotExist:
            return None
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
# from ecomApp.models import CustomUser
from django.conf import settings


@login_required(login_url='influencer/login')
def influencer_dashboard(request):
    if not request.user.is_influencer :
        return redirect('influencer/login')
    return render(request, 'backend/influencer_dashboard.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
def influencer_login(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST['password']
        user = authenticate(request, phone=phone, password=password,is_staff=False,is_influencer=True)
        if user is not None and not user.is_staff and user.is_influencer:
            login(request, user)
            return redirect('influencer_dashboard')  # Replace 'dashboard' with your desired redirect URL
        else:
            messages.error(request, 'Invalid phone number or password')
    return render(request, 'backend/influencer_login.html',{'error': 'Invalid login credentials'})


def influlogout_view(request):
    if request.user.is_authenticated and not request.user.is_staff and request.user.is_influencer:
        request.session['logged_out'] = True  # Set session variable to indicate logout
        logout(request)
    return redirect('influencer/login')












from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
import random
# from django.contrib.auth.models import User
from django.utils import timezone
#
# def send_otp(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         user = Influencer.objects.filter(phone=email).first()  # Use User model
#         if user and user.is_staff:
#             # Generate OTP
#             otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
#
#             # Send OTP email
#             subject = 'OTP for Password Change'
#             message = f'Your OTP for password change is: {otp}'
#             from_email = settings.EMAIL_HOST_USER
#             recipient_list = [email]
#             send_mail(subject, message, from_email, recipient_list)
#
#             # Store OTP and its creation time in database
#             otp_obj, created = Otp.objects.get_or_create(user=user)
#             otp_obj.otp = otp
#
#             otp_obj.otp_created_at = timezone.now()
#             otp_obj.save()
#
#             return redirect('verify_otp')
#         else:
#             error = "Email does not exist or user is not authorized."
#             return render(request, 'send_otp.html', {'error': error})
#     return render(request, 'send_otp.html')
#
# def influencer_verify_email(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         user = CustomUser.objects.filter(email=email, is_staff=True).first()
#         if user:
#             # Generate OTP
#             otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
#
#             # Send OTP email
#             subject = 'OTP for Email Verification'
#             message = f'Your OTP for email verification is: {otp}'
#             from_email = settings.EMAIL_HOST_USER
#             recipient_list = [email]
#             send_mail(subject, message, from_email, recipient_list)
#
#             # Store OTP and its creation time in database
#             otp_obj, created = Otp.objects.get_or_create(user=user)
#             otp_obj.otp = otp
#             otp_obj.otp_created_at = timezone.now()
#             otp_obj.save()
#
#             # Store email in session
#             request.session['verified_email'] = email
#
#             return redirect('verify_otp')
#         else:
#             error = "Email does not exist or user is not authorized."
#             return render(request, 'backend/verify_email.html', {'error': error})
#     return render(request, 'backend/verify_email.html')
# from django.contrib import messages
#
# def influencer_verify_otp(request):
#     email = request.session.get('verified_email')
#     if not email:
#         # If email is not found in session, redirect to the verify_email page
#         messages.error(request, 'Please verify your email first.')
#         return redirect('verify_email')
#
#     if request.method == 'POST':
#         otp_entered = request.POST.get('otp')
#         user = CustomUser.objects.filter(email=email).first()
#         if user and user.is_staff:
#             otp_obj = Otp.objects.filter(user=user).first()
#             if otp_obj:
#                 # Check if OTP matches
#                 if otp_obj.otp == otp_entered:
#                     # Check if OTP is expired (5 minutes expiry)
#                     if (timezone.now() - otp_obj.otp_created_at).total_seconds() > 300:
#                         return render(request, 'backend/verify_otp.html', {'email': email, 'error': 'OTP has expired. Please request a new OTP.'})
#                     else:
#                         return redirect('change_password')
#                 else:
#                     return render(request, 'backend/verify_otp.html', {'email': email, 'error': 'Invalid OTP. Please enter the correct OTP.'})
#             else:
#                 return render(request, 'backend/verify_otp.html', {'email': email, 'error': 'OTP not found. Please request a new OTP.'})
#         else:
#             error = "Otp Does Not Match!!"
#             return render(request, 'backend/verify_otp.html', {'error': error})
#     return render(request, 'backend/verify_otp.html', {'email': email})
# from django.contrib.auth import update_session_auth_hash
#
# def influencer_change_password(request):
#     if request.method == 'POST':
#         email = request.session.get('verified_email')
#         if not email:
#             # If email is not found in session, redirect to the verify_email page
#             messages.error(request, 'Please verify your email first.')
#             return redirect('change_password')
#
#         new_password = request.POST.get('new_password')
#         confirm_password = request.POST.get('confirm_password')
#
#         if new_password != confirm_password:
#             messages.error(request, "Passwords do not match.")
#             return render(request, 'backend/change_password.html')
#
#         user = CustomUser.objects.filter(email=email).first()
#         if user:
#             user.set_password(new_password)
#             user.save()
#             update_session_auth_hash(request, user)  # Keep the user logged in after password change
#             messages.success(request, "Password changed successfully.")
#             return redirect('backend/login')
#         else:
#             messages.error(request, "User not found.")
#             return redirect('verify_email')
#     return render(request, 'backend/change_password.html')

import random
import string
import json
import urllib.parse
import urllib.request
from django.conf import settings
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import  InfluencerOtp
import requests
import random
from urllib.parse import urlencode
def generate_otp(length=6):
    # Generate a random OTP of specified length
    otp = ''.join(random.choices(string.digits, k=length))
    return otp
@csrf_exempt
def sendSMS(apikey, mobile_no,otp):
    # Generate OTP
    # otp = random.randint(100000, 999999)

    # Prepare API parameters
    apikey_encoded = urlencode({'apikey': apikey})
    mobile = '91' + str(mobile_no)
    numbers = [mobile]
    sender = 'FRZWLA'
    message = f"{otp} is your signin OTP for Frozenwala account. Please apply this within 2min."
    message_encoded = urlencode({'message': message})

    # Construct the URL
    url = f"https://api.textlocal.in/send/?{apikey_encoded}&numbers={','.join(numbers)}&sender={sender}&{message_encoded}"

    try:
        # Send SMS using requests library
        response = requests.post(url)

        # Check response status
        if response.status_code == 200:
            # Assume the session and database operations are handled separately in Django views/models
            # Example session handling:
            # request.session['login_mobile_no'] = mobile_no

            # Example database insert (assuming Django ORM usage):
            # otp_instance = Otp.objects.create(mobile_no=mobile_no, otp=otp, created_date=date.today(), created_time=datetime.now().strftime('%H:%M %p'))

            # Example redirection after successful operation
            # return redirect('login/verifyotp')
            print("SMS sent successfully")
        else:
            print(f"Failed to send SMS. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {str(e)}")

@csrf_exempt
def influencer_verify_phone(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        user = Influencer.objects.filter(phone=phone_number, is_influencer=True).first()

        if user:
            otp = generate_otp()
            message = f'Your OTP for phone number verification is: {otp}'
            apikey = "NGI0ZjQzMzA2MTZjNjc1NDUzNTA3MDQ1NGI1ODczNWE="
            sender_name = "FRZWLA"
            # Send OTP via SMS
            sendSMS(apikey, phone_number,otp)

            # Save OTP to database
            otp_instance, created = InfluencerOtp.objects.get_or_create(phone_number=phone_number)
            otp_instance.otp = otp
            otp_instance.otp_created_at = timezone.now()
            otp_instance.save()

            # Store verified phone number in session
            request.session['verified_phone'] = phone_number

            return redirect('influencer/verify_otp')
        else:
            error = "Phone number does not exist or user is not authorized."
            return render(request, 'backend/influencer_verify_email.html', {'error': error})

    return render(request, 'backend/influencer_verify_email.html')


def influencer_verify_otp(request):
    phone_number = request.session.get('verified_phone')

    if not phone_number:
        messages.error(request, 'Please verify your phone number first.')
        return redirect('influencer/verify_email')

    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        otp_obj = InfluencerOtp.objects.filter(phone_number=phone_number).first()

        if otp_obj:
            if otp_obj.otp == otp_entered:
                if (timezone.now() - otp_obj.otp_created_at).total_seconds() > 300:
                    return render(request, 'backend/influencer_verify_otp.html',
                                  {'phone_number': phone_number, 'error': 'OTP has expired. Please request a new OTP.'})
                else:
                    return redirect('influencer/change_password')
            else:
                return render(request, 'backend/influencer_verify_otp.html',
                              {'phone_number': phone_number, 'error': 'Invalid OTP. Please enter the correct OTP.'})
        else:
            return render(request, 'backend/influencer_verify_otp.html',
                          {'phone_number': phone_number, 'error': 'OTP not found. Please request a new OTP.'})

    return render(request, 'backend/influencer_verify_otp.html', {'phone_number': phone_number})


def influencer_change_password(request):
    if request.method == 'POST':
        phone_number = request.session.get('verified_phone')

        if not phone_number:
            messages.error(request, 'Please verify your phone number first.')
            return redirect('influencer/verify_email')

        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'backend/influencer_change_password.html')

        user = Influencer.objects.filter(phone=phone_number).first()

        if user:
            user.password=new_password
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect('influencer/login')
        else:
            messages.error(request, "User not found.")
            return redirect('influencer/verify_email')

    return render(request, 'backend/influencer_change_password.html')

from order.models import Order
from django.db.models import Sum
from django.shortcuts import render
from datetime import datetime
from django.db.models import Sum, F

@login_required(login_url='influencer/login')
def sell_report(request):
    if not request.user.is_influencer:
        return redirect('influencer/login')

    influencer_code = request.user.code  # Assuming influencer_code is a field on your CustomUser model

    # Step 1: Fetch all relevant orders
    all_orders = Order.objects.filter(
        influencer_code=influencer_code,
        order_id__isnull=False
    ).values(
        'created_at__date', 'order_id', 'total_price'
    ).order_by('created_at__date', 'order_id')  # Ensure orders are ordered by date and order_id

    # Step 2: Process orders to aggregate total_price for unique order_id per date
    date_totals = {}
    seen_orders = set()  # To track which order_ids we have already included

    for order in all_orders:
        date = order['created_at__date']
        order_id = order['order_id']
        total_price = order['total_price']

        if order_id not in seen_orders:
            if date not in date_totals:
                date_totals[date] = {
                    'total_amount': 0,
                    'order_ids': set(),
                }

            date_totals[date]['total_amount'] += total_price
            date_totals[date]['order_ids'].add(order_id)
            seen_orders.add(order_id)

    # Step 3: Calculate total sum of total_amount across all dates
    total_sum = sum(data['total_amount'] for data in date_totals.values())

    # Step 4: Convert date_totals dictionary to a list of dictionaries for the template
    orders_by_influencer_and_date = [
        {'created_at__date': date, 'total_amount': data['total_amount'], 'order_ids': data['order_ids']}
        for date, data in sorted(date_totals.items())
    ]

    context = {
        'orders_by_influencer_and_date': orders_by_influencer_and_date,
        'total_sum': total_sum,  # Include total_sum in the context
    }

    return render(request, 'backend/influ_sell_report.html', context)

from django.shortcuts import render
from .models import InfluencerAmount

@login_required(login_url='influencer/login')
def commission_report(request):
    if not request.user.is_influencer:
        return redirect('influencer/login')
    # Fetch influencer commission records related to the current user
    influencer_code = request.user.code
    influencer_amounts = InfluencerAmount.objects.filter(influencer__code=influencer_code)
    total_amount = float(influencer_amounts.aggregate(total_amount=Sum('amount'))['total_amount'])

    # Pass data to the template context
    context = {
        'commission_records': influencer_amounts,
        'total_sum' : total_amount
    }

    return render(request, 'backend/commission_report.html', context)

from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from .models import InfluencerLink
class InfluViewuu(APIView):

    def get(self, request, *args, **kwargs):
        influencer_code = request.GET.get('influencer_code')

        # Get the client's IP address
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip_address = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        if influencer_code:
            # Log the influencer link click
            InfluencerLink.objects.get_or_create(influencer_code=influencer_code, ip_address=ip_address)

        # Redirect to your registration or target page
        return HttpResponseRedirect('/register/')