"""application URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
import debug_toolbar
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.urls.conf import re_path

from application import settings

urlpatterns = [
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    path('admin/', admin.site.urls, name='admin'),
    path('', include('authenticator.urls')),
    path('', include('store.urls')),
    path('', include('cart.urls')),
    path('', include('order.urls')),
    path('', include('consultation.urls')),
    path('', include('userprofile.urls')),
    path('', include('waitinglist.urls')),
    path('', include('pay.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]

# handler404 = 'store.views.custom_404'

if settings.DEBUG:
    if settings.MEDIA_ROOT:
        urlpatterns += static(settings.MEDIA_URL,
            document_root=settings.MEDIA_ROOT)

    urlpatterns += staticfiles_urlpatterns()
