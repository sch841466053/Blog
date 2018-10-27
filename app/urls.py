from django.conf.urls import url
from app import views

urlpatterns = [
    url(r"comment/",views.comment),
    url(r"^poll/$", views.up_down),
    url(r"^(\w+)/$", views.home),
    url(r"^(\w+)/article/(\d+)/", views.article_detail),

]