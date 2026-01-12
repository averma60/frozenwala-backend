from django.shortcuts import render
from order.models import Order
from django.db.models import Sum
from django.db.models import Count
from django.utils.timezone import datetime, timedelta
from django.db.models.functions import TruncDate


from django.db.models import Count, Avg
from menu_management.models import Item
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F

@login_required(login_url='backend/login')
def render_product_dropdown(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    products = Item.objects.all()
    return render(request, 'backend/itemwisereport.html', {'products': products})
@login_required(login_url='backend/login')
def daywise_report(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    if request.method == 'GET':
        order_type = request.GET.get('order_type', None)
        from_date = request.GET.get('from_date', None)
        to_date = request.GET.get('to_date', None)

        # Convert date strings to datetime objects if provided
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
        if not to_date:  # If to_date is not provided, set it to today
            to_date = datetime.now()

            # If from_date is not provided, set it to 30 days before to_date
        if not from_date:
            from_date = to_date - timedelta(days=30)
        # Filter orders based on the provided parameters
        queryset = Order.objects.all()
        queryset = queryset.exclude(payment_id="")

        if order_type:
            queryset = queryset.filter(pick_up=order_type)

        if from_date and to_date:
            # Add one day to include the end date
            to_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__range=(from_date, to_date))

        # Perform aggregation and ordering
        day_wise_report = queryset.values('order_id', 'created_at', 'total_price') \
            .annotate(total_amount=Sum('total_price'),
                      total_items=Count('id'),  # Counting unique items, not order_id occurrences
                      average_price=Avg('price')) \
            .order_by('order_id')

        # Convert the queryset to a dictionary for rendering
        unique_orders = {}
        total_amounts = {}

        for entry in day_wise_report:
            order_id = entry['order_id']
            created_at = entry['created_at'].strftime('%Y-%m-%d')  # Format the datetime
            total_price = entry['total_price']
            if order_id not in unique_orders:
                unique_orders[order_id] = {
                    'created_at': created_at,
                    'total_amount': total_price,
                    'total': total_price,
                }
                total_amounts[order_id] = total_price
            else:
                unique_orders[order_id]['total_amount'] += total_price
        total_all_orders = sum(total_amounts.values())        # Convert unique_orders dictionary to a list of dictionaries for rendering
        day_wise_report = [{'order_id': key, **value} for key, value in unique_orders.items()]

        return render(request, 'backend/daywisereport.html', {'day_wise_report': day_wise_report,'total_all_orders': total_all_orders})

    return render(request, 'backend/daywisereport.html', {})
@login_required(login_url='backend/login')
def itemwise_report(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    if request.method == 'GET':
        from_date = request.GET.get('from_date', None)
        to_date = request.GET.get('to_date', None)
        product_id = request.GET.get('product_id', None)  # Get product_id parameter

        # Convert date strings to datetime objects if provided
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
        if not to_date:  # If to_date is not provided, set it to today
            to_date = datetime.now()

            # If from_date is not provided, set it to 30 days before to_date
        if not from_date:
            from_date = to_date - timedelta(days=30)
        # Filter orders based on the provided parameters
        queryset = Order.objects.exclude(payment_id="")

        if from_date and to_date:
            # Add one day to include the end date
            to_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__range=(from_date, to_date))

        if product_id:
            queryset = queryset.filter(product_id=product_id)  # Filter by product_id

        # Aggregate total order amount for each product
        itemwise_report = queryset.values('product_id', 'product_id__title') \
            .annotate(total_order_amount=Sum(F('price') * F('quantity')))

        products = Item.objects.all()

        return render(request, 'backend/itemwisereport.html', {'itemwise_report': itemwise_report, 'products': products})

    return render(request, 'backend/itemwisereport.html', {})
from datetime import date

@login_required(login_url='backend/login')
def daily_sale(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    today = date.today()

    orders = Order.objects.filter(created_at__date=today).order_by('-created_at')

    # Create a dictionary to store orders grouped by their order_id
    orders_dict = {}

    # Iterate over orders and group them by their order_id
    for order in orders:
        if order.payment_id:
            if order.order_id not in orders_dict:
                orders_dict[order.order_id] = order
    # Extract the first element of each group
    first_elements = [order for order in orders_dict.values()]

    # Pass the first elements to the template context
    context = {
        'ordform': first_elements
    }
    return render(request, 'backend/daily_sale.html', context)
from django.db.models import Sum
from menu_management.models import Item  # Import the Item model

@login_required(login_url='backend/login')
def category_wise_sales_report(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    # Filter orders to get only orders with payment IDs
    orders = Order.objects.filter(payment_id__isnull=False)

    # Create a dictionary to store sales totals for each category
    category_sales = {}

    # Create a set to keep track of unique order IDs
    unique_order_ids = set()

    # Iterate over orders and aggregate sales by category
    for order in orders:
        # Check if the order ID is already processed
        if order.order_id not in unique_order_ids:
            # Get the product associated with the order
            product = order.product_id
            # Get the category of the product
            category = product.category.name
            # Calculate the total price of the order by multiplying price with quantity
            total_price = order.price * order.quantity
            # Add the total price of the order to the category's sales total
            if category in category_sales:
                category_sales[category] += total_price
            else:
                category_sales[category] = total_price
            # Add the order ID to the set of processed order IDs

    # Pass the category-wise sales data to the template context
    context = {
        'category_sales': category_sales.items()
    }
    return render(request, 'backend/category_wise_sales_report.html', context)
@login_required(login_url='backend/login')
def profit_report(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    if request.method == 'GET':
        order_type = request.GET.get('order_type', None)
        from_date = request.GET.get('from_date', None)
        to_date = request.GET.get('to_date', None)

        # Convert date strings to datetime objects if provided
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
        if not to_date:  # If to_date is not provided, set it to today
            to_date = datetime.now()

        # If from_date is not provided, set it to 30 days before to_date
        if not from_date:
            from_date = to_date - timedelta(days=30)

        # Filter orders based on the provided parameters
        queryset = Order.objects.exclude(payment_id="")

        if order_type:
            queryset = queryset.filter(pick_up=order_type)

        if from_date and to_date:
            # Add one day to include the end date
            to_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__range=(from_date, to_date))

        # Perform aggregation and ordering
        day_wise_report = queryset.values('order_id', 'created_at', 'delivery_price') \
            .annotate(
            total_items=Count('id'),
            total_price=Sum('total_price'),
            total_making_price=Sum(F('product_id__makingprice') * F('quantity'))
        ) \
            .order_by('order_id')

        # Convert the queryset to a dictionary for rendering
        unique_orders = {}
        total_all_orders = 0
        total_profit_amount = 0

        for entry in day_wise_report:
            order_id = entry['order_id']
            created_at = entry['created_at'].strftime('%Y-%m-%d')  # Format the datetime
            total_making_price = entry['total_making_price']
            total_price = entry['total_price']
            delivery_price = float(entry['delivery_price'])  # Convert delivery_price to float

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

        # Calculate profit amount for each entry
        for entry in day_wise_report:
            order_id = entry['order_id']
            profit_amount = entry['total_price'] - unique_orders[order_id]['total_making_price'] - \
                            unique_orders[order_id]['delivery_price']
            unique_orders[order_id]['profit_amount'] = profit_amount
            unique_orders[order_id]['total_pr'] = entry['total_price']

        total_all_orders = sum(entry['total_amount'] for entry in unique_orders.values())
        total_profit_amount += sum(entry['profit_amount'] for entry in unique_orders.values())

        # Convert unique_orders dictionary to a list of dictionaries for rendering
        day_wise_report = [{'order_id': key, **value} for key, value in unique_orders.items()]

        return render(request, 'backend/profitforpickup.html',
                      {'day_wise_report': day_wise_report, 'total_all_orders': total_all_orders,
                       'total_profit_amount': total_profit_amount})

    return render(request, 'backend/profitforpickup.html', {})

# def profit_report(request):
#     if request.method == 'GET':
#         order_type = request.GET.get('order_type', None)
#         from_date = request.GET.get('from_date', None)
#         to_date = request.GET.get('to_date', None)
#
#         # Convert date strings to datetime objects if provided
#         if from_date:
#             from_date = datetime.strptime(from_date, '%Y-%m-%d')
#         if to_date:
#             to_date = datetime.strptime(to_date, '%Y-%m-%d')
#         if not to_date:  # If to_date is not provided, set it to today
#             to_date = datetime.now()
#
#             # If from_date is not provided, set it to 30 days before to_date
#         if not from_date:
#             from_date = to_date - timedelta(days=30)
#         # Filter orders based on the provided parameters
#         queryset = Order.objects.exclude(payment_id="")
#
#         if order_type:
#             queryset = queryset.filter(pick_up=order_type)
#
#         if from_date and to_date:
#             # Add one day to include the end date
#             to_date = to_date + timedelta(days=1)
#             queryset = queryset.filter(created_at__range=(from_date, to_date))
#
#         # Perform aggregation and ordering
#         day_wise_report = queryset.values('order_id', 'created_at','total_price') \
#             .annotate(
#                       total_items=Count('id'),
#                       average_price=Avg('price'),
#                       total_making_price=Sum('product_id__makingprice')) \
#             .order_by('order_id')
#
#         # Convert the queryset to a dictionary for rendering
#         unique_orders = {}
#         total_all_orders = 0
#         total_profit_amount=0
#         for entry in day_wise_report:
#             order_id = entry['order_id']
#             created_at = entry['created_at'].strftime('%Y-%m-%d')  # Format the datetime
#             total_making_price = entry['total_making_price']
#             total_price = entry['total_price']
#
#             if order_id not in unique_orders:
#                 unique_orders[order_id] = {
#                     'created_at': created_at,
#                     'total_amount': total_price,
#                     'total': total_price,
#                     'total_making_price': total_making_price,
#                 }
#             else:
#                 unique_orders[order_id]['total_amount'] += total_price
#                 unique_orders[order_id]['total_making_price'] += total_making_price
#         # Calculate profit amount for each entry
#         # Calculate profit amount for each entry
#         for entry in day_wise_report:
#             order_id = entry['order_id']
#             profit_amount = entry['total_price'] - unique_orders[order_id]['total_making_price']
#             unique_orders[order_id]['profit_amount'] = profit_amount
#             unique_orders[order_id]['total_pr'] = entry['total_price']
#
#
#         total_all_orders = sum(entry['total_amount'] for entry in unique_orders.values())
#         total_profit_amount += sum(entry['profit_amount'] for entry in unique_orders.values())
#
#         # Convert unique_orders dictionary to a list of dictionaries for rendering
#         day_wise_report = [{'order_id': key, **value} for key, value in unique_orders.items()]
#
#         return render(request, 'backend/profitforpickup.html',
#                       {'day_wise_report': day_wise_report, 'total_all_orders': total_all_orders,'total_profit_amount':total_profit_amount})
#
#     return render(request, 'backend/profitforpickup.html', {})