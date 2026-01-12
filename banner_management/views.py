from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Banner
from ecomApp.models  import Catagory
# Create your views here.
@login_required(login_url='backend/login')
def banner_list(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    items = Banner.objects.all()
    context = {
        'items': items
    }
    return render(request, 'backend/banner_list.html', context)

@login_required(login_url='backend/login')
def add_banner(request):
    if not request.user.is_staff:
        return redirect('backend/login')
    if request.method == "POST":
        title=request.POST.get('title')
        description=request.POST.get('description')
        add_photo = request.FILES.get('item_photo')
        category_id = request.POST.get('category')

        # Calculate item_new_price based on item_old_price and discount


        # Create the item object
        item = Banner.objects.create(
            title=title,
            description=description,
            add_photo=add_photo,
            status=True,
            category_id=category_id
        )
        return redirect('banner_list')

    # If the request method is not POST, render the form
    categories = Catagory.objects.all()
    return render(request, 'backend/add_banner.html', {'categories': categories})

@login_required(login_url='backend/login')
def activate_add(request, add_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(Banner, id=add_id)
    item.status = True
    item.save()
    return redirect('banner_list')

@login_required(login_url='backend/login')
def deactivate_add(request, add_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(Banner, id=add_id)
    item.status = False
    item.save()
    return redirect('banner_list')

@login_required(login_url='backend/login')
def delete_add(request, add_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(Banner, id=add_id)
    item.delete()
    return redirect('banner_list')

@login_required(login_url='backend/login')
def view_add(request, add_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    item = get_object_or_404(Banner, id=add_id)
    return render(request, 'backend/view_banner.html', {'item': item})

@login_required(login_url='backend/login')
def update_add(request, add_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    edit_item = get_object_or_404(Banner, id=add_id)

    try:
        item_photo = request.FILES.get('item_photo')
        if item_photo:
            edit_item.add_photo = item_photo
        edit_item.title = request.POST.get('title')
        edit_item.description = request.POST.get('description')
        edit_item.category_id = request.POST.get('category')  # Assuming you're passing category id from the form
        edit_item.save()
        return redirect('banner_list')  # Redirect to item list page after successful update
    except Exception as e:
            # If an error occurs during update, handle it here
        error_message = f'Error occurred while updating item: {e}'
        return render(request, 'backend/edit_banner.html', {'item': edit_item, 'message': error_message})

    return render(request, 'backend/edit_banner.html', {'item': edit_item})

@login_required(login_url='backend/login')
def edit_add(request, add_id):
    if not request.user.is_staff:
        return redirect('backend/login')
    sel_item = get_object_or_404(Banner, id=add_id)
    all_items = Banner.objects.all()
    categories = Catagory.objects.all()

    context = {
        'all_items': all_items,
        'item': sel_item,
        'categories':categories
    }
    return render(request, 'backend/edit_banner.html', context)
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Banner
from .serializers import BannerSerializer
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class BannerByCategoryAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the category_id from query parameters
            category_id = request.query_params.get('category_id')

            # Fetch banners for the specified category ID
            banners = Banner.objects.filter(category_id=category_id)

            # Filter banners with status=True
            active_banners = [banner for banner in banners if banner.status]

            # Serialize the filtered banners
            serializer = BannerSerializer(
                banners,
                many=True,
                context={'request': request}
            )
            return Response(serializer.data)
        except Banner.DoesNotExist:
            return Response({"error": "Banners for the specified category do not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)