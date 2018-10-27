from django import forms
from captcha.fields import CaptchaField
from app import models
from django.core.exceptions import ValidationError

class RegForm(forms.Form):
    username = forms.CharField(
        required=True,
        min_length=5,
        label="用户名",
        error_messages={
            "min_length": "用户名不能少于5位",
            "required": "用户名不能为空"
        }
    )
    password = forms.CharField(
        required=True,
        min_length=5,
        label="密码",
        error_messages={
            "min_length": "密码不少于5位",
            "required": "密码不能为空"
        }
    )
    re_password = forms.CharField(
        required=True,
        min_length=5,
        label="确认密码",
        error_messages={
            "min_length": "密码不少于5位",
            "required": "确认密码不能为空"
        }
    )
    captcha = CaptchaField(label="验证码",
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
