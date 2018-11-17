from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from app import forms
from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from app import models
from geetest import GeetestLib
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.conf import settings
# Create your views here.
from utils.open_email_active.sendemail import send_email
from utils.page import Pagination

def Index(request):
    category_list = models.Category.objects.all()
    current_page=request.GET.get("page",1)

    all_count=models.Article.objects.all().count()
    print(all_count)
    base_url=request.path  # /index/
    pagination = Pagination(int(current_page),all_count, base_url, request.GET, per_page_num=3, pager_count=6)
    article_list = models.Article.objects.all()[pagination.start:pagination.end]
    return render(request, "index.html",locals())


def Select(request,id):
    category_list = models.Category.objects.all()
    current_page = request.GET.get("page", 1)
    category = models.Category.objects.filter(nid=id).first()
    # article_list = models.Article.objects.filter(category=category)

    all_count=models.Article.objects.filter(category=category).count()
    print(all_count)
    base_url=request.path  # /index/
    pagination = Pagination(int(current_page),all_count, base_url, request.GET, per_page_num=3, pager_count=6)
    article_list = models.Article.objects.filter(category=category)[pagination.start:pagination.end]
    return render(request, "index.html",locals())

#form 表单提交数据

# def Register(request):
#     if request.method == "GET":
#         form = forms.RegForm()
#         return render(request, "register1.html", {"form": form})
#     print(request.POST)
#
#     form = forms.RegForm(request.POST)
#
#     if form.is_valid():
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         avatar = request.FILES.get("avatar")
#         user = models.BlogUser.objects.create_user(username=username, password=password,avatar=avatar)
#         return render(request,"index.html")
#     print(form.errors)
#     return render(request, "register1.html", {"form": form})

#ajax提交

def Register(request):
    if request.method == "POST":
            ret = {"status": 0, "msg": ""}
            form = forms.RegForm(request.POST)
            print(request.POST)
            # 帮我做校验
            if form.is_valid():
                # 校验通过，去数据库创建一个新的用户
                email = request.POST.get("email")
                phone = request.POST.get("phone")
                username = request.POST.get("username")
                password = request.POST.get("password")
                avatar = request.FILES.get("avatar","avatars/timg.jpg")
                # 发送激活邮件
                send_email(email)
                # 数据可创建一个新用户
                user = models.BlogUser.objects.create_user(username=username, password=password,avatar=avatar,email=email)


                ret["msg"] = "/login/"
                return JsonResponse(ret)
            else:
                print(form.errors)
                ret["status"] = 1
                ret["msg"] = form.errors
                print(ret)
                return JsonResponse(ret)

    form = forms.RegForm()
    print(form.fields)
    return render(request, "register.html", {"form": form})



def Login(request):
    if request.method == "POST":
        # 初始化一个给AJAX返回的数据
        ret = {"status": 0, "msg": ""}
        # 从提交过来的数据中 取到用户名和密码
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        # 获取极验 滑动验证码相关的参数
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]

        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            # 验证码正确
            # 利用auth模块做用户名和密码的校验
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确
                # 给用户做登录

                auth.login(request, user)
                ret["msg"] = "/index/"
            else:
                # 用户名密码错误
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
        else:
            ret["status"] = 1
            ret["msg"] = "验证码错误"

        return JsonResponse(ret)
    return render(request, "login.html")


def Logout(request):
    auth.logout(request)
    return redirect("/index/")

@login_required
def Modify_Password(request):
    if request.method == "GET":
        return render(request, "modify_password.html")
    flag = request.user.check_password(request.POST.get("password"))
    if flag:
        return render(request, "modify_password2.html")

    return HttpResponse("密码输入不正确")

@login_required
def Modify_Password2(request):
    if request.method == "POST":
        new_password = request.POST.get('new_password', '')  # 拿到新密码
        repeat_password = request.POST.get('repeat_password', '')
        if not new_password:  #
            return HttpResponse("新密码不能为空")
        elif new_password != repeat_password:  #
            return HttpResponse("两次密码不一致")
        else:
            request.user.set_password(new_password)
            request.user.save()
            return redirect("/login")
    return HttpResponse("只接受get请求")


pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"
def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    print(99999)
    return HttpResponse(response_str)


def get_left_menu(username):
    user = models.BlogUser.objects.filter(username=username).first()
    blog = user.blog
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
    # 按日期归档
    archive_list = models.Article.objects.filter(user=user).extra(
        select={"archive_ym": "date_format(create_time,'%%Y-%%m')"}
    ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym", "c")

    return category_list, tag_list, archive_list


def home(request, username):
    user = models.BlogUser.objects.filter(username=username).first()
    blog = user.blog
    article_list = models.Article.objects.filter(user=user)
    category_list, tag_list, archive_list = get_left_menu(username)
    return render(request, "home.html", {
        "user":user,
        "blog":blog,
        "article_list":article_list,
        "category_list": category_list,
        "tag_list": tag_list,
        "archive_list": archive_list,

    })


def article_detail(request, username, pk):
    print(username, pk)
    article_obj = models.Article.objects.filter(pk=pk).first()
    user = models.BlogUser.objects.filter(username=username).first()
    blog = user.blog
    category_list, tag_list, archive_list = get_left_menu(username)
    # 所有评论列表

    comment_list=models.Comment.objects.filter(article_id=pk)
    return render(request,"article_detail.html", {
        "article": article_obj,
        "blog": blog,
        "category_list": category_list,
        "tag_list": tag_list,
        "archive_list": archive_list,
        "comment_list": comment_list
    })


import json
from django.db.models import F

def up_down(request):
    print(request.POST)
    article_id = request.POST.get('article_id')
    is_up = json.loads(request.POST.get('is_up'))
    user = request.user
    response = {"state": True}
    print("is_up", is_up)
    try:
        models.ArticleUpDown.objects.create(user=user, article_id=article_id, is_up=is_up)
        if is_up:

            models.Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
        else:

            models.Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)
    except Exception as e:
        response["state"] = False
        print(666)
        response["fisrt_action"] = models.ArticleUpDown.objects.filter(user=user, article_id=article_id).first().is_up

    return JsonResponse(response)
    # return HttpResponse(json.dumps(response))


def comment(request):

    print(request.POST)

    pid=request.POST.get("pid")
    article_id=request.POST.get("article_id")
    content=request.POST.get("content")
    user_pk=request.user.pk
    response={}
    if not pid:  #根评论
        comment_obj=models.Comment.objects.create(article_id=article_id,user_id=user_pk,content=content)
    else:
        comment_obj=models.Comment.objects.create(article_id=article_id,user_id=user_pk,content=content,parent_comment_id=pid)

    comment_count = models.Article.objects.get(nid=article_id).comment_count + 1
    models.Article.objects.filter(nid=article_id).update(comment_count=comment_count)

    response["create_time"]=comment_obj.create_time.strftime("%Y-%m-%d")
    response["content"]=comment_obj.content
    response["username"]=comment_obj.user.username

    return JsonResponse(response)


def comment_tree(request,article_id):

    ret=list(models.Comment.objects.filter(article_id=article_id).values("pk","content","parent_comment_id"))
    print(ret)
    return JsonResponse(ret,safe=False)


def add_article(request):

    if request.method=="POST":
        title=request.POST.get('title')
        article_content=request.POST.get('article_content')
        user=request.user

        from bs4 import BeautifulSoup

        bs=BeautifulSoup(article_content,"html.parser")
        desc=bs.text[0:150]+"..."


        # 过滤非法标签
        for tag in bs.find_all():

            print(tag.name)

            if tag.name in ["script", "link"]:
                tag.decompose()

        article_obj=models.Article.objects.create(user=user,title=title,desc=desc)
        models.ArticleDetail.objects.create(content=str(bs),article=article_obj)


        return redirect("/index/")




    return render(request,"add_article.html")


def edit_article(request,id):

    if request.method=="POST":
        article = models.Article.objects.filter(nid=id)
        title=request.POST.get('title')
        article_content=request.POST.get('article_content')
        user=request.user

        from bs4 import BeautifulSoup

        bs=BeautifulSoup(article_content,"html.parser")
        desc=bs.text[0:150]+"..."


        # 过滤非法标签
        for tag in bs.find_all():

            print(tag.name)

            if tag.name in ["script", "link"]:
                tag.decompose()

        article_obj=article.update(user=user,title=title,desc=desc)
        article_detail_obj = article.first().articledetail

        article_detail_obj.content = str(bs)
        article_detail_obj.article = article.first()
        article_detail_obj.save()


        return redirect("/index/")

    article = models.Article.objects.filter(nid=id).first()
    return render(request,"edit_article.html",{"article":article})

import os
def upload(request):
    print(request.FILES)
    obj = request.FILES.get("upload_img")

    print("name",obj.name)

    path=os.path.join(settings.MEDIA_ROOT,"article_img",obj.name)

    with open(path,"wb") as f:
        for line in obj:
            f.write(line)


    res={
        "error":0,
        "url":"/media/article_img/"+obj.name
    }


    return HttpResponse(json.dumps(res))


from utils.get_phone_code.default import sendTemplateSMS
def get_phone_code(request):
    ret = {"code": 10000}
    phone = request.POST.get("phone")
    print(phone,type(phone))
    s = sendTemplateSMS(phone,'',1)
    print(s)
    return JsonResponse(ret)


