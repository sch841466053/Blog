from django.conf.urls import url
from app import views

urlpatterns = [
    url(r"^get_phone_code/$",views.get_phone_code),
    url(r"backend/add_article/",views.add_article),
    url(r"backend/edit_article/(\d+)/",views.edit_article),
    url(r'comment_tree/(\d+)/', views.comment_tree),
    url(r"comment/",views.comment),
    url(r"^poll/$", views.up_down),
    url(r"^(\w+)/$", views.home),
    url(r"^(\w+)/article/(\d+)/", views.article_detail),


]