from django.urls import path
from .views import *


urlpatterns = [

    path('user-lists/', UserListsView.as_view(), name='user-lists'),
    path('user-uploads/<int:user_id>/', UserUploadsView.as_view(), name='user-uploads'),
    path('user-upload-details/<str:upload_identifier>/', UserUploadsDetailsView.as_view(), name='user-upload-details'),
    path('user-file-details/<str:csv_type>/<str:upload_identifier>/', UserFileDetailedDataView.as_view(), name='user-file-details-view'),

    ]

