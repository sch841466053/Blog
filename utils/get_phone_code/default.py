
from utils.get_phone_code.getcode_sdk import REST
accountSid= '8aaf070866235bc501667678bbba2bd4'
accountToken= '510275b77fe1474cac9cdbf0459d70f9'

appId='8aaf070866235bc501667678bc0b2bda'
serverIP='app.cloopen.com'
serverPort='8883'
softVersion='2013-12-26'


def sendTemplateSMS(to, datas, tempId):
    # 初始化REST SDK
    rest = REST(serverIP, serverPort, softVersion)
    rest.setAccount(accountSid, accountToken)
    rest.setAppId(appId)

    result = rest.sendTemplateSMS(to, datas, tempId)
    dict = {}
    for k, v in result.items():

        if k == 'templateSMS':
            for k, s in v.items():
                # print('%s:%s' % (k, s))
                dict[k] = s
        else:
            # print('%s:%s' % (k, v))
            dict[k] = v
    return dict