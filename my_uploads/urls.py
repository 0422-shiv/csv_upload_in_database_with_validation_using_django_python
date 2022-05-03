
from django.urls import path
from . import views


urlpatterns = [
  
     path('', views.MyUploadView.as_view() , name='MyUploadView'),
     path('file-detailed-data/<str:csv_type>/<str:upload_identifier>/', views.FileDetailedDataView.as_view() , name='FileDetailedDataView'),
     path('upload-detail/<str:upload_identifier>/', views.MyUploadsDetailsView.as_view() , name='MyUploadsDetailsView'),

      path('all-three-file-download/<str:upload_identifier>/', views.AllThreeFileDownloadListAPIView.as_view() , name='AllThreeFileDownload'),
     path('single_file-download/<str:upload_identifier>/<str:csv_type>/', views.FileDownloadListAPIView.as_view() , name='FileDownload'),

]