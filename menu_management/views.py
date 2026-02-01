from django.db.models import  Q, Avg, Count
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Item, ItemImage, ItemReview, ItemHighlights, MenuSettings
from ecomApp.models  import Catagory,Stock, DeliveryCharge
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from .serializers import ItemReviewSerializer
from rest_framework.permissions import AllowAny
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods


@login_required(login_url='backend/login')
@require_http_methods(["GET", "POST"])
def item_list(request):
    if not request.user.is_staff:
        return redirect('backend/login')

    if request.method == "POST":
        item_ids = request.POST.getlist('item_ids')
        action = request.POST.get('action')
        
        if not item_ids:
            return redirect('item_list')

        if action == "deactivate":
            Item.objects.filter(id__in=item_ids).update(status=False)

        elif action == "activate":
            Item.objects.filter(id__in=item_ids).update(status=True)

    category_id = request.GET.get('category')
    brand_name = request.GET.get('brand')

    items = Item.objects.all() .order_by('-created_at')

    if category_id:
        items = items.filter(category_id=category_id)

    if brand_name:
        items = items.filter(brand_name=brand_name)

    categories = Catagory.objects.all()

    brands = (
        Item.objects
        .exclude(brand_name__isnull=True)
        .exclude(brand_name__exact='')
        .values_list('brand_name', flat=True)
        .distinct()
    )

    context = {
        'items': items,
        'categories': categories,
        'brands': brands,
        'selected_category': category_id,
        'selected_brand': brand_name,
        'ASSET_URL': settings.ASSET_URL
    }
    return render(request, 'backend/item_list.html', context)

@login_required(login_url='backend/login')
def add_item(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    if request.method == "POST":
        title=request.POST.get('title')
        # weight_units=request.POST.get('weight_units')
        description=request.POST.get('description')
        item_photo = request.FILES.get('item_photo')
        # item_quantity = request.POST.get('item_quantity')
        item_old_price = request.POST.get('item_old_price')
        item_new_price = request.POST.get('item_new_price')

        discount = request.POST.get('discount')
        mp = request.POST.get('mp')

        category_id = request.POST.get('category')
        deal_of_the_day = request.POST.get('deal_of_the_day') == 'on'
        recommended = request.POST.get('recommended') == 'on'
        most_popular = request.POST.get('most_popular') == 'on'

        # Calculate item_new_price based on item_old_price and discount
        # item_new_price = float(item_old_price) * (1 - float(discount) / 100)
        mp = round(float(mp), 2)
        item_new_price=round(float(item_new_price),2)
        item_old_price=round(float(item_old_price),2)
        # Create the item object
        item = Item.objects.create(
            title=title,
            # item_measurement=weight_units,
            description=description,
            item_photo=item_photo,
            makingprice=mp,
            # item_quantity=item_quantity,
            item_old_price=item_old_price,
            discount=discount,
            item_new_price=item_new_price,
            status=True,
            category_id=category_id,
            most_popular=most_popular,
            recommended=recommended,
            deal_of_the_day=deal_of_the_day
        )
        Stock.objects.create(openingstock=0, item_id=item)
        # existing_items = Item.objects.all()
        #
        # for item in existing_items:
        #     # Check if a Stock entry already exists for this item
        #     existing_stock = Stock.objects.filter(item_id=item).exists()
        #
        #     # If a Stock entry doesn't exist, create one with opening stock = 0
        #     if not existing_stock:
        #         Stock.objects.create(openingstock=1, item_id=item)
        return redirect('item_list')

    # If the request method is not POST, render the form
    categories = Catagory.objects.all()
    return render(request, 'backend/add_item.html', {'categories': categories})
@login_required(login_url='backend/login')
def veg(request, item_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(Item, id=item_id)
    item.veg = '0'
    item.save()
    return redirect('item_list')

@login_required(login_url='backend/login')
def nonveg(request, item_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(Item, id=item_id)
    item.veg = '1'
    item.save()
    return redirect('item_list')
@login_required(login_url='backend/login')
def activate_item(request, item_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(Item, id=item_id)
    item.status = True
    item.save()
    return redirect('item_list')

@login_required(login_url='backend/login')
def deactivate_item(request, item_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(Item, id=item_id)
    item.status = False
    item.save()
    return redirect('item_list')

@login_required(login_url='backend/login')
def delete_item(request, item_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    return redirect('item_list')

@login_required(login_url='backend/login')
def view_item(request, item_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'backend/view_item.html', {'item': item, 'ASSET_URL': settings.ASSET_URL})

@login_required(login_url='backend/login')
def deal_of_the_day(request):
    if not request.user.is_staff:
        return redirect('backend/login')    
    items = Item.objects.filter(status=1, itemhighlights__deals_of_the_day=True)
    context = {
        'items': items
    }
    return render(request, 'backend/deal_of_the_day.html', context)
@login_required(login_url='backend/login')
def recommended(request):
    if not request.user.is_staff:
        return redirect('backend/login')    
    items = Item.objects.filter(status=1, itemhighlights__recommended=True)
    context = {
        'items': items
    }
    return render(request, 'backend/recommended.html', context)

@login_required(login_url='backend/login')
def most_popular(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    items = Item.objects.filter(status=1, itemhighlights__popular_item=True)    
    context = {
        'items': items
    }
    return render(request, 'backend/most_popular.html', context)

@login_required(login_url='backend/login')
def update_item(request, item_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    edit_item = get_object_or_404(Item, id=item_id)

    try:
        item_photo = request.FILES.get('item_photo')
        if item_photo:
            edit_item.item_photo = item_photo
        edit_item.title = request.POST.get('title')
        # edit_item.item_measurement = request.POST.get('item_measurement')

        edit_item.description = request.POST.get('description')
        # edit_item.item_quantity = request.POST.get('item_quantity')
        edit_item.item_old_price = request.POST.get('item_old_price')
        edit_item.discount = request.POST.get('discount')
        edit_item.item_new_price = request.POST.get('item_new_price')
        edit_item.deal_of_the_day = request.POST.get('deal_of_the_day') == 'on'
        edit_item.recommended = request.POST.get('recommended') == 'on'
        edit_item.most_popular = request.POST.get('most_popular') == 'on'

        edit_item.category_id = request.POST.get('category')  # Assuming you're passing category id from the form
        edit_item.save()

        deal_of_the_day = request.POST.get('deal_of_the_day') == 'on'
        recommended = request.POST.get('recommended') == 'on'
        popular_item = request.POST.get('most_popular') == 'on'

        highlight, created = ItemHighlights.objects.get_or_create(item=edit_item)

        highlight.deals_of_the_day = deal_of_the_day
        highlight.recommended = recommended
        highlight.popular_item = popular_item
        
        highlight.save()

        return redirect('item_list')
    except Exception as e:
            # If an error occurs during update, handle it here
        error_message = f'Error occurred while updating item: {e}'
        return render(request, 'backend/edit_item.html', {'item': edit_item, 'message': error_message})

    return render(request, 'backend/edit_item.html', {'item': edit_item})

@login_required(login_url='backend/login')
def edit_item(request, item_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    sel_item = get_object_or_404(Item, id=item_id)
    all_items = Item.objects.all()
    categories = Catagory.objects.all()

    highlight = ItemHighlights.objects.filter(item_id=item_id).first()

    context = {
        'all_items': all_items,
        'item': sel_item,
        'categories':categories,
        'highlight': highlight
    }
    return render(request, 'backend/edit_item.html', context)
from ecomApp.models import Stock
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Item
from .serializers import ItemSerializer,CategorySerializer

from django.db.models import F, Sum

class DealOfTheDayAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Item.objects.filter(itemhighlights__deals_of_the_day=True, status=True) # , stock__openingstock__gt=0
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)


class RecommendedAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        brand_param = request.query_params.get('brand', None)

        menu_setting = MenuSettings.objects.first()
        if menu_setting and menu_setting.show_out_of_stock:
            items = Item.objects.filter(itemhighlights__recommended=True, status=True) #, stock__openingstock__gt=0
        else:
            items = Item.objects.filter(itemhighlights__recommended=True, status=True, stock__openingstock__gt=0)
        
        if brand_param:
            brand_list = [b.strip() for b in brand_param.split(",")]
            query = Q()
            for b in brand_list:
                query |= Q(brand_name__iexact=b)
            items = items.filter(query)

        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

class MostPopularAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Item.objects.filter(itemhighlights__popular_item=True, status=True) # , stock__openingstock__gt=0
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)
class AllProduct(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Item.objects.filter(status=1)        
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)
    
class CategoryPagination(PageNumberPagination):
    page_size = 10  # default items per page
    page_size_query_param = 'page_size'  # allow ?page_size=20
    max_page_size = 100

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import Item
from .serializers import ItemSerializer


class SimplePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100



class CategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category_id = request.query_params.get('category_id')
        paginator = SimplePagination()

        try:
            # Filter items by category and status=True
            items = Item.objects.filter(category__id=category_id, status=True)

            # Paginate queryset
            paginated_items = paginator.paginate_queryset(items, request)
            serializer = ItemSerializer(paginated_items, many=True)

            # Return only required data
            response_data = {
                "total": items.count(),
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Item.DoesNotExist:
            return Response(
                {"error": "Category does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# class ProductDetailsAPIView(APIView):
#     # permission_classes = [IsAuthenticated]
#     def get(self, request):
#         product_id = request.query_params.get('product_id')

#         if not product_id:
#             return Response(
#                 {"error": "product_id is required"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             # Get product
#             item = Item.objects.get(id=product_id, status=True)

#             # Serialize product
#             item_data = ItemSerializer(item).data

#             asset_url = getattr(settings, "ASSET_URL", "")

#             # Fetch image gallery
#             images = ItemImage.objects.filter(item=item).order_by('sort_order')

#             image_gallery = []
#             for img in images:
#                 full_url = asset_url + img.image_path.lstrip("/")   # Prevent double slash

#                 image_gallery.append({
#                     "image_path": full_url
#                 })

#             # Insert image gallery inside product object
#             item_data["image_gallery"] = image_gallery

#             return Response({"product": item_data}, status=status.HTTP_200_OK)

#         except Item.DoesNotExist:
#             return Response(
#                 {"error": "Product not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

class ProductDetailsAPIView(APIView):
    permission_classes = []  # Allow public access
    authentication_classes = []  # Let DRF handle optional auth

    def get(self, request):
        product_id = request.query_params.get('product_id')

        if not product_id:
            return Response(
                {"error": "product_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            item = Item.objects.get(id=product_id, status=True)
            item_data = ItemSerializer(item).data
            
            old_price = item_data.get("item_old_price", 0)
            new_price = item_data.get("item_new_price", 0)

            if old_price and new_price and old_price > new_price:
                discount_percentage = round(((old_price - new_price) / old_price) * 100)
            else:
                discount_percentage = 0

            item_data["discount_percentage"] = discount_percentage
            asset_url = getattr(settings, "ASSET_URL", "")

            images = ItemImage.objects.filter(item=item).order_by("sort_order")

            item_data["image_gallery"] = [
                {"media_path": asset_url + img.image_path, "media_type": img.media_type, "id": img.id}
                for img in images if img.image_path
            ]

            reviews = ItemReview.objects.filter(item=item)

            stats = reviews.aggregate(
                average_rating=Avg("rating"),
                total_reviews=Count("id")
            )

            item_data["rating"] = {
                "average": stats["average_rating"] or 0,
                "total_reviews": stats["total_reviews"]
            }

            item_data["reviews"] = ItemReviewSerializer(
                reviews.order_by("-created_at")[:10],
                many=True
            ).data
            
            user = request.user if request.user.is_authenticated else None

            if user:
                item_data["user"] = None
                try:
                    user_review = ItemReview.objects.get(item=item, user=user)
                    item_data["user_rating"] = user_review.rating
                    item_data["user_review"] = user_review.review_text
                except ItemReview.DoesNotExist:
                    item_data["user_rating"] = None
                    item_data["user_review"] = None                    
            else:
                item_data["user_rating"] = None
                item_data["user_review"] = None
                item_data["user"] = None

            return Response({"product": item_data}, status=status.HTTP_200_OK)

        except Item.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AddOrUpdateReview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        user = request.user

        rating = request.data.get("rating")
        review_text = request.data.get("review_text", "")

        if not rating:
            return Response({"error": "Rating is required"}, status=400)

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        # Check if review exists (unique per user per item)
        review, created = ItemReview.objects.get_or_create(
            user=user,
            item=item,
            defaults={"rating": rating, "review_text": review_text}
        )

        if not created:
            # Update
            review.rating = rating
            review.review_text = review_text
            review.save()

        serializer = ItemReviewSerializer(review)
        return Response(serializer.data, status=200)
    

class GetItemReviews(APIView):
    permission_classes = [AllowAny]

    def get(self, request, item_id):
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        reviews = ItemReview.objects.filter(item=item).order_by("-created_at")

        paginator = Paginator(reviews, page_size)
        total_pages = paginator.num_pages

        try:
            paginated_reviews = paginator.page(page)
        except:
            return Response({"error": "Invalid page number"}, status=400)

        serializer = ItemReviewSerializer(paginated_reviews, many=True)

        return Response({
            "item_id": item_id,
            "current_page": page,
            "total_pages": total_pages,
            "total_reviews": paginator.count,
            "page_size": page_size,
            "reviews": serializer.data
        })

class SearchProductAPIView(APIView):
    def get(self, request):
        q = request.query_params.get('q', '').strip()
        paginator = SimplePagination()
        
        if not q or len(q) < 3:
            return Response(
                {"error": "Search query must be at least 3 characters long."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Perform case-insensitive partial search
            items = Item.objects.filter(title__icontains=q, status=True)

            if not items.exists():
                return Response(
                    {"message": "No products found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Paginate results
            paginated_items = paginator.paginate_queryset(items, request)
            serializer = ItemSerializer(paginated_items, many=True)

            # Return structured response
            response_data = {
                "total": items.count(),
                "results": serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# class CategoryAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # Get the category ID from the query parameters
#         category_id = request.query_params.get('category_id')

#         try:
#             # Get all items for the specified category ID
#             items = Item.objects.filter(category__id=category_id)

#             # Filter items where status is True using list comprehension
#             items = [item for item in items if item.status]

#             serializer = ItemSerializer(items, many=True)
#             return Response(serializer.data)
#         except Item.DoesNotExist:
#             return Response({"error": "Category does not exist"}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryFetch(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch all categories
            categories = Catagory.objects.all()

            # Use list comprehension to filter categories based on status
            categories = [category for category in categories if category.status]

            # Serialize the filtered categories
            category_serializer = CategorySerializer(categories, many=True)

            return Response(category_serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class CategoryfiveFetch(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch all categories
            categories = Catagory.objects.all()
            categories = [category for category in categories if category.status][:4]

            # Serialize the categories
            category_serializer = CategorySerializer(categories, many=True)

            return Response(category_serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DealOfTheDayfiveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Item.objects.filter(deal_of_the_day=True, status=True, stock__openingstock__gt=0)[:4]
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

class RecommendedfiveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Item.objects.filter(recommended=True, status=True, stock__openingstock__gt=0)[:4]
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

class MostPopularfiveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Item.objects.filter(most_popular=True, status=True, stock__openingstock__gt=0)[:4]
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)
class AllfiveProduct(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Item.objects.all()
        items = [item for item in items if item.status][:4]
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

class CategoryProAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch all categories
            categories = Catagory.objects.all()

            # Serialize the categories
            category_serializer = CategorySerializer(categories, many=True)

            # Fetch all products
            products = Item.objects.all()

            # Serialize the products
            product_serializer = ItemSerializer(products, many=True)

            # Combine categories and products in the response
            response_data = category_serializer.data

            # Add each product directly under "all"
            for product_data in product_serializer.data:
                response_data.append({"all": product_data})

            return Response(response_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class AuthCategoryFetch(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch all categories
            categories = Catagory.objects.all()

            # Use list comprehension to filter categories based on status
            categories = [category for category in categories if category.status]

            # Serialize the filtered categories
            category_serializer = CategorySerializer(categories, many=True)

            return Response(category_serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class AuthMostPopularAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Item.objects.filter(most_popular=True, status=True, stock__openingstock__gt=0)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

class AuthCategoryAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the category ID from the query parameters
        category_id = request.query_params.get('category_id')

        try:
            # Get all items for the specified category ID
            items = Item.objects.filter(category__id=category_id)

            # Filter items where status is True using list comprehension
            items = [item for item in items if item.status]

            serializer = ItemSerializer(items, many=True)
            return Response(serializer.data)
        except Item.DoesNotExist:
            return Response({"error": "Category does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AuthAllProduct(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Item.objects.all()
        items = [item for item in items if item.status]
        delivery_charge = DeliveryCharge.objects.first()
        if not delivery_charge:
            delivery_charge = 0
        else:
            delivery_charge = delivery_charge.charge
        serializer = ItemSerializer(items, many=True)
        data = serializer.data
        data.append({"DeliveryChange": delivery_charge})
        return Response(data)

class ProductsId(APIView):
    def get(self, request):
        pro_id = request.query_params.get('product_id')
        if not pro_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Item, id=pro_id)
        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

class VegItemListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        veg = request.query_params.get('veg')
        items = Item.objects.filter(veg=veg)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AuthVegItemListAPIView(APIView):
    def get(self, request):
        veg = request.query_params.get('veg')
        items = Item.objects.filter(veg=veg)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ItemSearchAPIView(APIView):
    def get(self, request):
        query = request.query_params.get('q', None)
        if query is not None:
            items = Item.objects.filter(title__icontains=query)
            serializer = ItemSerializer(items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Please provide a search query"}, status=status.HTTP_400_BAD_REQUEST)

class ItemBrandsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        brands = Item.objects.filter(status=True, brand_name__isnull=False).exclude(brand_name__exact='').values_list('brand_name', flat=True).distinct()
        return Response(brands, status=status.HTTP_200_OK)
