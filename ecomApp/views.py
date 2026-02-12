from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser,Otp
from django.db.models import Sum
from django.db.models import Count
from django.utils.timezone import datetime, timedelta
from django.db.models import Max, Subquery, OuterRef, Window
from django.db.models import F, FloatField, ExpressionWrapper
from collections import defaultdict
from django.db.models import F
from django.shortcuts import render
from datetime import timedelta

from menu_management.models import Item, MenuSettings
from django.db.models import Count, Avg, DecimalField, Value
# Create your views here.
from collections import defaultdict
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, F, Window, Subquery, OuterRef
from django.shortcuts import render
from order.models import PaymentOption, DeliverySlot
from walet.models import WalletBenefit, WalletTransaction
from django.db.models.functions import Coalesce

from .utils import fetchStocks


@login_required(login_url='backend/login')
def dashboard(request):
    if not request.user.is_staff :
        return redirect('backend/login')
    if 'logged_in_influencer' in request.session:
        del request.session['logged_in_influencer']
    if 'influencer_phone' in request.session:
        del request.session['influencer_phone']
    if request.method == 'GET':

        order_type = request.GET.get('order_type', None)
        from_date = request.GET.get('from_date', None)
        to_date = request.GET.get('to_date', None)

        # Convert date strings to datetime objects if provided
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
        else:  # If to_date is not provided, set it to today
            to_date = datetime.now()

        if not from_date:
            from_date = to_date - timedelta(days=30)

        queryset = Order.objects.exclude(payment_id="")

        if order_type:
            queryset = queryset.filter(pick_up=order_type)

        if from_date and to_date:
            to_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__range=(from_date, to_date))

        # Perform aggregation and ordering
        # day_wise_report = queryset.values('order_id', 'created_at', 'total_price') \
        #     .annotate(
        #         total_items=Count('id'),
        #         average_price=Avg('price'),
        #         total_making_price=Sum(F('product_id__makingprice') * F('quantity'))
        #     ).order_by('order_id')

        day_wise_report = queryset.values('order_id', 'created_at', 'total_price') \
            .annotate(
                total_items=Count('id'),
                average_price=Avg('price'),
                total_making_price=Sum(
                    ExpressionWrapper(
                        F('product_id__makingprice') * F('quantity'),
                        output_field=FloatField()
                    )
                )
            ).order_by('order_id')

        unique_orders = {}
        total_all_orders = 0
        total_profit_amount = 0

        for entry in day_wise_report:
            order_id = entry['order_id']
            created_at = entry['created_at'].strftime('%Y-%m-%d')
            total_making_price = entry['total_making_price']
            total_price = entry['total_price']
            delivery_price = float(entry.get('delivery_price', 0))  # Use get() to avoid KeyError

            if order_id not in unique_orders:
                unique_orders[order_id] = {
                    'created_at': created_at,
                    'total_amount': total_price,
                    'total': total_price,
                    'total_making_price': total_making_price,
                    'delivery_price': delivery_price
                }
            else:
                unique_orders[order_id]['total_amount'] += total_price
                unique_orders[order_id]['total_making_price'] += total_making_price

        for entry in day_wise_report:
            order_id = entry['order_id']
            profit_amount = entry['total_price'] - unique_orders[order_id]['total_making_price'] - \
                            unique_orders[order_id]['delivery_price']
            unique_orders[order_id]['profit_amount'] = profit_amount
            unique_orders[order_id]['total_pr'] = entry['total_price']

        total_all_orders = sum(entry['total_amount'] for entry in unique_orders.values())
        total_profit_amount += sum(entry['profit_amount'] for entry in unique_orders.values())

        day_wise_report = [{'order_id': key, **value} for key, value in unique_orders.items()]

        # Filter orders based on the provided parameters
        queryset = Order.objects.exclude(payment_id="")

        # Get the latest order for each payment_id using Max function
        latest_orders = queryset.values('payment_id').annotate(max_created_at=Max('created_at'))
        latest_order_ids = [Order.objects.filter(payment_id=order['payment_id'], created_at=order['max_created_at']).first().id for order in latest_orders]

        filtered_queryset = queryset.filter(id__in=latest_order_ids)

        if order_type:
            filtered_queryset = filtered_queryset.filter(pick_up=order_type)

        if from_date and to_date:
            to_date = to_date + timedelta(days=1)
            filtered_queryset = filtered_queryset.filter(created_at__range=(from_date, to_date))

        day_wise_report = filtered_queryset.values('created_at') \
            .annotate(total_amount=Sum('total_price')) \
            .order_by('created_at')

        unique_dates = defaultdict(lambda: {'total': 0})
        total_all_orders = 0

        for entry in day_wise_report:
            created_at = entry['created_at'].strftime('%Y-%m-%d')
            total_price = entry['total_amount']

            unique_dates[created_at]['total'] += total_price
            total_all_orders += total_price

        day_wise_report = [{'created_at': key, **value} for key, value in unique_dates.items()]

        # Retrieve total number of CustomUser
        total_custom_users = CustomUser.objects.count()

        # Retrieve total number of Item
        total_items = Item.objects.count()

        # Retrieve total number of unique payment_id of Order
        total_unique_payment_ids = Order.objects.exclude(payment_id="").values('payment_id').distinct().count()

        # Retrieve total of total_price of Order with unique payment_id
        distinct_payment_ids = Order.objects.exclude(payment_id="").values('payment_id').distinct()
        total_order_prices = 0

        for payment_id in distinct_payment_ids:
            total_order_prices += Order.objects.filter(payment_id=payment_id['payment_id']).aggregate(total_price=Sum('total_price'))['total_price']

        items = Item.objects.all().order_by('-created_at')[:5]
        orders = Order.objects.all().order_by('-created_at')

        orders_dict = {}

        for order in orders:
            if order.payment_id:
                if order.order_id not in orders_dict:
                    orders_dict[order.order_id] = order
        first_elements = [order for order in orders_dict.values()][:5]

        return render(request, 'backend/dashboard.html', {
            'ordform': first_elements,
            'items': items,
            'total_custom_users': total_custom_users,
            'total_items': total_items,
            'total_unique_payment_ids': total_unique_payment_ids,
            'total_order_prices': total_all_orders,
            'day_wise_report': day_wise_report,
            'total_profit_amount': total_profit_amount,
            'total_making': total_all_orders - total_profit_amount,
            'from_date': from_date.strftime('%Y-%m-%d'),
            'to_date': to_date.strftime('%Y-%m-%d'),
        })

    return render(request, 'backend/dashboard.html')
    
@login_required(login_url='backend/login')
def charts(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    return render(request,"backend/charts.html")

from django.contrib.auth import get_user_model  # Import get_user_model
from django.contrib.auth.models import User  # Import the User model

from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
import random
# from django.contrib.auth.models import User
from django.utils import timezone

def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email).first()  # Use User model
        if user and user.is_staff:
            # Generate OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            # Send OTP email
            subject = 'OTP for Password Change'
            message = f'Your OTP for password change is: {otp}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)

            # Store OTP and its creation time in database
            otp_obj, created = Otp.objects.get_or_create(user=user)
            otp_obj.otp = otp

            otp_obj.otp_created_at = timezone.now()
            otp_obj.save()

            return redirect('verify_otp')
        else:
            error = "Email does not exist or user is not authorized."
            return render(request, 'send_otp.html', {'error': error})
    return render(request, 'send_otp.html')

def verify_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email, is_staff=True).first()
        if user:
            # Generate OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            # Send OTP email
            subject = 'OTP for Email Verification'
            message = f'Your OTP for email verification is: {otp}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)

            # Store OTP and its creation time in database
            otp_obj, created = Otp.objects.get_or_create(user=user)
            otp_obj.otp = otp
            otp_obj.otp_created_at = timezone.now()
            otp_obj.save()

            # Store email in session
            request.session['verified_email'] = email

            return redirect('verify_otp')
        else:
            error = "Email does not exist or user is not authorized."
            return render(request, 'backend/verify_email.html', {'error': error})
    return render(request, 'backend/verify_email.html')
from django.contrib import messages

def verify_otp(request):
    email = request.session.get('verified_email')
    if not email:
        # If email is not found in session, redirect to the verify_email page
        messages.error(request, 'Please verify your email first.')
        return redirect('verify_email')

    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        user = CustomUser.objects.filter(email=email).first()
        if user and user.is_staff:
            otp_obj = Otp.objects.filter(user=user).first()
            if otp_obj:
                # Check if OTP matches
                if otp_obj.otp == otp_entered:
                    # Check if OTP is expired (5 minutes expiry)
                    if (timezone.now() - otp_obj.otp_created_at).total_seconds() > 300:
                        return render(request, 'backend/verify_otp.html', {'email': email, 'error': 'OTP has expired. Please request a new OTP.'})
                    else:
                        return redirect('change_password')
                else:
                    return render(request, 'backend/verify_otp.html', {'email': email, 'error': 'Invalid OTP. Please enter the correct OTP.'})
            else:
                return render(request, 'backend/verify_otp.html', {'email': email, 'error': 'OTP not found. Please request a new OTP.'})
        else:
            error = "Otp Does Not Match!!"
            return render(request, 'backend/verify_otp.html', {'error': error})
    return render(request, 'backend/verify_otp.html', {'email': email})
from django.contrib.auth import update_session_auth_hash

def change_password(request):
    if request.method == 'POST':
        email = request.session.get('verified_email')
        if not email:
            # If email is not found in session, redirect to the verify_email page
            messages.error(request, 'Please verify your email first.')
            return redirect('change_password')

        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'backend/change_password.html')

        user = CustomUser.objects.filter(email=email).first()
        if user:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after password change
            messages.success(request, "Password changed successfully.")
            return redirect('backend/login')
        else:
            messages.error(request, "User not found.")
            return redirect('verify_email')
    return render(request, 'backend/change_password.html')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .models import Catagory,Stock
from django.shortcuts import render

@login_required(login_url='backend/login')
def catagory(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    catagoryapp=Catagory.objects.all().order_by('-id')

    context={
        'banform': catagoryapp

    }
    return render(request,'backend/catagory.html',context)
@login_required(login_url='backend/login')
def catgoryadd(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    if request.method == "POST":
        contact = Catagory()
        name = request.POST.get('name')
        image = request.FILES.get('image')
        contact.name = name
        contact.image = image
        contact.save()
        return redirect('catagoryapp')
    return render(request, 'backend/catgoryadd.html')
@login_required(login_url='backend/login')
def delete_item(request, myid):
    if not request.user.is_staff:
        return redirect('backend/login')
    catagoryapp=Catagory.objects.get(id=myid)
    catagoryapp.delete()
    return redirect('catagoryapp')
@login_required(login_url='backend/login')
def edit_item(request, myid):
    if not request.user.is_staff:
        return redirect('backend/login')
    sel_catform=Catagory.objects.get(id=myid)
    cat = Catagory.objects.all()
    context = {
        'cat': cat,
        'sel_catform':sel_catform

    }
    return render(request,'backend/catagoryedit.html',context)
@login_required(login_url='backend/login')
def update_item(request, myid):
    if not request.user.is_staff:
        return redirect('backend/login')
    catagoryapp=Catagory.objects.get(id=myid)

    catagoryapp.name = request.POST.get('name')
    if 'image' in request.FILES:
        catagoryapp.image = request.FILES['image']

    catagoryapp.save()
    return redirect('catagoryapp')
@login_required(login_url='backend/login')
def view_item(request, myid):
    if not request.user.is_staff:
        return redirect('backend/login')
    sel_catform = Catagory.objects.get(id=myid)
    cat = Catagory.objects.all()
    context = {
        'catform': cat,
        'sel_catform': sel_catform

    }
    return render(request, 'backend/catagoryview.html', context)
@login_required(login_url='backend/login')
def activate_catagory(request, catagory_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    banner = get_object_or_404(Catagory, id=catagory_id)
    banner.status = True
    banner.save()
    return redirect('catagoryapp')  # Redirect to your banner list view
@login_required(login_url='backend/login')
def deactivate_catagory(request, catagory_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    banner = get_object_or_404(Catagory, id=catagory_id)
    banner.status = False
    banner.save()
    return redirect('catagoryapp')  # Redirect to your banner list view

from django.conf import settings
import os
# Create your views here.
@login_required(login_url='backend/login')
def customerlist(request):
    if not request.user.is_staff:
        return redirect('backend/login')

    users = CustomUser.objects.all()

    wallet_data = (
        WalletTransaction.objects
        .values('user_id')
        .annotate(
            total_recharge=Coalesce(
                Sum('credit_bal'),
                Value(0),
                output_field=DecimalField(max_digits=13, decimal_places=2)
            ),
            last_recharge_date=Max('created_at')
        )
    )

    with open(os.path.join(settings.BASE_DIR, "data.txt"), 'w') as f:
        f.write(str(wallet_data))

    wallet_map = {
        item['user_id']: {
            'total_recharge': item['total_recharge'],
            'last_recharge_date': item['last_recharge_date']
        }
        for item in wallet_data
    }

    for user in users:
        user_wallet = wallet_map.get(user.id, {})
        user.total_recharge_amount = user_wallet.get('total_recharge', 0)
        user.last_recharge_date = user_wallet.get('last_recharge_date')

    context = {
        'banform': users
    }

    return render(request,'backend/customerlist.html', context)

@login_required(login_url='backend/login')
def activate_customer(request, id):
    if not request.user.is_staff:
        return redirect('backend/login')
    banner = get_object_or_404(CustomUser, id=id)
    banner.status = True
    banner.save()
    return redirect('customerlist')  # Redirect to your banner list view
@login_required(login_url='backend/login')
def deactivate_customer(request, id):
    if not request.user.is_staff:
        return redirect('backend/login')
    banner = get_object_or_404(CustomUser, id=id)
    banner.status = False
    banner.save()
    return redirect('customerlist')  # Redirect to your banner list view

@login_required(login_url='backend/login')
def product(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    productapp=Product.objects.all()

    context={
        'banform': productapp
    }
    return render(request,'backend/product.html',context)
@login_required(login_url='backend/login')
def productadd(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    if request.method == "POST":
        product = Product()
        stock = Stock()
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        created_date = request.POST.get('created_date')
        coupon = request.POST.get('coupon')
        openingstock=request.POST.get('openingstock')

        image = request.FILES.get('image')
        product.name = name
        product.price = price
        product.description = description
        product.created_date =created_date
        product.coupon = coupon
         # Get the selected category ID
        cat_name = request.POST.get('cat_name')

       # Get the selected category name
        category = Catagory.objects.get(name=cat_name)  # Retrieve the Category object by name
        product.cat_name = category
        product.image = image
        stock.openingstock = openingstock
        stock.item = product
        product.save()
        stock.save()

        return redirect('productapp')
    # categories = Catagory.objects.get(status=True)
    categories = Catagory.objects.all()
    return render(request, 'backend/productadd.html',{'categories': categories})
@login_required(login_url='backend/login')
def delete_product(request, myid):
    if not request.user.is_staff:
        return redirect('backend/login')
    productapp=Product.objects.get(id=myid)
    productapp.delete()
    return redirect('productapp')
@login_required(login_url='backend/login')
def edit_product(request, myid):
    if not request.user.is_staff:
        return redirect('backend/login')
    sel_proform=Product.objects.get(id=myid)
    pro = Product.objects.all()
    # categories = Catagory.objects.filter(status=True)
    categories = Catagory.objects.all()
    context = {

        'pro': pro,
        'sel_proform':sel_proform,
        'categories':categories

    }
    return render(request,'backend/productedit.html',context)
@login_required(login_url='backend/login')
def update_product(request, myid):
    if not request.user.is_staff:
        return redirect('backend/login')
    productapp=Product.objects.get(id=myid)

    productapp.name = request.POST.get('name')
    productapp.price = request.POST.get('price')
    productapp.description = request.POST.get('description')
    productapp.created_date = request.POST.get('created_date')
    if 'image' in request.FILES:
        productapp.image = request.FILES['image']
    cat_name = request.POST.get('cat_name')  # Get the selected category name
    category = Catagory.objects.get(name=cat_name)  # Retrieve the Category object by name
    productapp.cat_name = category

    productapp.save()

    return redirect('productapp')
@login_required(login_url='backend/login')
def view_product(request, myid):
    if not request.user.is_staff:
        return redirect('backend/login')
    sel_proform = Product.objects.get(id=myid)
    pro = Product.objects.all()
    context = {
        'proform': pro,
        'sel_proform': sel_proform

    }
    return render(request, 'backend/productview.html', context)
@login_required(login_url='backend/login')
def activate_product(request, product_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    banner = get_object_or_404(Product, id=product_id)
    banner.status = True
    banner.save()
    return redirect('productapp')  # Redirect to your banner list view
@login_required(login_url='backend/login')
def deactivate_product(request, product_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    banner = get_object_or_404(Product, id=product_id)
    banner.status = False
    banner.save()
    return redirect('productapp')  # Redirect to your banner list view
# Create your views here.
from .models import CustomerCoupon
@login_required(login_url='backend/login')
def add_customer_coupon(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    if request.method == 'POST':
        customer_name = request.POST.get('customerName')
        minimum_purchase = request.POST.get('minimum_purchase')
        occasion_name = request.POST.get('occasionName')
        start_date = request.POST.get('startDate')
        image = request.FILES.get('image')

        expire_date = request.POST.get('expireDate')
        coupon_value = request.POST.get('couponValue') or request.POST.get('couponPercent') 
        coupon_type = request.POST.get('couponType')
        description = request.POST.get('description')
        maximum_amount_discount = request.POST.get('maximum_amount_discount')

        try:
            coupon_value = float(coupon_value)
            minimum_purchase = float(minimum_purchase)
        except:
            return render(
                request,
                'backend/add_customer_coupon.html',
                {
                    'error': "Coupon value and minimum purchase must be numbers!",
                    'form_data': request.POST
                }
            )

        if CustomerCoupon.objects.filter(coupon=customer_name).exists():
            return render(
                request,
                'backend/add_customer_coupon.html',
                {
                    'error': f"Coupon code '{customer_name}' already exists!",
                    'form_data': request.POST
                }
            )
        
        if coupon_type == "Percentage":
            if coupon_value >= 100:
                return render(
                    request,
                    'backend/add_customer_coupon.html',
                    {
                        'error': "Percentage coupon must be less than 100%",
                        'form_data': request.POST
                    }
                )
       
        elif coupon_type == "Flat":
            if minimum_purchase <= coupon_value:
                return render(
                    request,
                    'backend/add_customer_coupon.html',
                    {
                        'error': "Minimum purchase must be greater than flat coupon value!",
                        'form_data': request.POST
                    }
                )
        
        customer_coupon = CustomerCoupon(
            coupon=customer_name,
            occasion=occasion_name,
            expire_date=expire_date,
            start_date=start_date,
            coupon_value=coupon_value,
            coupon_type=coupon_type,
            description=description,
            image=image,
            minimum_purchase=minimum_purchase,
            max_amount_discount=maximum_amount_discount
        )
        customer_coupon.save()

        return redirect('customer_couponlist')  # Redirect to the desired page after submission

    return render(request, 'backend/add_customer_coupon.html')
@login_required(login_url='backend/login')
def customer_couponlist(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    coupons = CustomerCoupon.objects.all()
    return render(request, 'backend/customercouponlist.html', {'coupons': coupons})
from django.shortcuts import get_object_or_404
@login_required(login_url='backend/login')
def delete_coupon(request, coupon_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    coupon = get_object_or_404(CustomerCoupon, pk=coupon_id)
    coupon.delete()
    # Optionally, add a success message or redirect to a different page
    return redirect('customer_couponlist')
@login_required(login_url='backend/login')
def activate_coupon(request, coupon_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    banner = get_object_or_404(CustomerCoupon, id=coupon_id)
    banner.status = True
    banner.save()
    return redirect('customer_couponlist')  # Redirect to your banner list view
@login_required(login_url='backend/login')
def deactivate_coupon(request, coupon_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    banner = get_object_or_404(CustomerCoupon, id=coupon_id)
    banner.status = False
    banner.save()
    return redirect('customer_couponlist')  # Redirect to your banner list view








from .models import DeliveryCharge
@login_required(login_url='backend/login')
def charge(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    productapp=DeliveryCharge.objects.all()

    context={
        'banform': productapp
    }
    return render(request,'backend/chargelist.html',context)

@login_required(login_url='backend/login')
def payment_options(request):
    if not request.user.is_staff:
        return redirect('backend/login')

    payment_options = PaymentOption.objects.all()

    context={
        'payment_options': payment_options
    }
    return render(request,'backend/payment_options.html', context)

@login_required(login_url='backend/login')
def payment_options_add(request):
    if not request.user.is_staff:
        return redirect('backend/login')

    if request.method == "POST":
        code = request.POST.get('code')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == "1"
        
        if PaymentOption.objects.filter(code=code).exists():
            messages.error(request, "Payment option already exists.")
            return redirect('payment_options_add')

        PaymentOption.objects.create(
            code=code,
            description=description,
            is_active=is_active
        )

        messages.success(request, "Payment option added successfully.")

        return redirect('payment_options')

    return render(request, 'backend/payment_options_add.html')

@login_required(login_url='backend/login')
def chargeadd(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    if request.method == "POST":
        product = DeliveryCharge()
        charge = request.POST.get('charge')

        product.charge = charge

        product.save()

        return redirect('chargeapp')
    # categories = Catagory.objects.get(status=True)
    return render(request, 'backend/add_charge.html')

@login_required(login_url='backend/login')
def delete_charge(request, myid):
    if not request.user.is_staff:
        return redirect('backend/login')
    productapp=DeliveryCharge.objects.get(id=myid)
    productapp.delete()
    return redirect('chargeapp')
@login_required(login_url='backend/login')
def edit_charge(request, myid):
    if not request.user.is_staff:
        return redirect('backend/login')
    sel_proform=DeliveryCharge.objects.get(id=myid)
    pro = DeliveryCharge.objects.all()
    # categories = Catagory.objects.filter(status=True)
    context = {

        'pro': pro,
        'sel_proform':sel_proform,

    }
    return render(request,'backend/edit_charge.html',context)

@login_required(login_url='backend/login')
def edit_payment_option(request, id):
    if not request.user.is_staff:
        return redirect('backend/login')

    payment_option = get_object_or_404(PaymentOption, id=id)

    if request.method == "POST":
        new_code = request.POST.get('code')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == "1"

        if PaymentOption.objects.filter(code=new_code).exclude(id=id).exists():
            messages.error(request, "Payment option with this code already exists.")
            return render(
                request,
                'backend/edit_payment_option.html',
                {'payment_option': payment_option}
            )

        payment_option.code = new_code
        payment_option.description = description
        payment_option.is_active = is_active
        payment_option.save()

        messages.success(request, "Payment option updated successfully.")
        return redirect('payment_options')

    return render(request, 'backend/edit_payment_option.html', {
        'payment_option': payment_option
    })

@login_required(login_url='backend/login')
def delete_payment_option(request, id):
    if not request.user.is_staff:
        return redirect('backend/login')

    productapp = PaymentOption.objects.get(id=id)
    productapp.delete()

    messages.success(request, "Payment option deleted successfully.")
    return redirect('payment_options')

@login_required(login_url='backend/login')
def update_charge(request, myid):
    if not request.user.is_staff:
        return redirect('backend/login')
    productapp=DeliveryCharge.objects.get(id=myid)

    productapp.charge = request.POST.get('charge')

    productapp.save()

    return redirect('chargeapp')

@login_required(login_url='backend/login')
def stock(request):
    if not request.user.is_staff:
        return redirect('backend/login')

    stocks = fetchStocks()

    context = {
        'stocks': stocks
    }

    return render(request,'backend/inventory_list.html', context)

@login_required(login_url='backend/login')
def edit_stock(request, myid):
    if not request.user.is_staff:
        return redirect('backend/login')
    sel_proform=Stock.objects.get(id=myid)
    pro = Stock.objects.all()
    # categories = Catagory.objects.filter(status=True)
    context = {

        'pro': pro,
        'item':sel_proform,

    }
    return render(request,'backend/edit_inventory.html',context)
@login_required(login_url='backend/login')
def update_stock(request,stock_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    if request.method == 'POST':
        openingstock = request.POST.get('openingstock')

        try:
            stock = Stock.objects.get(id=stock_id)
            stock.openingstock = openingstock
            stock.save()

            messages.success(request, 'Stock updated successfully.')
        except Stock.DoesNotExist:
            messages.error(request, 'Stock does not exist.')
        except Exception as e:
            messages.error(request, str(e))

    return redirect('stock')
@login_required(login_url='backend/login')
def update_all_stock(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    if request.method == 'POST':

        for key, value in request.POST.items():
            if key.startswith('openingstock_'):
                stock_id = key.split('_')[1]
                try:
                    stock = get_object_or_404(Stock, pk=stock_id)
                    stock.openingstock = value
                    stock.save()
                except Exception as e:
                    # Handle exceptions as needed
                    pass
    return redirect('stock')
@login_required(login_url='backend/login')
def allstock(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    if not request.user.is_staff:
        return redirect('backend/login')
    catagoryapp=Stock.objects.all()

    context={
        'banform': catagoryapp

    }

    return render(request,'backend/allinventory_list.html',context)
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Stock
from .serializers import StockSerializer

class StockListAPIView(generics.ListAPIView):
    def get_serializer_class(self):
        return StockSerializer

    def get_queryset(self):
        queryset = Stock.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(item_id=product_id)
        return queryset


from order.models import Order
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def count_pending_orders():
    """
    Counts the number of pending orders.
    """
    pending_orders_count = Order.objects.filter(status='1').count()

    return pending_orders_count
from django.db.models import Q
@csrf_exempt  # Add this decorator if you're not handling CSRF tokens for this view
def pending_orders_count(request):
    """
    View to return the count of pending orders.
    """
    pending_orders_count = Order.objects.filter(status='1').exclude(Q(payment_id=None) | Q(payment_id='')).values('order_id').distinct().count()
    data = {'pending_orders_count': pending_orders_count}
    return JsonResponse(data)


def render_order_dropdown(request):
    """
    Renders order details in a dropdown menu.
    """
    # Fetch the orders
    orders = Order.objects.filter(status='1')[:5]  # Fetch the first 5 orders

    # Serialize order details
    serialized_orders = [{'id': order.id, 'status': order.status, 'created_at': order.created_at} for order in orders]

    # Prepare JSON response data
    data = {'orders': serialized_orders}

    # Return JSON response
    return JsonResponse(data)

from rest_framework import generics
from .models import CustomerCoupon
from .serializers import CustomerCouponSerializer
from datetime import date

class CouponList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = CustomerCouponSerializer

    def get_queryset(self):
        today = date.today()
        return CustomerCoupon.objects.filter(start_date__lte=today, expire_date__gte=today)

@login_required(login_url='backend/login')
def wallet_benefits(request):
    if not request.user.is_staff:
        return redirect('backend/login')

    wallet_benefits = WalletBenefit.objects.all()

    context={
        'wallet_benefits': wallet_benefits
    }
    return render(request,'backend/wallet_benefits.html', context)

@login_required(login_url='backend/login')
def add_wallet_benefit(request):
    if not request.user.is_staff:
        return redirect('backend/login')

    if request.method == "POST":
        try:
            add_amount = int(request.POST.get('add_amount'))
            benefit_amount = int(request.POST.get('benefit_amount'))
            if add_amount < 1 or benefit_amount < 1:
                messages.error(request, "Add amount and benefit amount must be greater that 0.")
                return redirect('add_wallet_benefit')
        except (TypeError, ValueError):
            messages.error(request, "Add amount and benefit amount must be valid numbers.")
            return redirect('add_wallet_benefit')

        description = request.POST.get('description')

        influencer = request.POST.get('influencer') == '1'
        is_active = request.POST.get('is_active') == '1'

        period = request.POST.get('influencer_time_period')

        influencer_time_period = None
        if period:
            try:
                days = int(period)
                influencer_time_period = timedelta(days=days)
            except ValueError:
                messages.error(request, "Influencer time period must be a valid number of days.")
                return redirect('add_wallet_benefit')

        try:
            influencer_benefit_percentage = float(
                request.POST.get('influencer_benefit_percentage', 0)
            )
            if influencer_benefit_percentage <= 0 or influencer_benefit_percentage > 100:
                messages.error(
                    request,
                    "Influencer benefit percentage must be between 1 and 100."
                )
                return redirect('add_wallet_benefit')
        except ValueError:
            messages.error(
                request,
                "Influencer benefit percentage must be a valid number."
            )
            return redirect('add_wallet_benefit')

        if WalletBenefit.objects.filter(add_amount=add_amount).exists():
            messages.error(request, "A wallet benefit with this add amount already exists.")
            return redirect('add_wallet_benefit')

        if influencer:
            if not influencer_time_period:
                messages.error(
                    request,
                    "Influencer time period is required when influencer benefit is enabled."
                )
                return redirect('add_wallet_benefit')

            if influencer_time_period.days < 1:
                messages.error(
                    request,
                    "Influencer time period must be at least 1 day."
                )
                return redirect('add_wallet_benefit')

        WalletBenefit.objects.create(
            add_amount=add_amount,
            benefit_amount=benefit_amount,
            influencer=influencer,
            influencer_time_period=influencer_time_period,
            influencer_benefit_percentage=influencer_benefit_percentage,
            description=description,
            is_active=is_active
        )

        messages.success(request, "Wallet benefit added successfully.")

        return redirect('wallet_benefits')

    return render(request, 'backend/add_wallet_benefit.html')

@login_required(login_url='backend/login')
def edit_wallet_benefit(request, id):
    if not request.user.is_staff:
        return redirect('backend/login')

    wallet_benefit = get_object_or_404(WalletBenefit, id=id)

    if request.method == "POST":
        try:
            add_amount = int(request.POST.get('add_amount'))
            benefit_amount = int(request.POST.get('benefit_amount'))
            if add_amount < 1 or benefit_amount < 1:
                messages.error(request, "Add amount and benefit amount must be greater that 0.")
                return render(
                    request,
                    'backend/edit_wallet_benefit.html',
                    {'wallet_benefit': wallet_benefit}
                )
        except (TypeError, ValueError):
            messages.error(
                request,
                "Add amount and benefit amount must be valid numbers."
            )
            return render(
                request,
                'backend/edit_wallet_benefit.html',
                {'wallet_benefit': wallet_benefit}
            )

        description = request.POST.get('description')
        influencer = request.POST.get('influencer') == '1'
        is_active = request.POST.get('is_active')

        period = request.POST.get('influencer_time_period')
        influencer_time_period = None

        try:
            influencer_benefit_percentage = float(
                request.POST.get('influencer_benefit_percentage', 0)
            )
            if influencer_benefit_percentage <= 0 or influencer_benefit_percentage > 100:
                messages.error(
                    request,
                    "Influencer benefit percentage must be between 1 and 100."
                )
                return render(
                    request,
                    'backend/edit_wallet_benefit.html',
                    {'wallet_benefit': wallet_benefit}
                )
        except ValueError:
            messages.error(
                request,
                "Influencer benefit percentage must be a valid number."
            )
            return render(
                request,
                'backend/edit_wallet_benefit.html',
                {'wallet_benefit': wallet_benefit}
            )

        if influencer:
            if not period:
                messages.error(
                    request,
                    "Influencer validity period is required when Influencer is enabled."
                )
                return render(
                    request,
                    'backend/edit_wallet_benefit.html',
                    {'wallet_benefit': wallet_benefit}
                )

            try:
                days = int(period)
                if days < 1:
                    raise ValueError
                influencer_time_period = timedelta(days=days)
            except ValueError:
                messages.error(
                    request,
                    "Influencer validity period must be at least 1 day."
                )
                return render(
                    request,
                    'backend/edit_wallet_benefit.html',
                    {'wallet_benefit': wallet_benefit}
                )

        try:
            if WalletBenefit.objects.filter(add_amount=add_amount).exclude(id=id).exists():
                messages.error(request, "A wallet benefit with this add amount already exists.")
                return render(
                    request,
                    'backend/edit_wallet_benefit.html',
                    {'wallet_benefit': wallet_benefit}
                )

            wallet_benefit.add_amount = add_amount
            wallet_benefit.benefit_amount = benefit_amount
            wallet_benefit.description = description
            wallet_benefit.influencer = influencer
            wallet_benefit.influencer_time_period = influencer_time_period
            wallet_benefit.influencer_benefit_percentage = influencer_benefit_percentage
            wallet_benefit.is_active = is_active
            wallet_benefit.save()

            messages.success(request, "Payment option updated successfully.")
            return redirect('wallet_benefits')
        except:
            messages.success(request, "Something went wrong.")
            return redirect('wallet_benefits')

    return render(request, 'backend/edit_wallet_benefit.html', {
        'wallet_benefit': wallet_benefit
    })

@login_required(login_url='backend/login')
def delete_wallet_benefit(request, id):
    if not request.user.is_staff:
        return redirect('backend/login')

    wallet_benefit = WalletBenefit.objects.get(id=id)
    wallet_benefit.delete()

    messages.success(request, "Wallet benefit deleted successfully.")
    return redirect('wallet_benefits')

@login_required(login_url='backend/login')
def menu_settings(request):
    settings = MenuSettings.objects.all().order_by('-id')
    return render(request, 'backend/menu_settings.html', {
        'settings': settings
        })

@login_required(login_url='backend/login')
def add_menu_setting(request):
    if MenuSettings.objects.all().exists():
        messages.error(request, "Only one menu setting allowed. Please edit the existing one.")
        return redirect('menu_settings')

    if request.method == "POST":
        show_out_of_stock = request.POST.get('show_out_of_stock') == 'on'

        MenuSettings.objects.all().delete()

        MenuSettings.objects.create(
            show_out_of_stock=show_out_of_stock
        )

        messages.success(request, "Menu setting added successfully")
        return redirect('menu_settings')

    return render(request, 'backend/menu_settings_add.html')

@login_required(login_url='backend/login')
def edit_menu_setting(request, id):
    setting = get_object_or_404(MenuSettings, id=id)

    if request.method == "POST":
        setting.show_out_of_stock = request.POST.get('show_out_of_stock') == 'on'
        setting.save()

        messages.success(request, "Menu setting updated successfully")
        return redirect('menu_settings')

    return render(request, 'backend/menu_settings_edit.html', {
        'setting': setting,
    })


@login_required(login_url='backend/login')
def delete_menu_setting(request, id):
    setting = get_object_or_404(MenuSettings, id=id)
    setting.delete()
    messages.success(request, "Menu setting deleted successfully")
    return redirect('menu_settings')

@login_required(login_url='backend/login')
def delivery_slots(request):
    slots = DeliverySlot.objects.all().order_by('-id')
    return render(request, 'backend/delivery_slots.html', {
        'slots': slots
        })

@login_required(login_url='backend/login')
def add_delivery_slot(request):
    if request.method == "POST":
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        is_active = request.POST.get('is_active', False) == 'on'

        if start_time >= end_time:
            messages.error(request, "End time must be greater than start time")
            return redirect('add_delivery_slot')

        overlapping_slot = DeliverySlot.objects.filter(
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if overlapping_slot:
            messages.error(
                request,
                "Another delivery slot already exists in this time range"
            )
            return redirect('add_delivery_slot')

        DeliverySlot.objects.create(
            start_time=start_time,
            end_time=end_time,
            is_active=is_active
        )

        messages.success(request, "Delivery slot added successfully")
        return redirect('delivery_slots')

    return render(request, 'backend/delivery_slots_add.html')

@login_required(login_url='backend/login')
def edit_delivery_slot(request, id):
    delivery_slot = get_object_or_404(DeliverySlot, id=id)

    if request.method == "POST":
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        max_orders = request.POST.get('max_orders')
        is_active = request.POST.get('is_active') == 'on'

        if start_time >= end_time:
            messages.error(request, "End time must be greater than start time")
            return redirect('edit_delivery_slot', id=id)

        overlapping_slot = DeliverySlot.objects.filter(
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(id=id).exists()

        if overlapping_slot:
            messages.error(
                request,
                "Another delivery slot already exists in this time range"
            )
            return redirect('edit_delivery_slot', id=id)

        delivery_slot.start_time = start_time
        delivery_slot.end_time = end_time
        delivery_slot.max_orders = max_orders
        delivery_slot.is_active = is_active
        delivery_slot.save()

        messages.success(request, "Delivery slot updated successfully")
        return redirect('delivery_slots')

    return render(request, 'backend/delivery_slots_edit.html', {
        'delivery_slot': delivery_slot
    })

@login_required(login_url='backend/login')
def delete_delivery_slot(request, id):
    delivery_slot = get_object_or_404(DeliverySlot, id=id)
    delivery_slot.delete()
    messages.success(request, "Delivery slot deleted successfully")
    return redirect('delivery_slots')
