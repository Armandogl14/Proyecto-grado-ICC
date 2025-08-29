"""
Custom middleware for security and monitoring
"""
import logging
from django.http import HttpResponseBadRequest
from django.core.exceptions import DisallowedHost
from django.conf import settings

logger = logging.getLogger('django.security')

class SecurityMiddleware:
    """
    Custom middleware to handle security issues and log suspicious activity
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        return response
        
    def process_exception(self, request, exception):
        """Handle DisallowedHost exceptions with detailed logging"""
        if isinstance(exception, DisallowedHost):
            host = request.META.get('HTTP_HOST', 'unknown')
            ip = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
            
            logger.warning(
                f"Blocked suspicious host: {host} from IP: {ip} "
                f"User-Agent: {user_agent} Path: {request.path}"
            )
            
            # Return a generic bad request instead of exposing Django error
            return HttpResponseBadRequest("Bad Request")
        
        return None
    
    def get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
