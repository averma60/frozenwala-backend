# views.py
from influencer.models import InfluencerLink
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
# from django_otp import devices_for_user
# from .serializers import RegistrationSerializer
from ecomApp.models import CustomUser,Otp
import random
from django.utils import timezone
import json
# views.py
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
User = get_user_model()
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CustomUserSerializer,ProfileSerializer,ProfileUpdateSerializer, MyRefferalsSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from walet.models import Walet,ReferralBenefit,InstallationBenefit, WalletTransaction
import requests

# @api_view(['POST'])
# def register_user(request):
#     if request.method == 'POST':
#         serializer = UserSerializer(data=request.data)
#         try:
#             if serializer.is_valid():
#                 # Hash the password before saving
#                 password = make_password(serializer.validated_data.get('password'))
#                 serializer.validated_data['password'] = password
#                 user = serializer.save()
#                 return Response({"message": "Registration successful!"}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except CustomUser.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# @api_view(['POST'])
# def login_user(request):
#     if request.method == 'POST':
#         phone_number = request.data.get('phone_number')
#         password = request.data.get('password')
#         try:
#             user = CustomUser.objects.get(phone_number=phone_number)
#         except CustomUser.DoesNotExist:
#             return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
#
#         if check_password(password, user.password):
#             return Response({"message": "Login successful!","user_id":user.id,"status":"success"}, status=status.HTTP_200_OK)
#         else:
#             # return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
import random
from django.http import HttpResponseRedirect
from django.views import View
from .models import ReferralLink
import string
AUTH_USER_MODEL = 'ecomApp.CustomUser'
from random import choices
from string import ascii_uppercase, digits
from decimal import Decimal
class RegistrationViewuu(APIView):

    def get(self, request, *args, **kwargs):
        referral_code = request.GET.get('referral_code')

        # Get the client's IP address
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip_address = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        if referral_code:
            # Log the referral link click
            ReferralLink.objects.get_or_create(referral_code=referral_code, ip_address=ip_address)

        # Redirect to your registration or target page
        return HttpResponseRedirect('/register/')

class RegistrationView(APIView):
    # def post(self, request):
    #     request_data = json.loads(request.body.decode('utf-8'))
    #
    #     serializer = CustomUserSerializer(data=request_data)  # Use request_data instead of request.data
    #     print(request_data, "============")
    #     if serializer.is_valid():
    #
    #         phone_number = request_data.get('phone_number')  # Assuming phone_number is in request data
    #         otp_code = request_data.get('otp_value')  # Assuming OTP code is in request data
    #         name = request_data.get('name')  # Assuming name is in request data
    #
    #         # Verify OTP for the given phone number
    #         try:
    #             otp_instance = Otp.objects.get(phone_number=phone_number, otp=otp_code)
    #         except Otp.DoesNotExist:
    #             return Response({'error': 'Invalid OTP'}, status=400)
    #
    #         # OTP verification successful, proceed with user registration
    #         user = serializer.save()
    #         refresh = RefreshToken.for_user(user)
    #
    #         # Delete the OTP record
    #         otp_instance.delete()
    #
    #         response_data = {
    #             'status': 'success',
    #             'refresh': str(refresh),
    #             'access': str(refresh.access_token),
    #         }
    #         return Response(response_data, status=201)
    #     return Response(serializer.errors, status=400)
    #

    def post(self, request):
        request_data = request.data
        serializer = CustomUserSerializer(data=request_data)

        if serializer.is_valid():
            phone_number = request_data.get('phone_number')
            otp_code = request_data.get('otp_value')
            name = request_data.get('name')
            influencer_code = request_data.get('influencer_code')
            refer_by = request_data.get('referral_code')


            try:
                with transaction.atomic():
                    otp_instance = Otp.objects.get(phone_number=phone_number, otp=otp_code)
                   
                    user = serializer.save()

                    user.referral_code = self.generate_unique_referral_code()

                    first_installation_benefit = InstallationBenefit.objects.first()
                    
                    wallet_amount = 0
                    if first_installation_benefit:
                        wallet_amount = Decimal(first_installation_benefit.price)
                        user.walet = wallet_amount
                    else:
                        user.walet = Decimal(0)
                    
                    if influencer_code:
                        user.influencer_code = influencer_code

                    if refer_by:
                        user.refer_by = refer_by

                    self.apply_referral_benefit(request, user)

                    self.apply_influencer_code(request, user)

                    # Save user with referral code and wallet value
                    user.save()

                    if wallet_amount:
                        WalletTransaction.objects.create(
                            user_id=user.id,  
                            opening_bal=wallet_amount,
                            credit_bal=wallet_amount,
                            debit_bal=0,
                            closing_bal=wallet_amount,
                            transaction_type="Installation Benefit",
                            created_at=timezone.now(),
                            updated_at=timezone.now()
                        )


                    # Generate refresh token for the user
                    refresh = RefreshToken.for_user(user)

                    # Delete the OTP record
                    otp_instance.delete()

                    # Prepare response data
                    response_data = {
                        'status': 'success',
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user_id': user.id,
                        'name': user.name,
                        'referral_code': user.referral_code,
                        'wallet': user.walet,
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
            except Otp.DoesNotExist:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def generate_unique_referral_code(self):
        while True:
            code = ''.join(choices(ascii_uppercase + digits, k=6))
            if not CustomUser.objects.filter(referral_code=code).exists():
                return code

    def apply_referral_benefit(self, request, user):
        # Get the client's IP address
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip_address = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # Check if the IP address exists in the ReferralLink model
        referral_links = ReferralLink.objects.filter(ip_address=ip_address)

        if referral_links.exists():
            referral_link = referral_links.first()
            referrer = CustomUser.objects.filter(referral_code=referral_link.referral_code).first()
            if referrer:
                # Get the referral benefit amount
                referral_benefit = Decimal(ReferralBenefit.objects.first().price)
                referrer.walet = Decimal(referrer.walet) + referral_benefit
                referrer.save()

                # Delete all referral link objects with the same IP address
                referral_links.delete()



    def apply_influencer_code(self, request, user):
        # Get the client's IP address
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip_address = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # Check if the IP address exists in the InfluencerLink model
        influencer_links = InfluencerLink.objects.filter(ip_address=ip_address)

        if influencer_links.exists():
            influencer_link = influencer_links.first()
            # Save the influencer_code into the CustomUser's field
            user.influencer_code = influencer_link.influencer_code
            user.save()

            # Delete all influencer link objects with the same IP address
            influencer_links.delete()


from rest_framework.permissions import AllowAny


class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow access to all users

    def post(self, request):
        request_data = json.loads(request.body.decode('utf-8'))
        phone_number = request_data.get('phone_number')
        otp = request_data.get('otp_value')
        registration_id = request_data.get('registration_id', '')

        # Verify OTP for the given phone number
        try:
            otp_instance = Otp.objects.get(phone_number=phone_number, otp=otp)
        except Otp.DoesNotExist:
            return Response({'error': 'Invalid OTP'}, status=400)

        # OTP verification successful, authenticate the user using phone number
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=401)

        if user is not None:
            user.otp_value = otp

            # Authentication successful, generate tokens
            refresh = RefreshToken.for_user(user)
            if registration_id:
                # Update registration_id in CustomUser model
                user_profile = CustomUser.objects.get(id=user.id)
                user_profile.registration_id = registration_id
                user_profile.save()

            user.registration_id = registration_id
            # Update otp_value in CustomUser model
            user.otp_value = otp  # Assuming you have a field named 'otp_value' in your CustomUser model
            user.save()

            # Delete the OTP instance
            otp_instance.delete()

            response_data = {
                'user_id': user.id,
                'name': user.name,
                'referral_code': user.referral_code,
                'wallet': user.walet,
                'status': 'success',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(response_data, status=200)
        else:
            # Authentication failed
            return Response({'error': 'Invalid credentials'}, status=401)
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Address
from .serializers import AddressSerializer
from rest_framework.permissions import IsAuthenticated

class AddressList(APIView):
    permission_classes = [AllowAny]  # Allow access to all users

    def get(self, request):
        try:
            # Get the user_id from query parameters
            user_id = request.query_params.get('user_id')

            # Check if user_id parameter is provided
            if user_id is None:
                return Response({"error": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve addresses associated with the user
            addresses = Address.objects.filter(user_id=user_id)

            # Serialize the addresses data
            serializer = AddressSerializer(addresses, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        # Accessing data using request.data.get()
        name = request.data.get('newname')
        phone = request.data.get('phone')
        address = request.data.get('address')
        city = request.data.get('city')
        state = request.data.get('state')
        country = request.data.get('country')
        zip_code = request.data.get('zip_code')
        user_id = request.data.get('user_id')

        # Check if user_id is provided and if it is a valid user ID
        if not user_id:
            return Response({"error": "User ID is required."}, status=400)
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid User ID."}, status=400)

        # Create the Address object
        address_obj = Address.objects.create(
            newname=name,
            phone=phone,
            address=address,
            city=city,
            state=state,
            country=country,
            zip_code=zip_code,
            status=1,
            user_id=user
        )

        return Response({"message": "Address created successfully."}, status=201)
    
    def delete(self, request):        
        address_id = request.query_params.get('address_id')
        user_id = request.query_params.get('user_id')

        if not address_id or not user_id:
            return Response({"error": "Both address_id and user_id are required."}, status=400)

        try:
            address = Address.objects.get(id=address_id, user_id=user_id)
        except Address.DoesNotExist:
            return Response({"error": "Address not found for this user."}, status=404)

        address.delete()
        return Response({"message": "Address deleted successfully."}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_delivery_time(request):

    address_id = request.data.get('address_id')
    new_delivery_time = request.data.get('delivery_time')

    if not address_id:
        return Response({"error": "Address ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        address = Address.objects.get(pk=address_id)
    except Address.DoesNotExist:
        return Response({"error": "Address not found."}, status=status.HTTP_404_NOT_FOUND)

    if new_delivery_time:
        address.delivery_time = new_delivery_time
        address.save()
        return Response({"message": "Delivery time updated successfully."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Delivery time not provided."}, status=status.HTTP_400_BAD_REQUEST)

class ProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    """
    API endpoint for user profiles.
    """

    def get(self, request):
        """
        Retrieve a specific user profile by user_id.
        """
        user_id = request.query_params.get('user_id')
        try:
            profile = CustomUser.objects.get(id=user_id)
            serializer = ProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Update a user profile.
        """
        user_id = request.data.get('user_id')
        try:
            profile = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Extract data from request
        name = request.data.get('name', "")
        email = request.data.get('email', "")
        bio = request.data.get('bio', "")
        profile_photo = request.FILES.get('profile_photo', "")  # Get the file from request.FILES

        # Update profile fields if provided
        if name is not None:
            profile.name = name
        if email is not None:
            profile.email = email
        if bio is not None:
            profile.bio = bio
        if profile_photo is not None:
            profile.profile_photo = profile_photo


        profile.save()
        return Response({"success": "Profile updated successfully"}, status=status.HTTP_200_OK)
# views.py

from django.shortcuts import redirect
from django.views import View
from django.utils import timezone
from .models import ReferralLink

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404



class SignOutAPI(APIView):
    """
    API endpoint for user sign-out.
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        # Retrieve the user_id from query parameters
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the user object
        user = get_object_or_404(CustomUser, id=user_id)

        # Perform any additional checks if needed (e.g., verify user's identity)

        # Perform the logout action
        logout(request)

        return Response({"message": "User successfully signed out."}, status=status.HTTP_200_OK)

class DeleteAccountAPI(APIView):
    """
    API endpoint for user account deletion.
    """
    permission_classes = [IsAuthenticated]
    def delete(self, request):
        # Retrieve the user_id from query parameters
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the user object
        user = get_object_or_404(CustomUser, id=user_id)

        # Perform any additional checks if needed (e.g., verify user's identity)

        # Delete the user account
        user.delete()

        return Response({"message": "User account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


import urllib.request
import urllib.parse


import urllib.request
import urllib.parse

import random
import string
import urllib.request
import urllib.parse


import random
import string
import urllib.request
import urllib.parse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import urllib.request

import urllib.request
import urllib.parse
import random
import string


import urllib.request
import urllib.parse
import random
import string

def generate_otp(length=6):
    first_digit = random.choice(string.digits.replace('0', ''))  # 1–9
    other_digits = ''.join(random.choices(string.digits, k=length-1))
    return first_digit + other_digits



# @csrf_exempt
# def sendSMS(apikey, numbers, sender, message):
#     print(apikey, numbers, sender, message)
#     data = urllib.parse.urlencode({'apikey': apikey, 'numbers': numbers,'message': message, 'sender': sender})
#     data = data.encode('utf-8')
#     request = urllib.request.Request("https://api.textlocal.in/send/?")
#     f = urllib.request.urlopen(request,data)
#     fr = f.read()
#     return (fr)

@csrf_exempt
def sendSMS(apikey, numbers, sender, message_template):
    # Generate a 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Insert OTP into the message
    message = f"{message_template} Your OTP is {otp}."
    
    # Encode data for the API request
    data = urllib.parse.urlencode({
        'apikey': apikey,
        'numbers': numbers,
        'message': message,
        'sender': sender
    }).encode('utf-8')
    
    # Send request
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    response = urllib.request.urlopen(request, data)
    result = response.read().decode('utf-8')  # Decode bytes to string
    
    # Return both API response and OTP
    return {'response': result, 'otp': otp}

# Example usage
# Example usage
# apikey = "NGI0ZjQzMzA2MTZjNjc1NDUzNTA3MDQ1NGI1ODczNWE="
# sender_name = "FRZWLA"
# recipient_number = '917980750314'  # Make sure to pass the phone number as a string
# otp = generate_otp()
# messsage = f'Your OTP is: {otp}'
# resp = send_otp(apikey,918123456789,'Jims Autos','This is your message')
# print(resp)
@csrf_exempt
def send_sms(request):
    if request.method == 'POST':
        # Extract the parameters from the request
        apikey = "NGI0ZjQzMzA2MTZjNjc1NDUzNTA3MDQ1NGI1ODczNWE="
        sender_name = "FRZWLA"
        request_data = json.loads(request.body.decode('utf-8'))
        recipient_number = str(request_data.get('phone_number')).strip() # request_data.get('phone_number')

        # Check if the phone number already exists in CustomUser
        if CustomUser.objects.filter(phone_number=recipient_number).exists():
            return JsonResponse({'error': 'Phone number already exists','status':'400'}, status=400)

        # otp = generate_otp()
        if recipient_number in ['9892543476', '8100098024']:
            otp = '123456'  # Manually set OTP
        else:
            otp = generate_otp()  # Generate OTP normally for other numbers

        message = f'{otp} is your signin OTP for Frozenwala account. Please apply this within 2min.'

        otp_instance, created = Otp.objects.get_or_create(phone_number=recipient_number)

        # If the record already exists, update the OTP value
        if not created:
            otp_instance.otp = otp
            otp_instance.otp_created_at = timezone.now()
            otp_instance.save()
        # If the record doesn't exist, create a new OTP record
        else:
            otp_instance.otp = otp
            otp_instance.otp_created_at = timezone.now()
            otp_instance.save()
        
        if otp != '123456' :
            message = f"{otp} is your verification code."
            url = "https://unify.smsgateway.center/WAApi/send"

            payload = {'userid': 'frozenwala',
            'password': '1rUa2kFk',
            'msg': message,
            'wabaNumber': '918828881884',
            'output': 'json',
            'mobile': f"91{recipient_number}",
            'sendMethod': 'quick',
            'msgType': 'text',
            'templateName': 'login_otp'}
            files=[

            ]
            headers = {
            'Cookie': 'SERVERID=webC1'
            }

            response = requests.request("POST", url, headers=headers, data=payload, files=files)

            print(response.text)



        # print(apikey, recipient_number, sender_name, message)

        # Call the send_otp function
        # sendSMS(apikey, recipient_number, sender_name, message)
        # print(apikey, recipient_number, sender_name, message)

        # Return a JSON response
        return JsonResponse({'status': 'success'})
    else:
        # Return an error response if the request method is not POST
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def loginsend_sms(request):
    if request.method == 'POST':
        # Extract the parameters from the request
        apikey = "NGI0ZjQzMzA2MTZjNjc1NDUzNTA3MDQ1NGI1ODczNWE="
        sender_name = "FRZWLA"

        # Load the request data
        request_data = json.loads(request.body.decode('utf-8'))
        recipient_number = str(request_data.get('phone_number')).strip() # request_data.get('phone_number')

        # Validate if the phone_number exists in the CustomUser model
        if not CustomUser.objects.filter(phone_number=recipient_number).exists():
            return JsonResponse({'error': 'Phone number not found in user records','status':'400'}, status=400)

        # otp = generate_otp()
        if recipient_number in ['9892543476', '8100098024']:
            otp = '123456'  # Manually set OTP
        else:
            otp = generate_otp()  # Generate OTP normally for other numbers

        message = f'{otp} is your signin OTP for Frozenwala account. Please apply this within 2min.'

        otp_instance, created = Otp.objects.get_or_create(phone_number=recipient_number)

        # If the record already exists, update the OTP value
        if not created:
            otp_instance.otp = otp
            otp_instance.otp_created_at = timezone.now()
            otp_instance.save()
        # If the record doesn't exist, create a new OTP record
        else:
            otp_instance.otp = otp
            otp_instance.otp_created_at = timezone.now()
            otp_instance.save()

        if otp != '123456' :
            message = f"{otp} is your verification code."
            url = "https://unify.smsgateway.center/WAApi/send"

            payload = {'userid': 'frozenwala',
            'password': '1rUa2kFk',
            'msg': message,
            'wabaNumber': '918828881884',
            'output': 'json',
            'mobile': f"91{recipient_number}",
            'sendMethod': 'quick',
            'msgType': 'text',
            'templateName': 'login_otp'}
            files=[

            ]
            headers = {
            'Cookie': 'SERVERID=webC1'
            }

            response = requests.request("POST", url, headers=headers, data=payload, files=files)

            print(response.text)

        # Call the send_otp function
        # response = sendSMS(apikey, recipient_number, sender_name, message)

        # Return a JSON response
        return JsonResponse({'status': 'success'})
    else:
        # Return an error response if the request method is not POST
        return JsonResponse({'error': 'Invalid request method'}, status=400)


from .models import AddressAdmin
from .serializers import AddressAdminSerializer

class AddressAdminList(APIView):
    permission_classes = [AllowAny]  # Allow access to all users

    def get(self, request):
        addresses = AddressAdmin.objects.all()
        serializer = AddressAdminSerializer(addresses, many=True)
        return Response(serializer.data)

class AddressAdminDetail(APIView):
    permission_classes = [AllowAny]  # Allow access to all users

    def get(self, request):
        try:
            address_id = request.query_params.get('address_id')

            address = AddressAdmin.objects.get(id=address_id)
        except AddressAdmin.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AddressAdminSerializer(address)
        return Response(serializer.data)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import AddressAdmin
@login_required(login_url='backend/login')
def address_list(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    items = AddressAdmin.objects.all()
    context = {
        'items': items
    }
    return render(request, 'backend/address_list.html', context)
@login_required(login_url='backend/login')
def add_address(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    if request.method == "POST":
        newname = request.POST.get('newname')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        zip_code = request.POST.get('zip_code')
        status = 1

        # Create the address object
        AddressAdmin.objects.create(
            newname=newname,
            phone=phone,
            address=address,
            city=city,
            state=state,
            country=country,
            zip_code=zip_code,
            status=status
        )
        return redirect('back/address_list')

    return render(request, 'backend/add_address.html')
@login_required(login_url='backend/login')
def activate_address(request, address_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(AddressAdmin, id=address_id)
    item.status = '1'
    item.save()
    return redirect('back/address_list')
@login_required(login_url='backend/login')
def deactivate_address(request, address_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(AddressAdmin, id=address_id)
    item.status = '0'
    item.save()
    return redirect('back/address_list')
@login_required(login_url='backend/login')
def delete_address(request, address_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(AddressAdmin, id=address_id)
    item.delete()
    return redirect('back/address_list')
@login_required(login_url='backend/login')
def view_address(request, address_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(AddressAdmin, id=address_id)
    return render(request, 'backend/view_address.html', {'item': item})
@login_required(login_url='backend/login')
def update_address(request, address_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    edit_item = get_object_or_404(AddressAdmin, id=address_id)

    if request.method == "POST":
        edit_item.newname = request.POST.get('newname')
        edit_item.phone = request.POST.get('phone')
        edit_item.address = request.POST.get('address')
        edit_item.city = request.POST.get('city')
        edit_item.state = request.POST.get('state')
        edit_item.country = request.POST.get('country')
        edit_item.zip_code = request.POST.get('zip_code')
        edit_item.save()
        return redirect('back/address_list')

    return render(request, 'backend/edit_address.html', {'item': edit_item})
@login_required(login_url='backend/login')
def edit_address(request, address_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    sel_item = get_object_or_404(AddressAdmin, id=address_id)
    all_items = AddressAdmin.objects.all()

    context = {
        'all_items': all_items,
        'item': sel_item,
    }
    return render(request, 'backend/edit_address.html', context)

class MyRefferals(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        my_refferals = CustomUser.objects.filter(refer_by=request.user.referral_code)
        serializer = MyRefferalsSerializer(my_refferals, many=True)
        return Response({
            'status': True,
            'data': serializer.data
        })
