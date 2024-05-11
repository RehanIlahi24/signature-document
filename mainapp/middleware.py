from django.http import JsonResponse
from .ip_validating import check_ip_blacklist

class IPAbuseCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        if ip_address:
            if check_ip_blacklist(ip_address) == False:
                return JsonResponse({'error': 'Your IP address has been blocked due to abuse.'}, status=403)
        response = self.get_response(request)
        return response
