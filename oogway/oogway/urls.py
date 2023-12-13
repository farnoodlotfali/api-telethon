from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('analyze/', include('PostAnalyzer.urls')),
    path('panel/', include('Panel.urls')),
    path('admin/', admin.site.urls),
]
