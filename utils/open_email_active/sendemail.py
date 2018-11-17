import smtplib
from email.mime.text import MIMEText



#设置登录及服务器信息
#163邮箱服务器地址
mail_host = 'smtp.163.com'
#163用户名
mail_user = '13714628754'
#密码(部分邮箱为授权码)
mail_pass = 'SHANGchunhong022'
#邮件发送方邮箱地址
sender = '13714628754@163.com'
#邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发


#设置eamil信息
# #添加一个MIMEmultipart类，处理正文及附件
# message = MIMEMultipart()

#推荐使用html格式的正文内容，这样比较灵活，可以附加图片地址，调整格式等
def send_email(recev):
    with open('utils/open_email_active/demo.html','r',encoding="utf-8") as f:
        content = f.read()
    #设置html格式参数
    message = MIMEText(content,'html','utf-8')
    message['From'] = sender
    message['To'] = recev
    message['Subject'] = '这是一个测试的邮件'

    # #将内容附加到邮件主体中
    # message.attach(part1)


    #登录并发送
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host,25)
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(
            sender,recev,message.as_string())
        print('success')
        smtpObj.quit()
    except smtplib.SMTPException as e:
        print('error',e)