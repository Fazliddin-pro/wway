from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="WisdomWay Education Platform API",
        default_version="v1.0",
        description=(
            "Welcome to the official API documentation for the **WisdomWay Education Platform**.\n\n"
            "This API allows developers to interact with core features such as course management, "
            "user authentication, module handling, and more."
        ),
        # terms_of_service="https://www.wway.uz/terms/",
        terms_of_service="https://www.wway.uz/",
        contact=openapi.Contact(
            name="Wway Support Team",
            email="support@wway.com",
            # url="https://www.wway.uz/contact/"
            url="https://t.me/FazlCode"
        ),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Define URL patterns for Swagger and ReDoc
urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
