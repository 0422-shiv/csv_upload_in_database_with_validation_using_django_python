
from django.urls import path
from . import views


urlpatterns = [
    path('', views.CsvUpload.as_view() , name='CsvUpload'),
    path('validate-matching', views.ValidateMatching.as_view() , name='ValidateMatching'),
    path('column-header-matching', views.ColumnHeaderMatching.as_view() , name='ColumnHeaderMatching'),
    path('track-map/<str:upload_identifier>', views.MapView.as_view() , name='MapView'),
    path('license/', views.licenseView.as_view() , name='licenseView'),
    path('post-license/', views.PostFilelicenseView.as_view() , name='PostFilelicenseView'),
    path('draft/', views.DraftView.as_view() , name='DraftView'),
    path('draft-details/', views.DraftDetailsView.as_view() , name='DraftDetailsView'),
    path('draft-discard/<str:upload_identifier>', views.DraftDiscardView.as_view() , name='DraftDiscardView'),

    path('re-upload/', views.ReUploadView.as_view() , name='ReUploadView'),


]