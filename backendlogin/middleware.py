from django.utils.decorators import decorator_from_middleware
from django.middleware.cache import CacheMiddleware


class RevalidateBackHistoryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add headers to revalidate back history
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = 'Fri, 01 Jan 1990 00:00:00 GMT'

        return response


# Decorator to apply the middleware to views
revalidate_back_history = decorator_from_middleware(RevalidateBackHistoryMiddleware)
