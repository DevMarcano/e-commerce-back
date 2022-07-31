from django.urls import re_path as url
from modules.products import views as products_view

urlpatterns = [
    # productos
    url(r'^createproduct/$', products_view.register_Product),
    url(r'^updateproduct/$', products_view.update_Product),
    url(r'^getproducts/$', products_view.get_Products ),
    url(r'^getproduct/$', products_view.get_Product),
    url(r'^byprovider/$', products_view.get_Products_by_Provider),
    url(r'^bycategory/$', products_view.get_Products_by_category),
    url(r'^byname/$', products_view.get_Products_by_Search_Name),

    #category
    url(r'^createcategory/$', products_view.create_Category),
    url(r'^updatecategory/$', products_view.update_Category),
    url(r'^getcategorys/$', products_view.get_categorys),

    #providers
    url(r'^createprovider/$', products_view.create_Provider),
    url(r'^updateprovider/$', products_view.update_Provider),
    url(r'^getproviders/$', products_view.get_providers),

]