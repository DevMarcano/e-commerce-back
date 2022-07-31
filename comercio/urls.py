# -*- coding: UTF-8 -*
from django.urls import re_path as url
from django.conf.urls import include, handler404
from comercio.views import HomePageView, handle404
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
	url(r'^$',HomePageView.as_view()),
    url(r'^api/v1/profiles/', include('modules.profiles.urls')),
    url(r'^api/v1/products/', include('modules.products.urls')),
    url(r'^api/v1/order/', include('modules.order.urls')),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


handler404 = handle404
