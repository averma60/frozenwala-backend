from django.shortcuts import render

# Create your views here.
# First, install the necessary library:
# pip install pyfcm

# Import necessary modules
from pyfcm import FCMNotification
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Notification
from ecomApp.models import CustomUser
# Initialize FCM with your server key
# push_service = FCMNotification(api_key="AAAAhkj7a5w:APA91bGXnsbD6RKIH7oDQvwl_j8mGKAlT58mww6zuLwVHPws7XBhhCHezSzy6VTtVPku2r_f-NA7TVmstWMSnNs4Ixv_r_exR2wUzSGCCeCLjYLJ7EkNRz86Q6AwmHHUgwKvmH1DHOd6")

import requests
# Define a class-based view for sending notifications
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import requests
import json

class SendNotificationAPI(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        # Parse request body
        data = json.loads(request.body.decode('utf-8'))

        # Extract data from request
        registration_id = data.get('registration_id')
        title = data.get('title')
        message = data.get('message')

        # Send the notification
        if registration_id and title and message:
            result = self.send_notification(registration_id, title, message)
            if result.status_code == 200:
                return JsonResponse({"status": "success", "message": "Notification sent successfully.", "result": result.json()})
            else:
                return JsonResponse({"status": "error", "message": "Failed to send notification.", "result": result.text}, status=result.status_code)
        else:
            return JsonResponse({"status": "error", "message": "Missing parameters."}, status=400)

    def send_notification(self, registration_id, title, message):
        url = "https://fcm.googleapis.com/fcm/send"
        # Define the message payload
        message_payload = {
            "registration_ids": [registration_id],
            "notification": {
                "title": title,
                "body": message
            }
        }

        # Define the headers with authorization key
        headers = {
            "Authorization": "key=AAAAhkj7a5w:APA91bGXnsbD6RKIH7oDQvwl_j8mGKAlT58mww6zuLwVHPws7XBhhCHezSzy6VTtVPku2r_f-NA7TVmstWMSnNs4Ixv_r_exR2wUzSGCCeCLjYLJ7EkNRz86Q6AwmHHUgwKvmH1DHOd6",  # Replace YOUR_SERVER_KEY with your actual server key
            "Content-Type": "application/json"
        }


        # Send the notification
        result = requests.post(url, data=json.dumps(message_payload), headers=headers)
        if result.status_code == 200:
            # Get user_id from CustomUser model
            try:
                user_id = CustomUser.objects.get(registration_id=registration_id)
            except CustomUser.DoesNotExist:
                user_id = None
            # Create a Notification object with status 0 (unread) and user_id
            notification = Notification.objects.create(title=title, message=message, status=0, user_id=user_id)


        return result
import pytz
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from django.http import JsonResponse
from django.views import View
from .models import Notification
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class GetNotificationsAPI(View):
    permission_classes = [IsAuthenticated]


    def get(self, request):
        # Get user_id from query parameters
        user_id = request.GET.get('user_id')

        if user_id is None:
            return JsonResponse({"error": "Missing user_id parameter"}, status=400)

        # Retrieve notifications for the given user_id
        notifications = Notification.objects.filter(user_id=user_id).values()

        # Serialize notifications as a list of dictionaries
        notifications_list = list(notifications)
        # Convert created_at datetime format
        for notification in notifications_list:
            created_at = notification['created_at']
            # Convert UTC to local timezone (Asia/Kolkata)
            local_tz = pytz.timezone('Asia/Kolkata')
            local_created_at = created_at.astimezone(local_tz)
            formatted_created_at = local_created_at.strftime("%d %b at %I:%M %p")
            notification['created_at'] = formatted_created_at
        return JsonResponse({"notifications": notifications_list})


class GetUnreadNotificationsCountAPI(View):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Count notifications with status 0 (unread)
        user_id = request.GET.get('user_id')

        if user_id is None:
            return JsonResponse({"error": "Missing user_id parameter"}, status=400)

        # Count notifications with status 0 (unread) for the specified user_id
        unread_count = Notification.objects.filter(user_id=user_id, status=0).count()

        return JsonResponse({"unread_count": unread_count})

class MarkNotificationsAsReadAPI(View):
    permission_classes = [IsAuthenticated]




    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @csrf_exempt
    def post(self, request):
        # Parse request body as JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        # Get user_id from request data
        user_id = data.get('user_id')

        if user_id is None:
            return JsonResponse({"error": "Missing user_id parameter"}, status=400)

        # Update status of notifications for the specified user_id to 1 (read)
        notifications_updated = Notification.objects.filter(user_id=user_id).update(status=1)

        return JsonResponse({"message": f"{notifications_updated} notifications marked as read"})