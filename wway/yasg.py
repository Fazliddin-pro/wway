from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

info = openapi.Info(
    title="WisdomWay Education Platform API",
    default_version="v1.0",
    description=(
        "Welcome to the official API documentation for the **WisdomWay Education Platform**.\n\n"
        "This API allows developers to interact with core features such as course management, "
        "user authentication, module handling, and more.\n\n"
        "## Authentication\n"
        "Most endpoints require authentication. Use the login endpoint to obtain a token.\n\n"
        "## Rate Limiting\n"
        "API requests are limited to 100 requests per minute per IP address.\n\n"
        "## Error Handling\n"
        "All errors return a JSON response with an error message and status code."
    ),
    terms_of_service="https://www.wway.uz/terms/",
    contact=openapi.Contact(
        name="Wway Support Team",
        email="support@wway.com",
        url="https://www.wway.uz/contact/"
    ),
    license=openapi.License(name="Proprietary License"),
)

schema_view = get_schema_view(
    info,
    public=True,
    permission_classes=[permissions.AllowAny],
    validators=['flex', 'ssv'],
)

urlpatterns = [
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]
