from django.urls import re_path as url
from modules.order import views as order_view

urlpatterns = [
    url(r'^createorder/$', order_view.save_car),
    url(r'^cancelorder/$', order_view.cancel_car),
    url(r'^history/$', order_view.history),
    url(r'^userhistory/$', order_view.historyUser),
    url(r'^providerhistory/$', order_view.historyProvider),
]