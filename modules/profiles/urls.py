from django.urls import re_path as url
from modules.profiles import views as profiles_view

urlpatterns = [
    url(r'^register/$', profiles_view.register_user),
    url(r'^login/$', profiles_view.login_user),
    url(r'^logout/$', profiles_view.close_session),
    url(r'^allusers/$', profiles_view.get_users),
    url(r'^getuser/$', profiles_view.get_user),
]