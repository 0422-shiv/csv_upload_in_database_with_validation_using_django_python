from rest_framework_tracking.models import APIRequestLog
from django.shortcuts import render
from django.views import generic
# Create your views here.

class ApiTrackingView(generic.TemplateView):
    	def get(self, request, *args, **kwargs):
            get_tracking=APIRequestLog.objects.all().order_by('-id')
            return render(request, "api-tracking.html",{'get_tracking':get_tracking})
         	

