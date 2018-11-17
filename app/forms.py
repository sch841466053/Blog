from django import forms
from captcha.fields import CaptchaField
from app import models
from django.core.exceptions import ValidationError
import re

class RegForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="邮箱",
        widget=forms.EmailInput(attrs={"class":"form-control","placeholder":"请输入邮箱"}),
        error_messages={
            "required": "邮箱不能为空"
        }
    )

    phone = forms.CharField(
        required=True,
        label="手机号",
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"请输入手机号码"}),
        error_messages={
            "required": "手机号不能为空"
        }

    )

    username = forms.CharField(
        required=True,
        min_length=5,
        label="用户名",
        widget=forms.widgets.TextInput(attrs={"class": "form-control","placeholder":"请输入用户名"}),
        error_messages={
            "min_length": "用户名不能少于5位",
            "required": "用户名不能为空",

        }
    )
    password = forms.CharField(
        required=True,
        min_length=5,
        label="密码",
        widget=forms.widgets.PasswordInput(attrs={"class":"form-control","placeholder":"请输入密码"}),
        error_messages={
            "min_length": "密码不少于5位",
            "required": "密码不能为空"
        }
    )
    re_password = forms.CharField(
        required=True,
        min_length=5,
        label="确认密码",
        widget=forms.widgets.PasswordInput(attrs={"class": "form-control","placeholder":"请确认密码"}),
        error_messages={
            "min_length": "密码不少于5位",
            "required": "确认密码不能为空"
        }
    )
    captcha = CaptchaField(label="验证码",
                           # widget=forms.widgets.TextInput(attrs={"placeholder":"请输入验证码"}),
                           error_messages={
                               "invalid": "验证码错误",
                               "required": "验证码不能为空"

                            }
                           )

    def clean(self):
        password = self.cleaned_data.get("password")
        re_password = self.cleaned_data.get("re_password")

        if re_password and re_password != password:
            self.add_error("re_password", ValidationError("两次密码不一致"))

        else:
            return self.cleaned_data


    def clean_username(self):
        username = self.cleaned_data.get("username")
        is_exist = models.BlogUser.objects.filter(username=username)
        if is_exist:
            # 表示用户名已注册
            self.add_error("username", ValidationError("用户名已存在"))
        else:
            return username

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        phone_re = re.compile(r'^(13|14|15|17|18)[0-9]{9}$')
        if not phone_re.match(phone):
            self.add_error("phone", ValidationError("手机号格式错误"))
        else:
            return phone