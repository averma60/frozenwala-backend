from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from order.models import Order
from django.db.models import Sum
from django.db.models import Count
from django.utils.timezone import datetime, timedelta
from django.db.models.functions import TruncDate
from collections import defaultdict


from django.db.models import Count, Avg
from menu_management.models import Item
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.models import Max, Subquery, OuterRef


@login_required(login_url='backend/login')
def render_product_dropdown(request):
    products = Item.objects.all()
    return render(request, 'backend/itemwisechart.html', {'products': products})


@login_required(login_url='backend/login')
def daywise_chart(request):
    if request.method == 'GET':
        order_type = request.GET.get('order_type', None)
        from_date = request.GET.get('from_date', None)
        to_date = request.GET.get('to_date', None)

        # Convert date strings to datetime objects if provided
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d')

        # Filter orders based on the provided parameters
        queryset = Order.objects.exclude(payment_id="")

        # Subquery to get the latest order for each payment_id
        latest_order_subquery = Order.objects.filter(payment_id=OuterRef('payment_id')) \
                                             .values('payment_id') \
                                             .annotate(max_created_at=Max('created_at'))

        queryset = queryset.annotate(
            max_created_at=Subquery(latest_order_subquery.values('max_created_at')[:1])
        ).filter(created_at=F('max_created_at'))

        if order_type:
            queryset = queryset.filter(pick_up=order_type)

        if from_date and to_date:
            # Add one day to include the end date
            to_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__range=(from_date, to_date))

        # Perform aggregation and ordering
        day_wise_report = queryset.values('created_at') \
            .annotate(total_amount=Sum('total_price')) \
            .order_by('created_at')

        # Convert the queryset to a dictionary for rendering
        unique_dates = defaultdict(lambda: {'total': 0})  # Using defaultdict to store totals for each unique created date
        total_all_orders = 0

        for entry in day_wise_report:
            created_at = entry['created_at'].strftime('%Y-%m-%d')  # Format the datetime
            total_price = entry['total_amount']

            # Aggregate totals for each unique created date
            unique_dates[created_at]['total'] += total_price
            total_all_orders += total_price

        # Convert unique_dates dictionary to a list of dictionaries for rendering
        day_wise_report = [{'created_at': key, **value} for key, value in unique_dates.items()]

        return render(request, 'backend/daywise_chart.html',
                      {'day_wise_report': day_wise_report, 'total_all_orders': total_all_orders})

    return render(request, 'backend/daywise_chart.html', {})
@login_required(login_url='backend/login')
def itemwise_chart(request):
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

        return render(request, 'backend/itemwisechart.html', {'itemwise_report': itemwise_report, 'products': products})

    return render(request, 'backend/itemwisechart.html', {})
from datetime import date

@login_required(login_url='backend/login')
def daily_chart(request):
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
    return render(request, 'backend/daily_chart.html', context)
from django.db.models import Sum
from menu_management.models import Item  # Import the Item model

@login_required(login_url='backend/login')
def category_wise_sales_chart(request):
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
    return render(request, 'backend/category_wise_sales_chart.html', context)
@login_required(login_url='backend/login')
def profit_chart(request):
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
        # Initialize a dictionary to store total profit for each date
        total_profit_by_date = {}

        # Calculate profit amount for each entry and aggregate by date
        for entry in day_wise_report:
            created_at = entry['created_at']
            profit_amount = entry['total_pr'] - entry['total_making_price'] - entry['delivery_price']

            if created_at not in total_profit_by_date:
                total_profit_by_date[created_at] = profit_amount
            else:
                total_profit_by_date[created_at] += profit_amount

        # Convert the total profit by date dictionary to a list of dictionaries for rendering
        total_profit_report = [{'created_at': key, 'total_profit': value} for key, value in
                               total_profit_by_date.items()]

        # Now you have a list of dictionaries with 'created_at' and 'total_profit' for each date

    return render(request, 'backend/profitforpickupchart.html',
                      {'day_wise_report': total_profit_report, 'total_all_orders': total_all_orders,'total_profit_amount':total_profit_amount})

    return render(request, 'backend/profitforpickupchart.html', {})