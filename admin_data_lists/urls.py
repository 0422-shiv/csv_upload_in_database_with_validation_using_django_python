from django.urls import path
from .views import *


urlpatterns = [

    path('', AllDataListView.as_view(), name='all-data'),
    path('user-data-detail/<str:upload_identifier>/', UserDataDetailView.as_view(), name='user-data-detail'),

    
    path('all-three-file-download/<str:upload_identifier>/', AllThreeFileDownloadListAPIView.as_view() , name='AllThreeFileDownload'),
    path('single_file-download/<str:upload_identifier>/<str:csv_type>/', FileDownloadListAPIView.as_view() , name='FileDownload'),

    ]

