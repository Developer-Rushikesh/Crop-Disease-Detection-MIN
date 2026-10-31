from django.urls import path
from . import views

app_name = 'detector'

urlpatterns = [
    # Page 1: Home Page
    path('', views.home_view, name='home'),
    
    # Page 2: Combined Upload, Prediction & On-Page Results
    path('upload/', views.upload_view, name='upload'),
    
    # Direct PDF Download Endpoint (triggers browser file download)
    path('download-report/', views.download_report_view, name='download_report'),
]
