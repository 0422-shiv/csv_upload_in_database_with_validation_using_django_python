"""uwa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from rest_framework.documentation import include_docs_urls
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.static import static
from django.conf import settings
...

schema_view = get_schema_view(
   openapi.Info(
      title="UWA API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.uwa.com/policies/terms/",
      contact=openapi.Contact(email="contact@uwa.local"),
      license=openapi.License(name="uwa License"),
    ),
   public=True,
   permission_classes=(permissions.AllowAny,),
  
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/user/', include('accounts.urls')),
    path('api/v1/file-upload/', include(('data_upload.urls', 'data_upload'), namespace='data_upload')),
    path('api/v1/my-uploads/', include(('my_uploads.urls', 'my_uploads'), namespace='my_uploads')),
    path('api/v1/dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),


    path('api/v1/admin-accounts/', include(('admin_accounts.urls', 'admin_accounts'), namespace='admin_accounts')),
    path('api/v1/admin-user-lists/', include(('admin_user_lists.urls', 'admin_user_lists'), namespace='admin_user_lists')),
    path('api/v1/admin-data-lists/', include(('admin_data_lists.urls', 'admin_data_lists'), namespace='admin_data_lists')),
    path('api/v1/admin-dashboard/', include(('admin_dashboard.urls', 'admin_dashboard'), namespace='admin_dashboard')),

    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    path('api-tracking/', include(('api_tracking.urls', 'api_tracking'), namespace='api_tracking')),



  
      
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

