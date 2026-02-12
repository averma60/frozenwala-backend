from django.db.models import Q, Sum, F
from django.shortcuts import render, redirect
from cart.models import CartCoupon

# Create your views here.
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, generics
from .models import  DeliverySlot, Order, PaymentOption
from .serializers import OrderSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ecomApp.models import CustomUser
from ecomApp.models import Catagory
from ecomApp.models import Product
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from walet.models import PurchaseBenefit, WalletTransaction
from registration.models import AddressAdmin
import random
from django.urls import reverse
from django.utils import timezone as django_timezone

from menu_management.models import Item


from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.http import JsonResponse, HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from weasyprint import HTML

import pytz
from pytz import timezone
from .models import Order

from django.http import JsonResponse, HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from django.http import JsonResponse, HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import secrets

from django.contrib import messages
import razorpay
from django.conf import settings
from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from notification.views import SendNotificationAPI  # Import the SendNotificationAPI class

from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from django.http import HttpResponse
# from django.utils.timezone import localtime

from datetime import datetime, timedelta

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from pathlib import Path
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

from walet.views import calculate_purchase_benefit  
from walet.models import Walet
from ecomApp.models import Stock
import random
import string
from cart.models import Cart
from uuid import uuid4  # Import UUID generator

from rest_framework import generics
from rest_framework.response import Response
from .models import Order
from .serializers import GroupedOrderSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer, PaymentOptionSerializer, DeliverySlotSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from django.db.models import Max, Q
from datetime import date
from rest_framework import serializers
from .models import CustomUser
from influencer.models import InfluencerRecord
from django.utils.timezone import now

india_tz = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(india_tz)

from django.utils import timezone as dtz
from datetime import datetime, timedelta

from pytz import timezone
from reportlab.platypus import *
from django.http import HttpResponse, JsonResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER

from .utils import update_stock, sale_sync

#for noww...
class OrderView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required(login_url='backend/login')
def orderlist(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    # Fetch all orders
    orders = Order.objects.all().order_by('-created_at')

    status = request.GET.get('status')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    if status:
        orders = orders.filter(status=status)

    if from_date:
        from_dt = dtz.make_aware(
            datetime.strptime(from_date, "%Y-%m-%d")
        )
        orders = orders.filter(created_at__gte=from_dt)

    if to_date:
        to_dt = dtz.make_aware(
            datetime.strptime(to_date, "%Y-%m-%d")
        ) + timedelta(days=1)
        orders = orders.filter(created_at__lte=to_dt)

    # Create a dictionary to store orders grouped by their order_id
    orders_dict = {}
    local_tz = pytz.timezone('Asia/Kolkata')
    for order in orders_dict.values():
        order.created_at = order.created_at.astimezone(local_tz)

    # Iterate over orders and group them by their order_id
    for order in orders:
        # if order.payment_id:
        if order.order_id not in orders_dict:
            orders_dict[order.order_id] = order
    # Extract the first element of each group
    first_elements = [order for order in orders_dict.values()][:10]
    sec_elements = [order for order in orders_dict.values()]
    
    for o in sec_elements:
        if o.user_id and o.user_id.influencer_records and o.user_id.influencer_records.filter(
        end_date__gte=now()
    ).exists():
            o.influencer_code = o.user_id.referral_code

    # Pass the first elements to the template context
    context = {
        'ordform': first_elements,
        'new': sec_elements,
        'selected_status': status,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, 'backend/orderlist.html', context)
@login_required(login_url='backend/login')
def confirmorderlist(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    ordercon=Order.objects.filter(Q(status=2) | Q(status=3) | Q(status=4))
    context={
        'ordercon':ordercon

    }
    return render(request,'backend/confirmorderlist.html',context)
@login_required(login_url='backend/login')
@login_required(login_url='backend/login')
def view_item(request, myid):
    sel_ordform = Order.objects.filter(order_id=myid)
    total_quantity = sel_ordform.aggregate(total=Sum('quantity'))['total'] or 0
    ord = Order.objects.all()
    if not request.user.is_staff:
        return redirect('backend/login')

    total_price = 0
    total_saved = 0
    total_gst_amount = 0

    for item in sel_ordform:
        gst_amount = (item.product_id.item_new_price * item.quantity) * item.gst_rate / 100
        item.gst_amount = gst_amount
        total_price += item.product_id.item_old_price * item.quantity
        total_saved += (item.product_id.item_old_price - item.product_id.item_new_price) * item.quantity
        total_gst_amount += gst_amount

    first_order = sel_ordform.first()
    if first_order.delivery_price:
        total_price += int(first_order.delivery_price)
    if first_order.dicounted_price:
        total_saved += int(first_order.dicounted_price)

    taxable_amount = int(first_order.total_price) - total_gst_amount

    context = {
        'ordform': ord,
        'sel_ordform': sel_ordform,
        'total_quantity': total_quantity,
        'total_price': total_price,
        'total_saved': total_saved,
        'total_gst_amount': total_gst_amount,
        'taxable_amount': taxable_amount,
        'cgst': round(total_gst_amount / 2, 2),
        'sgst': round(total_gst_amount / 2, 2),
    }
    return render(request, 'backend/orderview.html', context)

@login_required(login_url='backend/login')
def suspend_user(request, catagory_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    order = get_object_or_404(Order, id=catagory_id)
    order.status = 2  # Change status to "confirm"
    order.save()
    return redirect('orderapp:activate_catagory', catagory_id=catagory_id)
@login_required(login_url='backend/login')
def cancel(request, catagory_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    order = get_object_or_404(Order, id=catagory_id)
    order.status = 5  # Change status to "cancel"
    order.save()
    return redirect('orderapp:returnrequest', catagory_id=catagory_id)
@login_required(login_url='backend/login')
def activate_catagory(request, catagory_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    order = get_object_or_404(Order, id=catagory_id)
    order.status = 3  # Change status to "pickup"
    order.save()
    return redirect('orderapp:deactivate_catagory', catagory_id=catagory_id)
@login_required(login_url='backend/login')
def deactivate_catagory(request, catagory_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    order = get_object_or_404(Order, id=catagory_id)
    order.status = 4  # Change status to "delivered"
    order.save()
    return redirect('orderapp:deliver', catagory_id=catagory_id)
@login_required(login_url='backend/login')
def deliver(request, catagory_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    order = get_object_or_404(Order, id=catagory_id)
    order.status = 4  # Change status to "delivered"
    order.save()
    return redirect('orderapp:index')  # Redirect to main page after delivery
@login_required(login_url='backend/login')
def returnrequest(request, catagory_id):
    if not request.user.is_staff:
        return redirect('backend/login')

    order = get_object_or_404(Order, id=catagory_id)
    order.status = 6  # Change status to "return request"
    order.save()
    return redirect('orderapp/returnaccepted', catagory_id=catagory_id)
@login_required(login_url='backend/login')
def returnaccepted(request, catagory_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    order = get_object_or_404(Order, id=catagory_id)
    order.status = 7  # Change status to "return accepted"
    order.save()
    return redirect('orderapp')  # Redi

def generate_random_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def update_status(request, id):
    if not request.user.is_staff:
        return redirect('backend/login')
    
    if request.method == 'POST':
        now = django_timezone.now()
        selected_status_str = request.POST.get('selected_status')
        cancel_reason = request.POST.get('cancel_reason', '')
        try:
            selected_status = int(selected_status_str)
        except (TypeError, ValueError):
            # Handle the case where selected_status_str is not a valid integer
            messages.error(request, 'Invalid status value!')
            # return redirect(request.META.get('HTTP_REFERER', 'fallback_url'))
            return redirect('orderapp')  # Redirect to order list page on error

        order = Order.objects.get(id=id)

        # Update status for each order
        order_id = order.order_id

        # Retrieve all orders with the same order_id
        orders_to_update = Order.objects.filter(order_id=order_id)

        # Update status for each order
        for order_id in orders_to_update:
            order_id.status = selected_status

            if selected_status == 2 and not order_id.confirmed_at:
                order_id.confirmed_at = now
            elif selected_status == 3 and not order_id.picked_up_at:
                order_id.picked_up_at = now
            elif selected_status == 4 and not order_id.delivered_at:
                order_id.delivered_at = now
                order_id.delivery_slot -= 1
                order_id.delivery_slot.save()
            elif selected_status == 5 and cancel_reason:
                order_id.cancelled_at = now
                order_id.cancellation_reason = cancel_reason
                order_id.delivery_slot -= 1
                order_id.delivery_slot.save()

            order_id.save()
        # Send notification to the user if the status has changed
        if selected_status != 1:
            uid = None
            if order.user_id:
                uid = CustomUser.objects.get(id=order.user_id.id)
            registration_id = uid.registration_id if uid and uid.registration_id else 0
            if selected_status == 2:
                title = "Order Confirmed"
                message = "Your order has been confirmed."
                if registration_id:
                    SendNotificationAPI().send_notification(registration_id, title, message)

            elif selected_status == 3:
                title = "Order Picked Up"
                message = "Congrats! Your order has been picked up from FrozenWala Store Ruby Tower Jogeswari West, Mumbai, Maharashtra, India, 400102."
                if registration_id:
                    SendNotificationAPI().send_notification(registration_id, title, message)

            elif selected_status == 4:
                title = "Order Delivered"
                message = "Your order has been delivered successfully."
                if registration_id:
                    SendNotificationAPI().send_notification(registration_id, title, message)

            elif selected_status == 5:
                title = "Order Canceled"
                message = "Sorry! Your order has been canceled due to some internal reason."
                if registration_id:
                    SendNotificationAPI().send_notification(registration_id, title, message)

            elif selected_status == 7:
                title = "Return Request Accepted"
                message = "Your return request has been accepted by the store."
                if registration_id:
                    SendNotificationAPI().send_notification(registration_id, title, message)

        messages.success(request, 'Status updated successfully!')

    return redirect(
        reverse('orderapp/view_item', args=[order.order_id])
    )


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_SECRET_KEY))

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    if request.method == 'POST':
        user_id = request.data.get('user_id')
        total_amount = request.data.get('total_amount')
        dicounted_price = request.data.get('discounted_price', "")
        previous_price = request.data.get('previous_price')
        delivery_price = request.data.get('delivery_price', "")
        walet_value = request.data.get('walet_value',0)
        pick_up=request.data.get('pick_up')
        coupon_code = request.data.get('coupon_code', "")
        coupon_value = request.data.get('coupon_value')
        newname = request.data.get('newname', "")
        phone = request.data.get('phone', "")
        address = request.data.get('address', "Pick UP")
        city = request.data.get('city', "")
        state = request.data.get('state', "")
        country = request.data.get('country', "")
        zip_code = request.data.get('zip_code', "")
        delivery_time = request.data.get('delivery_time', ""),
        influencer_code = request.data.get('influencer_code', "")
        payment_option = request.data.get('payment_option', "")
        delivery_slot = request.data.get('delivery_slot', "")

        if not payment_option:
            return JsonResponse({'message': 'Please select a payment option','status':'400'}, status=400)
        
        payment_option = PaymentOption.objects.filter(id=payment_option).first()
        
        if not payment_option:
            return JsonResponse({'message': 'Invalid payment option selected','status':'400'}, status=400)

        user = get_object_or_404(CustomUser, id=user_id)
        if not influencer_code:
            influencer_code = user.influencer_code if hasattr(user, 'influencer_code') else ""

        try:
            print(user_id)
            # Create order in Razorpay
            order_amount = int(float(total_amount) * 100)  # Amount in paisa
            order_currency = 'INR'
            order_receipt = 'order_receipt_' + str(user_id)  # You can set it as per your requirement
            razorpay_order = razorpay_client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt))
            razorpay_order_id = razorpay_order['id']
            # Get cart items for the user
            cart_items = Cart.objects.filter(u_id=user_id, status='Active')
            # max_benefit_percentage, wallet_value = calculate_purchase_benefit(user_id, total_amount)

            #new
            for cart_item in cart_items:
                # Get the stock for the item
                stock = get_object_or_404(Stock, item_id=cart_item.product_id)

                # Check if the stock is sufficient
                if stock.openingstock < cart_item.quantity:
                    return JsonResponse({'message': f"Stock is not available for {cart_item.product_id.title}",'status':'400'},
                                        status=400)
            
            try:
                walet_value = int(float(walet_value))
            except:
                walet_value = 0

            # if walet_value:
            #     user = CustomUser.objects.get(id=user_id)
            #     user_walet = int(user.walet)
            #     if walet_value > user_walet:
            #         walet_value = 0

            if not newname:
                newname = user.name
            if not phone:
                phone = user.phone_number

            cgst_amount = 0
            sgst_amount = 0
            total_gst = 0
            gst_rate = 0
            gstn = ""

            address_admin = AddressAdmin.objects.first()
            if address_admin:
                gstn = address_admin.gstn
                gst_rate = address_admin.gst_rate
                gst_amount = round((float(total_amount) * gst_rate) / (100 + gst_rate), 2)
                cgst_amount = round(gst_amount / 2, 2)
                sgst_amount = round(gst_amount - cgst_amount, 2)
                total_gst = round(gst_amount, 2)

            if delivery_slot:
                delivery_slot = DeliverySlot.objects.filter(id=delivery_slot).first()

            order_items = []

            # Create orders for each item in the cart
            for cart_item in cart_items:
                order = Order.objects.create(
                    order_id=razorpay_order_id,
                    user_id=CustomUser.objects.get(id=user_id),
                    product_id=cart_item.product_id,
                    payment_id='',  # Leave payment_id empty initially
                    couponcode=coupon_code,
                    walet_value=walet_value,
                    influencer_code=influencer_code,
                    # percentage_benefit=max_benefit_percentage,  # Save the percentage benefit
                    pick_up=pick_up,
                    status=1,  # Set initial status
                    quantity=cart_item.quantity,
                    price="{:.2f}".format(cart_item.price),
                    total_price=total_amount,
                    previous_price=previous_price,
                    dicounted_price=dicounted_price,
                    delivery_price=delivery_price,
                    signature='',  # Leave signature empty initially
                    newname=newname,
                    phone=phone,
                    address=address,
                    city=city,
                    state=state,
                    country=country,
                    zip_code=zip_code,
                    delivery_time=delivery_time,
                    payment_option=payment_option,
                    gstn=gstn,
                    gst_rate=gst_rate,
                    cgst_amount=cgst_amount,
                    sgst_amount=sgst_amount,
                    total_gst=total_gst
                )

                purchase_benefit_amount = Decimal('0.00')
                purchase_benefit = (
                    PurchaseBenefit.objects
                    .filter(price__lte=order.price, status='1')
                    .order_by('price')
                    .last()
                )
                if purchase_benefit:
                    order_price = Decimal(str(order.price))
                    purchase_benefit_amount = (
                        order_price * purchase_benefit.benefit_percentage
                    ) / Decimal('100')

                    order.purchase_benefit = purchase_benefit_amount
                    order.save()

                if delivery_slot and delivery_slot.is_active and delivery_slot.booked_orders < delivery_slot.max_orders:
                    order.delivery_slot = delivery_slot
                    order.save()

                if payment_option and payment_option.code == 'cod':
                    update_stock(cart_item.product_id.id, cart_item.quantity)

                order_items.append({
                    "item_id": cart_item.product_id.id,
                    "quantity": cart_item.quantity,
                    "price_per_unit": cart_item.product_id.item_new_price,
                    "total_cost": cart_item.product_id.item_new_price*cart_item.quantity,
                    "purchase_price": cart_item.product_id.item_new_price,
                    "tax_id": 0,
                    "tax_amt": 0
                })

            if order and len(order_items) > 0:
                sale_sync(order, user_id, order_items)

            # if order and order.purchase_benefit:
            #     user.walet += float(order.purchase_benefit)
            #     user.save()

            #     WalletTransaction.objects.create(
            #         user_id=user_id,
            #         transaction_id=order.order_id,  
            #         credit_bal=order.purchase_benefit,
            #         debit_bal=0,
            #         opening_bal=0,
            #         closing_bal=order.purchase_benefit,
            #         transaction_type="Purchase Benefit",
            #     )

            if order.delivery_slot and delivery_slot:
                delivery_slot.booked_orders += 1
                delivery_slot.save()

            # if order:
            #     order_price = Decimal(str(order.price))
            #     reffered_by = CustomUser.objects.filter(referral_code=user.refer_by).first()
            #     if reffered_by:
            #         influencer_record = InfluencerRecord.objects.filter(user=reffered_by, end_date__gte=now()).first()
            #         if influencer_record and influencer_record.benefit_percentage:
            #             benefit_amount = (order_price * influencer_record.benefit_percentage) / Decimal('100')
            #             reffered_by.walet += float(benefit_amount)
            #             reffered_by.save()
            #             WalletTransaction.objects.create(
            #                 user_id=reffered_by.id,
            #                 transaction_id=order.order_id,  
            #                 credit_bal=benefit_amount,
            #                 debit_bal=0,
            #                 opening_bal=0,
            #                 closing_bal=benefit_amount,
            #                 transaction_type="Influencer Benefit",
            #             )

            # for cart_item in cart_items:
            #     stock = get_object_or_404(Stock, item_id=cart_item.product_id)
            #     stock.openingstock -= cart_item.quantity
            #     stock.save()

            cart_items.delete()

            if walet_value:
                user = CustomUser.objects.get(id=user_id)
                if user and user.walet >= walet_value:
                    user.walet = int(user.walet) - walet_value
                    user.save()

            return JsonResponse({'razorpay_order_id': razorpay_order_id, 'couponcode': coupon_code, 'total_price': total_amount,'status':'success'}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return HttpResponseServerError("Method Not Allowed")

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    if request.method == 'POST':
        try:
            razorpay_payment_id = request.data.get('razorpay_payment_id')
            razorpay_order_id = request.data.get('razorpay_order_id')
            razorpay_signature = request.data.get('razorpay_signature')

            # Verify payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Update order status or save payment details to your database
            orders = Order.objects.filter(order_id=razorpay_order_id)

            order_items = []

            for order in orders:
                # Generate a unique order item ID
                order_item_id = str(uuid4())
                order.payment_id = razorpay_payment_id
                order.signature = razorpay_signature
                order.status = 1  # Set status to success
                order.order_item_id = order_item_id
                order.save()

                # stock = Stock.objects.select_for_update().filter(item_id=order.product_id).first()
                # stock.openingstock -= 1
                # stock.save()
                product_id = order.product_id
                quantity = order.quantity
                # stock = Stock.objects.select_for_update().get(item_id=product_id)
                # stock = Stock.objects.get(item_id=product_id)

                # stock.openingstock -= quantity
                # stock.save()
                update_stock(product_id.id, quantity)

                order_items.append({
                    "item_id": product_id.id,
                    "quantity": quantity,
                    "price_per_unit": product_id.item_new_price,
                    "total_cost": product_id.item_new_price*quantity,
                    "purchase_price": product_id.item_new_price,
                    "tax_id": 0,
                    "tax_amt": 0
                })

            first_order = orders.first()
            user_id = first_order.user_id.id
            total_amount = first_order.total_price
            order_id = first_order.id
            print(user_id, total_amount)
            max_benefit_percentage, wallet_value = calculate_purchase_benefit(user_id, total_amount)
            # Get the user_id from the first order

            cart_items = Cart.objects.filter(u_id=user_id, status='Active')
            cart_items.delete()
            cart_coupon = CartCoupon.objects.filter(user_id=user_id)
            if cart_coupon:
                cart_coupon.delete()
            cart_walet=Walet.objects.filter(user_id=user_id)
            if cart_walet:
                cart_walet.delete()
                
            #new
            walet_value = int(first_order.walet_value or 0)
            if walet_value > 0:
                user = CustomUser.objects.get(id=user_id)
                user_walet = opening_bal = int( user.walet)
                curr_wallet= int(first_order.walet_value)
                user_walet -= curr_wallet
                user.walet = user_walet
                user.save()

                WalletTransaction.objects.create(
                    user_id=user_id,
                    transaction_id=order_id,  
                    opening_bal=opening_bal,
                    credit_bal=0,
                    debit_bal=curr_wallet,
                    closing_bal=user_walet,
                    transaction_type="Order Payment",
                    created_at=current_time,
                    updated_at=current_time
                )                

            alluser = CustomUser.objects.filter(id=user_id)
            userss = alluser.first()
            
            if first_order and first_order.purchase_benefit:
                user = CustomUser.objects.get(id=user_id)
                user.walet += float(first_order.purchase_benefit)
                user.save()

                WalletTransaction.objects.create(
                    user_id=user_id,
                    transaction_id=first_order.order_id,  
                    credit_bal=first_order.purchase_benefit,
                    debit_bal=0,
                    opening_bal=0,
                    closing_bal=first_order.purchase_benefit,
                    transaction_type="Purchase Benefit",
                )
            
            if first_order:
                user = CustomUser.objects.get(id=user_id)
                order_price = Decimal(str(first_order.price))
                reffered_by = CustomUser.objects.filter(referral_code=user.refer_by).first()
                if reffered_by:
                    influencer_record = InfluencerRecord.objects.filter(user=reffered_by, end_date__gte=now()).first()
                    if influencer_record and influencer_record.benefit_percentage:
                        benefit_amount = (order_price * influencer_record.benefit_percentage) / Decimal('100')
                        reffered_by.walet += float(benefit_amount)
                        reffered_by.save()
                        WalletTransaction.objects.create(
                            user_id=reffered_by.id,
                            transaction_id=first_order.order_id,  
                            credit_bal=benefit_amount,
                            debit_bal=0,
                            opening_bal=0,
                            closing_bal=benefit_amount,
                            transaction_type="Influencer Benefit",
                        )

            if first_order and len(order_items) > 0:
                sale_sync(first_order, user_id, order_items)

            # Get the registration_id of the user
            registration_id = userss.registration_id
            title = "Order Placed Successfully!"
            message = "Your order has been successfully placed at FrozenwalaStore."
            if registration_id:
                SendNotificationAPI().send_notification(registration_id, title, message)

            return JsonResponse({'message': 'Payment successful'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        else:
            return HttpResponseServerError("Method Not Allowed")

class OrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('user_id')

        # Fetch all orders for the given user where payment_id is not null
        orders = Order.objects.filter(user_id=user_id)

        # Group orders by order_id, keeping the latest order with the highest created_at timestamp
        unique_orders = orders.values('order_id').annotate(
            latest_created_at=Max('created_at'),
            total_price=Max('total_price'),
            status=Max('status'),
            payment_id=Max('payment_id')
        )

        # Construct list of dictionaries for each unique order
        order_list = []
        local_tz = pytz.timezone('Asia/Kolkata')
        for order in unique_orders:
            # if order['payment_id']:
            # Check if payment_id is not empty or null
            # Convert UTC to local timezone
            local_created_at = order['latest_created_at'].astimezone(local_tz)
            order_dict = {
                'order_id': order['order_id'],
                'created_at': local_created_at.strftime("%d-%m-%Y %I:%M:%S %p"),
                'total_price': order['total_price'],
                'status': order['status']
            }
            order_list.append(order_dict)

        # Sort the order list in descending order based on created_at
        sorted_order_list = sorted(order_list, key=lambda x: x['created_at'], reverse=True)

        return Response(sorted_order_list)

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class OrderDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the order_id from query parameters
            order_id = request.query_params.get('order_id')

            # Check if order_id parameter is provided
            if order_id is None:
                return Response({"error": "order_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve all orders for the specified order_id
            orders = Order.objects.filter(order_id=order_id)

            # If no orders found for the given order_id
            if not orders:
                return Response({"error": "No orders found for the given order_id"}, status=status.HTTP_404_NOT_FOUND)

            # Initialize lists to store product details and order details
            products = []
            order_details = []

            company_address = AddressAdmin.objects.first()
            seller_address = {}
            if company_address:
                seller_address = {
                    "newname": company_address.newname,
                    "phone": company_address.phone,
                    "address": company_address.address,
                    "city": company_address.city,
                    "state": company_address.state,
                    "country": company_address.country,
                    "zip_code": company_address.zip_code,
                    "gstn": company_address.gstn,
                }

            # Iterate over orders
            for order in orders:
                # Retrieve product details for all orders
                gst_price = (order.product_id.item_new_price * order.quantity) * order.gst_rate / 100
                product = {
                    "product_id": order.product_id.id,
                    "name": order.product_id.title,
                    "description": order.product_id.description,
                    # "item_photo": order.product_id.item_photo.url,
                    "item_quantity": order.quantity,
                    # "item_measurement": order.product_id.item_measurement,
                    "item_old_price": order.product_id.item_old_price,
                    "discount": order.product_id.discount,
                    "item_new_price": order.product_id.item_new_price,
                    "product_order_price":order.product_id.item_new_price*order.quantity,
                    "status": order.product_id.status,
                    "category": order.product_id.category.name,
                    "created_at": order.product_id.created_at,
                    "deal_of_the_day": order.product_id.deal_of_the_day,
                    "recommended": order.product_id.recommended,
                    "most_popular": order.product_id.most_popular,
                    "gst_price": gst_price,
                }
                products.append(product)

                # Append full order details for the first order only
                if not order_details:  # Ensures only the first order details are added
                    order_detail = {
                        "id": order.id+1000,
                        "order_id": order.order_id,
                        "order_date": order.created_at.strftime("%-d/%-m/%Y"),
                        "status": order.status,
                        "total_price": order.total_price,
                        "discounted_price": order.dicounted_price,
                        "previous_price": order.previous_price,
                        "delivery_price":order.delivery_price,
                        "coupon_code":order.couponcode,
                        # "item_price": order.price,
                        # "created_at": order.created_at,
                        "newname": order.newname,
                        "phone": order.phone,
                        "address": order.address,
                        "city": order.city,
                        "state": order.state,
                        "country": order.country,
                        "zip_code": order.zip_code,
                        "delivery_time": order.delivery_time,
                        "wallet": order.walet_value,
                        "cgst_amount": order.cgst_amount,
                        "sgst_amount": order.sgst_amount,
                        "total_gst": order.total_gst,
                        "gstn": order.gstn,
                        "gst_rate": order.gst_rate,
                        "seller_address": seller_address,
                        "cancellation_reason": order.cancellation_reason,
                        "placed_at": order.created_at,
                        "confirmed_at": order.confirmed_at,
                        "picked_up_at": order.picked_up_at,
                        "delivered_at": order.delivered_at,
                        "cancelled_at": order.cancelled_at,
                        "delivery_slot": (
                            f"{order.delivery_slot.start_time.strftime('%I:%M %p')} - "
                            f"{order.delivery_slot.end_time.strftime('%I:%M %p')}"
                            if order.delivery_slot else None
                        ),

                        # "order_item_id": order.order_item_id
                    }
                    order_details.append(order_detail)

            return Response({"order_details": order_details, "products": products}, status=status.HTTP_200_OK)



        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

def generate_invoice(request):
    order_id = request.GET.get('order_id')

    if not order_id:
        return JsonResponse({"error": "Order ID is required"}, status=400)

    order_items = Order.objects.filter(order_id=order_id)

    if not order_items.exists():
        return JsonResponse({"error": "Order not found"}, status=404)

    order = order_items.first()
    
    wallet_used = float(order.walet_value or 0)
    coupon_code = order.couponcode or None

    local_tz = timezone("Asia/Kolkata")
    order_date = order.created_at.astimezone(local_tz).strftime("%d %B %Y, %I:%M %p")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=invoice_{order_id}.pdf"

    # Create PDF document
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    # Define custom styles
    styles = getSampleStyleSheet()
    
    # Title style
    styles.add(ParagraphStyle(
        name='InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    ))
    
    # Invoice number style
    styles.add(ParagraphStyle(
        name='InvoiceNumber',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=20
    ))
    
    # Section header style
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold',
        spaceAfter=6
    ))
    
    # Normal text style
    styles.add(ParagraphStyle(
        name='InfoText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=4
    ))
    
    # Gray text style
    styles.add(ParagraphStyle(
        name='GrayText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=4
    ))
    
    # Footer style
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#95a5a6'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    ))

    # Container for elements
    elements = []

    # ============ HEADER WITH LOGO ============
    logo_path = Path("ecomApp/static/assets/images/FrozenWala-Logo.jpeg")
    if logo_path.exists():
        logo = Image(str(logo_path), width=120, height=60)
        elements.append(logo)
        elements.append(Spacer(1, 0.2*inch))

    # Invoice title
    title = Paragraph("INVOICE", styles['InvoiceTitle'])
    elements.append(title)
    
    # Invoice/Order number
    inv_num = Paragraph(f"Order No: {order.id}", styles['InvoiceNumber'])
    elements.append(inv_num)
    
    elements.append(Spacer(1, 0.2*inch))

    # ============ SELLER AND CUSTOMER INFO ============
    # Get seller details
    try:
        address = AddressAdmin.objects.first()
        seller_name = address.newname if address else "Frozenwala"
        seller_addr = address.address if address else "Ruby Tower, Jogeshwari West, Mumbai"
        seller_gst = address.gstn if address and address.gstn else "N/A"
    except:
        seller_name = "Frozenwala"
        seller_addr = "Ruby Tower, Jogeshwari West, Mumbai"
        seller_gst = "N/A"

    # Create info section table
    info_data = []
    
    # Headers
    seller_header = Paragraph("<b>Seller Details</b>", styles['SectionHeader'])
    customer_header = Paragraph("<b>Bill To</b>", styles['SectionHeader'])
    info_data.append([seller_header, customer_header])
    
    # Seller details
    seller_info = [
        Paragraph(f"<b>{seller_name}</b>", styles['InfoText']),
        Paragraph(seller_addr, styles['GrayText']),
        Paragraph(f"GSTIN: {seller_gst}", styles['GrayText']),
        Paragraph(f"Order Date: {order_date}", styles['GrayText'])
    ]
    
    # Customer details
    customer_info = [
        Paragraph(f"<b>{order.newname or 'Customer'}</b>", styles['InfoText']),
        Paragraph(order.address or "", styles['GrayText']),
        Paragraph(f"{order.city}, {order.state}, {order.country}", styles['GrayText']),
        Paragraph(f"Phone: {order.phone}", styles['GrayText'])
    ]
    
    # Add to data with proper alignment
    max_lines = max(len(seller_info), len(customer_info))
    for i in range(max_lines):
        seller_cell = seller_info[i] if i < len(seller_info) else ""
        customer_cell = customer_info[i] if i < len(customer_info) else ""
        info_data.append([seller_cell, customer_cell])
    
    # Create info table
    info_table = Table(info_data, colWidths=[3.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))

    # ============ ITEMS TABLE ============
    # Section title
    title = Paragraph("<b>Bill Details</b>", styles['SectionHeader'])
    elements.append(title)
    elements.append(Spacer(1, 0.1*inch))
    
    # Table data
    data = []
    
    # Header row
    headers = ['Item', 'Qty', 'Rate (Rs.)', 'Total (Rs.)']
    data.append([Paragraph(f"<b>{h}</b>", styles['Normal']) for h in headers])
    
    # Item rows
    for item in order_items:
        raw_title = item.product_id.title if item.product_id else "N/A"
        title_para = Paragraph(raw_title, styles['Normal'])
        qty = item.quantity or 0
        rate = float(item.product_id.item_new_price or 0)
        total = rate * qty

        row = [
            title_para,
            Paragraph(str(qty), styles['Normal']),
            Paragraph(f"Rs.{rate:.2f}", styles['Normal']),
            Paragraph(f"Rs.{total:.2f}", styles['Normal'])
        ]
        data.append(row)
    
    # Create items table
    items_table = Table(data, colWidths=[3.8*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    
    # Table style
    table_style = TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        
        # Alignment
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        
        # Borders
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#3498db')),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ])
    
    items_table.setStyle(table_style)
    elements.append(items_table)
    elements.append(Spacer(1, 0.2*inch))

    # ============ FINANCIAL SUMMARY ============
    item_total = float(order.previous_price or 0)
    delivery = float(order.delivery_price or 0)
    grand_total = float(order.total_price or 0)

    gst_rate = order.gst_rate or 0
    cgst = order.cgst_amount or 0
    sgst = order.sgst_amount or 0
    total_gst = order.total_gst or 0

    # Build summary data
    summary_data = []
    summary_data.append(['Item Total (incl GST)', f"Rs.{item_total:.2f}"])
    
    if total_gst:
        summary_data.append([f'CGST ({gst_rate/2}%)', f"Rs.{cgst:.2f}"])
        summary_data.append([f'SGST ({gst_rate/2}%)', f"Rs.{sgst:.2f}"])
        summary_data.append(['Total GST', f"Rs.{total_gst:.2f}"])
    
    if wallet_used:
        summary_data.append(['Wallet Used', f"- Rs.{wallet_used:.2f}"])
    
    summary_data.append(['Delivery Fee', f"Rs.{delivery:.2f}"])
    
    if coupon_code:
        summary_data.append(['Coupon Applied', f"{coupon_code}"])
    
    # Convert to Paragraphs
    summary_table_data = []
    for label, value in summary_data:
        summary_table_data.append([
            Paragraph(label, styles['GrayText']),
            Paragraph(value, styles['InfoText'])
        ])
    
    # Create summary table
    summary_table = Table(summary_table_data, colWidths=[4.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.1*inch))
    
    # Grand total
    total_data = [[
        Paragraph('<b>Grand Total</b>', styles['Normal']),
        Paragraph(f"<b>Rs.{grand_total:.2f}</b>", styles['Normal'])
    ]]
    
    total_table = Table(total_data, colWidths=[4.5*inch, 2.5*inch])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(total_table)
    elements.append(Spacer(1, 0.3*inch))

    # ============ FOOTER ============
    footer_text = Paragraph(
        "This is a system-generated invoice. Prices are inclusive of applicable taxes.",
        styles['Footer']
    )
    elements.append(footer_text)

    # Build PDF
    doc.build(elements)
    return response

class PaymentOptionListCreateView(generics.ListCreateAPIView):
    queryset = PaymentOption.objects.filter(is_active=True)
    serializer_class = PaymentOptionSerializer

class DownloadOrderInvoice(APIView):
    def get(self, request, order_id):
        orders = Order.objects.filter(order_id=order_id)
        if orders.count() == 0:
            return HttpResponse("Order not found", status=404)

        order = orders[0]
        order_data = {}
        products = []
        address = AddressAdmin.objects.first()
        if address:
            order_data["shop_name"] = address.newname or "-"
            order_data["shop_address"] = address.address or "-"
            order_data["shop_city"] = address.city or "-"
            order_data["shop_state"] = address.state or "-"
            order_data["shop_country"] = address.country or "-"
            order_data["shop_phone"] = address.phone or "-"
            order_data["shop_gstn"] = address.gstn or "-"

        order_data["invoice_number"] = order.id+1000
        order_data["order_date"] = order.created_at.strftime("%-d/%-m/%Y")
        order_data["customer_name"] = order.newname
        order_data["customer_phone"] = order.phone
        order_data["is_pickup"] = True if order.pick_up == "1" else False
        order_data["delivery_slot"] = (
                                        f"{order.delivery_slot.start_time.strftime('%I:%M %p')} - "
                                        f"{order.delivery_slot.end_time.strftime('%I:%M %p')}"
                                        if order.delivery_slot else None
                                    )
        
        total_quantity = 0
        total_price = 0
        coupon_discount = 0
        total_saved = 0
        total_gst_amount = 0
        wallet_use = 0

        for ordr in orders:
            gst_price = (ordr.product_id.item_new_price * ordr.quantity) * ordr.gst_rate / 100
            product = {
                "name": ordr.product_id.title,
                "quantity": ordr.quantity,
                "old_price": ordr.product_id.item_old_price,
                "new_price": ordr.product_id.item_new_price,
                "purchase_price":ordr.product_id.item_new_price*ordr.quantity,
                "gst_price": gst_price,
            }
            products.append(product)
            total_quantity += ordr.quantity
            total_price += ordr.product_id.item_old_price * ordr.quantity
            total_saved += (ordr.product_id.item_old_price - ordr.product_id.item_new_price) * ordr.quantity
            total_gst_amount += gst_price

        if order.delivery_price:
            total_price += int(order.delivery_price)
        if order.dicounted_price:
            coupon_discount = int(order.dicounted_price)
            total_saved += int(order.dicounted_price)
        if order.walet_value:
            wallet_use = int(order.walet_value)

        order_data["products"] = products
        order_data["total_quantity"] = total_quantity
        order_data["total_price"] = round(total_price, 2)
        order_data["coupon_discount"] = round(coupon_discount, 2)
        order_data["total_saved"] = round(total_saved, 2)
        order_data["total_paid"] = order.total_price
        order_data["taxable_amount"] = int(order.total_price) - total_gst_amount
        order_data["cgst"] = round(total_gst_amount / 2, 2)
        order_data["sgst"] = round(total_gst_amount / 2, 2)
        order_data["total_gst_amount"] = round(total_gst_amount, 2)
        order_data["wallet_use"] = round(wallet_use, 2)

        html_string = render_to_string(
            "invoice.html",
            {"order": order_data}
        )

        pdf_file = HTML(
            string=html_string,
            base_url=request.build_absolute_uri()
        ).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{order.order_id}_invoice.pdf"'
        )

        return response

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_SECRET_KEY))

@csrf_exempt
@api_view(['POST'])
def create_qr_order(request):
    total_amount = request.data.get('total_amount', 0)
    if not total_amount:
        return JsonResponse({'error': 'Total amount is required'}, status=400)

    order_amount = int(float(total_amount) * 100)
    order_currency = 'INR'
    order_receipt = 'order_receipt_' + str(random.randint(100000, 999999))
    razorpay_order = razorpay_client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt))
    razorpay_order_id = razorpay_order['id']
    return JsonResponse({'razorpay_order_id': razorpay_order_id, 'order_amount': order_amount, 'status': 'success'}, status=200)

@csrf_exempt
@api_view(['POST'])
def verify_qr_order(request):
    try:
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = request.data.get('razorpay_signature')
        products = request.data.get('products', [])
        total_price = request.data.get('total_price', 0)

        if not products or not total_price:
            return JsonResponse({'error': 'No products or total price provided'}, status=400)

        if not razorpay_payment_id or not razorpay_order_id or not razorpay_signature:
            return JsonResponse({'error': 'Missing payment details'}, status=400)

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        razorpay_client.utility.verify_payment_signature(params_dict)
        
        cgst_amount = 0
        sgst_amount = 0
        total_gst = 0
        gst_rate = 0
        gstn = ""
        
        address_admin = AddressAdmin.objects.first()
        if address_admin:
            gstn = address_admin.gstn
            gst_rate = address_admin.gst_rate
            gst_amount = round((float(total_price) * gst_rate) / (100 + gst_rate), 2)
            cgst_amount = round(gst_amount / 2, 2)
            sgst_amount = round(gst_amount - cgst_amount, 2)
            total_gst = round(gst_amount, 2)

        order = None

        for prod in products:
            product = Item.objects.filter(id=prod['id']).first()
            if not product:
                continue

            order = Order.objects.create(
                order_id=razorpay_order_id,
                user_id=None,
                product_id=product,
                payment_id=razorpay_payment_id,
                pick_up=1,
                status=1,
                quantity=prod['qty'],
                price="{:.2f}".format(prod['price']),
                total_price=total_price,
                previous_price=total_price,
                dicounted_price=0,
                delivery_price=0,
                signature=razorpay_signature,
                newname="Guest User",
                phone="0000000000",
                address="Instant Order",
                city="Instant Order",
                state="Instant Order",
                country="Instant Order",
                zip_code="Instant Order",
                delivery_time="Instant Order",
                gstn=gstn,
                gst_rate=gst_rate,
                cgst_amount=cgst_amount,
                sgst_amount=sgst_amount,
                total_gst=total_gst,
                order_type="qr_code"
            )

            # stock = Stock.objects.get(item_id=prod['id'])
            # stock.openingstock -= prod['qty']
            # stock.save()
            update_stock(prod['id'], prod['qty'])

        if not order:
            return JsonResponse({'error': 'No valid products found to create order'}, status=400)

        order_data = {
            "order_id": order.order_id,
            "total_price": order.total_price,
            "total_gst": order.total_gst,
            "order_date": order.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

        return JsonResponse({'message': 'Payment successful and order created', 'success': True, 'order_data': order_data}, status=200)
    except Exception as e:
        print("Order payment verify error:", str(e))
        return JsonResponse({'error': 'Something went wrong!'}, status=500)

class DeliverySlotListAPIView(APIView):
    def get(self, request):
        slots = DeliverySlot.objects.filter(is_active=True, booked_orders__lt=F('max_orders')).order_by('start_time')
        serializer = DeliverySlotSerializer(slots, many=True)
        return Response(serializer.data)
