from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.http import JsonResponse
import logging
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class CustomAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A server error occurred.'
    default_code = 'error'

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        if isinstance(response.data, dict):
            response.data['status_code'] = response.status_code
        else:
            response.data = {
                'detail': response.data,
                'status_code': response.status_code
            }
    
    return response

def handle_500_error(request):
    logger.error("Internal Server Error occurred")
    return JsonResponse({
        'error': 'Internal Server Error',
        'status_code': 500
    }, status=500)

def handle_404_error(request, exception):
    logger.error(f"Not Found Error: {request.path}")
    return JsonResponse({
        'error': 'Not Found',
        'status_code': 404
    }, status=404) 