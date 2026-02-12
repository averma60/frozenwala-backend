from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, Whishlist
from .serializers import CartSerializer,CartGetSerializer, WishlistSerializer
from ecomApp.models import CustomUser
from menu_management.models import Item
from rest_framework.permissions import IsAuthenticated
from walet.models import Walet

from django.utils.timezone import now
from ecomApp.models import CustomerCoupon
from registration.models import AddressAdmin
from .utils import item_stock_quantity

class AddToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # old code
            product_id = request.data.get('product_id')
            u_id = request.data.get('u_id')

            if product_id or u_id: 
                product = Item.objects.filter(id=product_id).first()
                if not product:
                    return Response({"error": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND)
                user = CustomUser.objects.filter(id=u_id).first()
                if not user:
                    return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
                cart_items = Cart.objects.filter(product_id=product, u_id=user)
                if cart_items.exists():
                    cart_item = cart_items.first()
                    cart_item.quantity += 1
                    cart_item.price = cart_item.quantity * product.item_new_price
                else:
                    cart_item = Cart.objects.create(product_id=product, u_id=user, quantity=1,
                                                    price=product.item_new_price)
                cart_item.save()
                serializer = CartSerializer(cart_item)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # new code
                cart = request.data.get('cart')
                user_id = request.data.get('user_id')
                user = CustomUser.objects.filter(id=user_id).first()
                if not user:
                    return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
                for product in cart:
                    item = Item.objects.filter(id=product['id']).first()
                    if item:
                        cart_item = Cart.objects.filter(product_id=item, u_id=user)
                        stock = item_stock_quantity(item.id)
                        if cart_item and cart_item.quantity < stock:
                            cart_item.quantity = cart_item.quantity + product['qty']
                            cart_item.price = item.item_new_price * cart_item.quantity
                            cart_item.save()
                        elif not cart_item:
                            if int(product['qty']) < stock:
                                price = item.item_new_price * int(product['qty'])
                                quantity = product['qty']
                            else:
                                price = item.item_new_price
                                quantity = 1
                            Cart.objects.create(product_id=item, u_id=user, quantity=quantity, price=price)
                        else:
                            return Response({"error": "Out of stock"}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'status': True}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
class CartDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the user_id from query parameters
            user_id = request.query_params.get('user_id')

            # Validate user_id parameter
            if not user_id:
                return Response({"error": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve all cart items for the specified user_id
            cart_items = Cart.objects.filter(u_id=user_id)

            # Serialize the cart items
            serializer = CartSerializer(cart_items, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetAllCouponAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:    
            today = now().date()
            coupons = CustomerCoupon.objects.filter(expire_date__gte=today)
            data = []
            for c in coupons:
                data.append({
                    "coupon": c.coupon,
                    "coupon_type": c.coupon_type,
                    "coupon_value": c.coupon_value,
                    "minimum_purchase": c.minimum_purchase,
                    "description": c.description,
                })

            if data:
                return Response({
                    "status": True,
                    "coupons": data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": False,
                    "coupons": data
                }, status=status.HTTP_200_OK)
                        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ApplyCouponAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            coupon_code = request.data.get("coupon_code")
            cart_value = request.data.get("cart_value")

            if not coupon_code or not cart_value:
                return Response({
                    "status": False,
                    "message": "coupon_code and cart_value are required"
                }, status=status.HTTP_400_BAD_REQUEST)

            cart_value = float(cart_value)
            today = now().date()
            try:
                coupon = CustomerCoupon.objects.get(
                    coupon=coupon_code,
                    start_date__lte=today,
                    expire_date__gte=today
                )
            except CustomerCoupon.DoesNotExist:
                return Response({
                    "status": False,
                    "message": "Invalid or expired coupon"
                }, status=status.HTTP_200_OK)

            if coupon.minimum_purchase:
                if cart_value < float(coupon.minimum_purchase):
                    return Response({
                        "status": False,
                        "message": f"Minimum purchase required is {coupon.minimum_purchase}"
                    }, status=status.HTTP_200_OK)

            discount = 0
            if coupon.coupon_type == "Percentage":
                discount = (cart_value * float(coupon.coupon_value)) / 100
                if discount > coupon.max_amount_discount:
                    discount = coupon.max_amount_discount

            elif coupon.coupon_type == "Flat":
                discount = float(coupon.coupon_value)

            final_price = max(cart_value - discount, 0)

            return Response({
                "status": True,
                "coupon_code": coupon_code,
                "discount": round(discount, 2),
                "final_price": round(final_price, 2),
                "message": "Coupon applied successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from ecomApp.models import Stock
class IncreaseQuantity(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart_id = request.data.get('cart_id')

            # Retrieve the cart item
            cart_item = Cart.objects.get(id=cart_id)

            stock = item_stock_quantity(cart_item.product_id.id)

            # Check if quantity is less than opening stock
            if cart_item.quantity < stock:
                # Increment quantity
                cart_item.quantity += 1
                cart_item.save()

                # Update total price
                cart_item.price = cart_item.product_id.item_new_price * cart_item.quantity
                cart_item.save()

                return Response({"message": "Quantity increased successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Quantity cannot be increased beyond opening stock."},
                                status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class DecreaseQuantity(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         try:
#             cart_id = request.data.get('cart_id')
#
#             # Retrieve the cart item
#             cart_item = Cart.objects.get(id=cart_id)
#
#             # Ensure quantity is greater than 1 before decrementing
#             if cart_item.quantity > 1:
#                 # Decrement quantity
#                 cart_item.quantity -= 1
#                 cart_item.save()
#
#                 # Update total price
#                 cart_item.price = cart_item.product_id.item_new_price * cart_item.quantity
#                 cart_item.save()
#
#                 return Response({"message": "Quantity decreased successfully."}, status=status.HTTP_200_OK)
#             else:
#                 cart_item.delete()
#                 return Response({"error": "Quantity cannot be less than 1."}, status=status.HTTP_400_BAD_REQUEST)
#         except Cart.DoesNotExist:
#             return Response({"error": "Cart item does not exist."}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#new
class DecreaseQuantity(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart_id = request.data.get('cart_id')

            # Retrieve the cart item
            cart_item = Cart.objects.get(id=cart_id)

            if cart_item.quantity > 1:
                # Decrement quantity
                cart_item.quantity -= 1
                cart_item.save()

                # Update total price
                cart_item.price = cart_item.product_id.item_new_price * cart_item.quantity
                cart_item.save()

                return Response({"message": "Quantity decreased successfully."}, status=status.HTTP_200_OK)
            else:
                cart_item.delete()
                return Response({"error": "Quantity cannot be less than 1."}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class RemoveCartItem(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def delete(self, request):
#         try:
#             cart_id = request.query_params.get('cart_id')
#
#             # Check if cart_id parameter is provided and if it's a valid integer
#             if not cart_id.isdigit():
#                 return Response({"error": "Valid cart_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
#
#             # Retrieve the cart item
#             cart_item = Cart.objects.get(id=int(cart_id))
#
#             # Delete the cart item
#             cart_item.delete()
#
#             return Response({"message": "Cart item removed successfully."}, status=status.HTTP_204_NO_CONTENT)
#         except Cart.DoesNotExist:
#             return Response({"error": "Cart item does not exist."}, status=status.HTTP_404_NOT_FOUND)
#         except ValueError:
#             return Response({"error": "Invalid cart_id provided."}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#new
class RemoveCartItem(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            cart_id = request.query_params.get('cart_id')
            cart_id=int(cart_id)

            # Check if cart_id parameter is provided and if it's a valid integer
            # if not cart_id.isdigit():
            #     return Response({"error": "Valid cart_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the cart item
            cart_item = Cart.objects.get(id=int(cart_id))
            # wallet = Walet.objects.get(user_id=cart_item.u_id.id)
            # # wallet_value = wallet.wallet_value  # Get the wallet value before deleting
            #
            # # Delete the wallet
            # wallet.delete()
            # wallet = Walet.objects.get(user_id=cart_item.u_id.id)
            try:
                wallet = Walet.objects.get(user_id=cart_item.u_id.id)
                # wallet_value = wallet.wallet_value  # Get the wallet value before deleting

                # Delete the wallet
                wallet.delete()

                # Add wallet value back to CustomUser's walet
                # new
                # user.walet += wallet_value
                # user.save()
                pass

                # return Response({"success": "Wallet deleted successfully and amount added back to user's wallet."},
                #                 status=200)

            except Walet.DoesNotExist:
                pass
            cart_item.delete()

            return Response({"message": "Cart item removed successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({"error": "Invalid cart_id provided."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# class CartTotalPrice(APIView):
#     def get(self, request):
#         try:
#             # Get the user_id from query parameters
#             user_id = request.query_params.get('user_id')
#
#             # Check if user_id parameter is provided
#             if user_id is None:
#                 return Response({"error": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
#
#             # Check if user_id is a valid integer
#             if not str(user_id).isdigit():
#                 return Response({"error": "Valid user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
#
#             # Retrieve all cart items for the specified user_id
#             cart_items = Cart.objects.filter(u_id=user_id)
#
#             # Calculate total price by summing the prices of all cart items
#             total_price = sum(cart_item.price for cart_item in cart_items)
#
#             return Response({"total_price": total_price}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
from datetime import date
from django.utils import timezone
from ecomApp.models import CustomerCoupon,DeliveryCharge
from order.models import Order
from .models import CartCoupon
import math
from walet.models import Walet
import math

class CartTotalPrice(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            pick_up = request.query_params.get('pick_up')
            coupon_value_param = request.query_params.get('coupon_code')
            used_wallet = request.query_params.get('used_wallet')

            gst_amount = 0
            cgst = 0
            sgst = 0
            
            gst_rate = AddressAdmin.objects.first().gst_rate if AddressAdmin.objects.first() else 0

            if pick_up == '1':
                delivery_charge = 0
            else:
                delivery_charge = DeliveryCharge.objects.first().charge

            user_id = request.query_params.get('user_id')

            if user_id is None:
                return Response({"error": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

            if not str(user_id).isdigit():
                return Response({"error": "Valid user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

            cart_items = Cart.objects.filter(u_id=user_id)
            total_price = sum(cart_item.price for cart_item in cart_items)
            previous_price = total_price
            discounted_price = 0
            today_date = date.today()

            if gst_rate:
                for item in cart_items:
                    gst_amount += (item.price * item.quantity) * gst_rate / 100
                gst_amount = round(gst_amount, 2)
                cgst = round(gst_amount / 2, 2)
                sgst = round(gst_amount / 2, 2)

            try:
                # coupon_value_param = CartCoupon.objects.get(user_id=user_id).coupon_code

                if coupon_value_param:
                    try:
                        coupon = CustomerCoupon.objects.get(
                            coupon=coupon_value_param,
                            start_date__lte=today_date,
                            expire_date__gte=today_date
                        )

                        if coupon.minimum_purchase:
                            if total_price >= float(coupon.minimum_purchase):                                  
                                if coupon.coupon_type == "Percentage":
                                    discounted_price = (total_price * float(coupon.coupon_value)) / 100
                                    if discounted_price > coupon.max_amount_discount:
                                        discounted_price = coupon.max_amount_discount

                                elif coupon.coupon_type == "Flat":
                                    discounted_price = float(coupon.coupon_value)

                                total_price = max(total_price - discounted_price, 0)                       
                    except CustomerCoupon.DoesNotExist:
                        pass
            except CartCoupon.DoesNotExist:
                pass

            total_price = math.ceil(total_price * 100) / 100
            previous_price = math.ceil(previous_price * 100) / 100
            discounted_price = math.ceil(discounted_price * 100) / 100
            if delivery_charge:
                delivery_charge = math.ceil(delivery_charge * 100) / 100

            rounded_total_price = total_price


            wallet_value = 0
            current_wallet = 0

            if delivery_charge:
                total_price += delivery_charge

            if used_wallet:

                try:
                    wallet = Walet.objects.get(user_id=user_id)
                    wallet_value = float(wallet.wallet_value)
                    total_price -= wallet_value
                except Walet.DoesNotExist:
                    wallet_value = None

                user_wallet = CustomUser.objects.get(id=user_id).walet
                if wallet_value is not None:
                    current_wallet = user_wallet - wallet_value
                else:
                    current_wallet = user_wallet

            return Response({
                "total_price": rounded_total_price,
                "previous_price": previous_price,
                "discounted_price": discounted_price,
                "delivery_charge": delivery_charge if delivery_charge else 0,
                "wallet_value": wallet_value or 0,
                "current_wallet": current_wallet,

                # GST fields
                "gst_rate": gst_rate,
                "cgst_amount": cgst,
                "sgst_amount": sgst,
                "total_gst": gst_amount,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from .models import CartCoupon
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_coupon(request):
    if request.method == 'POST':
        user_id = request.data.get('user_id')
        print("Received user_id:", user_id)  # Log the received user_id for debugging

        coupon = request.data.get('coupon')

        try:
            user = CustomUser.objects.get(id=user_id)
            try:
                existing_coupon = CartCoupon.objects.get(user_id=user.id)
                existing_coupon.coupon_code = coupon
                existing_coupon.save()
                message = 'Coupon updated successfully'
            except CartCoupon.DoesNotExist:
                coupon = CartCoupon.objects.create(user_id=user.id, coupon_code=coupon)
                message = 'Coupon sent successfully'
            return JsonResponse({'message': message})
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)



class IncreaseQuantityMain(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            product_id = request.data.get('product_id')
            user_id = request.data.get('user_id')
            
            user = CustomUser.objects.filter(id=user_id).first()
            if not user:
                return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

            # Retrieve the cart item
            cart_item = Cart.objects.get(product_id=product_id, u_id=user_id)

            stock = item_stock_quantity(product_id)

            # Check if quantity is less than opening stock
            if cart_item.quantity < stock:
                # Increment quantity
                cart_item.quantity += 1
                cart_item.save()

                # Update total price
                cart_item.price = cart_item.product_id.item_new_price * cart_item.quantity
                cart_item.save()

                cart_items = Cart.objects.filter(u_id=user_id)
                serializer = CartSerializer(cart_items, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Quantity cannot be increased beyond opening stock."},
                                status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            item = Item.objects.filter(id=product_id).first()
            Cart.objects.create(product_id=item, u_id=user, quantity=1, price=item.item_new_price)
            cart_items = Cart.objects.filter(u_id=user)
            serializer = CartSerializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# class DecreaseQuantityMain(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         try:
#             product_id = request.data.get('product_id')
#             user_id = request.data.get('user_id')
#
#             action = request.data.get('action')
#
#             if action == 'remove':
#                 Cart.objects.filter(product_id=product_id, u_id=user_id).first().delete()
#                 cart_items = Cart.objects.filter(u_id=user_id)
#                 serializer = CartSerializer(cart_items, many=True)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#
#             # Retrieve the cart item
#             cart_item = Cart.objects.get(product_id=product_id, u_id=user_id)
#
#             # Ensure quantity is greater than 1 before decrementing
#             if cart_item.quantity > 1:
#                 # Decrement quantity
#                 cart_item.quantity -= 1
#                 cart_item.save()
#
#                 # Update total price
#                 cart_item.price = cart_item.product_id.item_new_price * cart_item.quantity
#                 cart_item.save()
#
#                 cart_items = Cart.objects.filter(u_id=user_id)
#                 serializer = CartSerializer(cart_items, many=True)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 cart_item.delete()
#                 cart_items = Cart.objects.filter(u_id=user_id)
#                 serializer = CartSerializer(cart_items, many=True)
#                 return Response({"error": "Quantity cannot be less than 1." ,"status":0, "data": serializer.data}, status=status.HTTP_200_OK)
#         except Cart.DoesNotExist:
#             return Response({"error": "Cart item does not exist." ,"status":0}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#new
class DecreaseQuantityMain(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Retrieve product_id, user_id, and action from the request
            product_id = request.data.get('product_id')
            user_id = request.data.get('user_id')
            action = request.data.get('action')

            # Ensure user_id is provided
            # if not user_id:
            #     return Response({"error": "User ID parameter is required"}, status=400)

            # Check if user exists
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({"error": "User does not exist."}, status=404)

            # Check if wallet exists for the user

            if action == 'remove':
                # If action is 'remove', delete the cart item
                Cart.objects.filter(product_id=product_id, u_id=user_id).first().delete()


                # Get the updated list of cart items
                cart_items = Cart.objects.filter(u_id=user_id)
                serializer = CartSerializer(cart_items, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            # Retrieve the cart item
            cart_item = Cart.objects.get(product_id=product_id, u_id=user_id)

            # Ensure quantity is greater than 1 before decrementing
            if cart_item.quantity > 1:
                # Decrement quantity
                cart_item.quantity -= 1
                cart_item.save()

                # Update total price based on the new quantity
                cart_item.price = cart_item.product_id.item_new_price * cart_item.quantity
                cart_item.save()

                # Get the updated list of cart items
                cart_items = Cart.objects.filter(u_id=user_id)
                serializer = CartSerializer(cart_items, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # If quantity is 1 or less, delete the cart item
                cart_item.delete()

                # Get the updated list of cart items
                cart_items = Cart.objects.filter(u_id=user_id)
                serializer = CartSerializer(cart_items, many=True)
                return Response({
                    "error": "Quantity cannot be less than 1.",
                    "status": 0,
                    "data": serializer.data
                }, status=status.HTTP_200_OK)

        except Cart.DoesNotExist:
            return Response({"error": "Cart item does not exist.", "status": 0}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class CartDetailsMainAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the user_id from query parameters
            user_id = request.query_params.get('user_id')
            product_id = request.query_params.get('product_id')

            # Validate user_id parameter
            if not user_id:
                return Response({"error": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve all cart items for the specified user_id
            cart_items = Cart.objects.filter(u_id=user_id,product_id=product_id)

            if not cart_items.exists():
                return Response(
                    {"message": "No cart items found for this user and product"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Serialize the cart items
            serializer = CartGetSerializer(cart_items, many=True)

            return Response(serializer.data[0], status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UniqueProductCount(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_id = request.query_params.get('user_id')

            # Query the Cart table to get the count of unique products for the given user_id
            unique_product_count = Cart.objects.filter(u_id=user_id).values('product_id').distinct().count()
            return Response({'unique_product_count': unique_product_count}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'error': 'User does not have any products in the cart.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

            wishlist_items = Whishlist.objects.filter(user=request.user)
            serializer = WishlistSerializer(wishlist_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

            item_id = request.data.get('item_id')
            item = Item.objects.filter(id=item_id).first()
            if not item:
                return Response({"error": "Item does not exist."}, status=status.HTTP_404_NOT_FOUND)
            
            wishlist_item = Whishlist.objects.filter(user=request.user, item=item).first()
            if wishlist_item:
                wishlist_item.delete()
                return Response({"message": "Item removed from wishlist."}, status=status.HTTP_200_OK)
            else:
                Whishlist.objects.create(user=request.user, item=item)
            serializer = WishlistSerializer(wishlist_item)
            return Response({"message": "Item added to wishlist.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
