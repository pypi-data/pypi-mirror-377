#!/usr/bin/env python
# coding:utf-8

import requests
from hashlib import md5

class Chaojiying_Client(object):
    """
    超级鹰验证码识别客户端
    文档：https://www.chaojiying.com/api-5.html
    """

    def __init__(self, username, password, soft_id):
        """
        初始化
        :param username: 超级鹰用户名
        :param password: 超级鹰用户密码
        :param soft_id: 软件ID(在用户中心, 软件ID处可以生成)
        """
        self.username = username
        password =  password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()

    def PostPic_base64(self, base64_str, codetype):
        """
        base64_str: 图片base64编码字符串
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        # 预处理满足传递格式，不要图片前缀 data:image/jpeg;base64,
        base64_str = base64_str.split(',')[-1]
        params = {
            'codetype': codetype,
            'file_base64':base64_str
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        识别错误后进行返分
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()

    def GetScore(self):
        """
        获取当前账号的题分
        """
        r = requests.post('https://upload.chaojiying.net/Upload/GetScore.php', data=self.base_params, headers=self.headers)
        return r.json()


if __name__ == '__main__':
    #用户中心>>软件ID 生成一个替换 96001
    chaojiying = Chaojiying_Client('超级鹰用户名', '超级鹰用户名的密码', '96001')	

    # 1.使用图片字节数据来进行识别
    #本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
    # im = open('a.jpg', 'rb').read()		
    # result = chaojiying.PostPic(im, 1004)

    # 2.base64代码识别 
    # base64_str = '...'
    # result = chaojiying.PostPic_base64(base64_str, 1004)	 #1902 验证码类型 

    # 查询剩余题分
    # result = chaojiying.GetScore()
    # print(result)  
