# -*- coding: utf-8 -*-
import binascii
import requests
from bs4 import BeautifulSoup
import sys
import rsa
import json
import requests
import re
import time
import smtplib
from email.mime.text import MIMEText


class Student:

    def __init__(self, config_json, ed_system):
        self.pub = None
        self.token = None
        self.header = None
        self.cookie = None
        self.modules = None
        self.request = None

        # 定义一个暂时变量，存放查询后的成绩数目，一遍与之前的比较
        self.temp_number_of_scores = None

        self.year = str(config_json['temp_year'])
        # 将配置中的学期转换为关键词,0为第一学期,1为第二学期

        self.setup_term(config_json['temp_term'])

        self.term_0_chongxiu_grade_number = config_json['term_0_chongxiu_grade_number']
        self.term_1_chongxiu_grade_number = config_json['term_1_chongxiu_grade_number']

        self.name = str(config_json['stu_name']).encode("utf8").decode("utf8")
        self.password = str(config_json['stu_password']).encode("utf8").decode("utf8")
        self.temp_password = self.password
        self.url = ed_system.url
        self.KeyUrl = ed_system.key_url
        self.gradeUrl = ed_system.grade_url
        self.chongxiuUrl = ed_system.chongxiu_url
        self.login()

    # 设置当前的学期0：第一学期，1：第二学期
    def setup_term(self, term_key):
        self.term_key = str(term_key)
        if self.term_key == "1":
            self.term = "3"  # 第一学期
        elif self.term_key == "2":
            self.term = "12"  # 第二学期

    # 获取公钥密码
    def get_public_key(self):
        result = None
        result = self.sessions.get(self.KeyUrl + str(self.time), verify=False).json()
        self.modules = result["modulus"]
        # 说实话 这也太那啥了 这居然是没用的 怪不得去年栽在这里
        # self.exponent = result["exponent"]

    # 获取CsrfToken
    def get_csrf_token(self):
        r = self.sessions.get(self.url + str(self.time))
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        self.token = soup.find('input', attrs={'id': 'csrftoken'}).attrs['value']

    # 加密密码
    def process_public(self):
        weibo_rsa_e = 65537
        self.password = self.temp_password
        message = str(self.password).encode()

        rsa_n = binascii.b2a_hex(binascii.a2b_base64(self.modules))
        key = rsa.PublicKey(int(rsa_n, 16), weibo_rsa_e)
        encropy_pwd = rsa.encrypt(message, key)
        self.password = binascii.b2a_base64(encropy_pwd)

    # 登录函数
    def login(self):
        self.sessions = requests.Session()
        self.time = int(time.time())
        self.get_public_key()
        self.get_csrf_token()
        self.process_public()
        try:
            self.header = {
                'Accept': 'text/html, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
                'Connection': 'keep-alive',
                'Referer': self.url + str(self.time),
                'Upgrade-Insecure-Requests': '1',
            }
            data = {
                'csrftoken': self.token,
                'mm': self.password,
                'mm': self.password,
                'yhm': self.name
            }
            self.request = self.sessions.post(self.url, headers=self.header, data=data)
            self.cookie = self.request.request.headers['cookie']
            key_word = r'用户名或密码不正确'
            if re.findall(key_word, self.request.text):
                print('用户名或密码错误,请查验..')
                sys.exit()
            else:
                print("登陆成功")
        except Exception as e:
            print(str(e))
            sys.exit()

    # 请求重修数据
    def post_grade_chongxiu_data(self):
        try:
            payload = {
                "cxxnm": "2021",  # 学年
                "cxxqm": self.term,  # 学期3为上学期,12为下学期
                # "cxxqm": "",  # 学期3为上学期,12为下学期
                "pc": "1",  # 页码
                "njdm_id": "2019",  # 年级代码
                "kkbm_id": "",  # 可选
                "zyh_id": "1803",  # 专业代码
                "xqh_id": "1",  # 学期号
                "kcdmmc": "",  # 课程代码
                "jsxmgh": "",  # 教师工号
                "jxbmc": "",  # 教学班名称
                "kklxdm": "-1",  # -1表示全部
                "yxzx": "0",  # 0为全部，1为本科，2为专科
                "kbmbj": "-1",  # -1全部，0未选，1已选
                "_search": "false",  # 是否搜索
                "nd": int(time.time()),  # 时间戳
                "queryModel.showCount": "100",  # 每页显示的数据条数
                "queryModel.currentPage": "1",  # 当前页
                "queryModel.sortName": "cj",  # 设置排序名字
                "queryModel.sortOrder": "asc",  # 设置排序方式
                "time": "0"  # 时间戳
            }
            print(f"开始获取第{self.term_key}学期重修数据")
            self.request = self.sessions.post(self.chongxiuUrl, data=payload, headers=self.header).json()

            # print(self.request)
            return self.request
        except Exception as e:
            print(str(e))
            sys.exit()

    # 请求重修成绩,自动化完成成绩的获取
    def get_chongxiu_grade(self):
        # 首先进行登录
        self.login
        # 设置查询的学期
        self.setup_term("1")

        temp_response_json = self.post_grade_chongxiu_data()
        # 处理响应数据
        info_of_score, self.temp_number_of_scores = temp_system.handle_response(temp_response_json, stu)
        # 获得表格
        temp_system.get_table(info_of_score, stu)
        # 发送推送
        stu.setup_term("2")
        temp_response_json = stu.post_grade_chongxiu_data()
        # 处理响应数据
        info_of_score, self.temp_number_of_scores = temp_system.handle_response(temp_response_json, stu)
        # 获得表格
        temp_system.get_table(info_of_score, stu)
        # 发送推送


class eduction_sysem:
    # 教务系统登录路径
    url = "https://jwgl.nwu.edu.cn/jwglxt/xtgl/login_slogin.html?language=zh_CN&_t="

    # 请求PublicKey的URL
    key_url = "https://jwgl.nwu.edu.cn/jwglxt/xtgl/login_getPublicKey.html?time="

    # 获取成绩路径
    grade_url = "https://jwgl.nwu.edu.cn/jwglxt/cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdm=N305005"

    def __init__(self, config_json):
        self.stuID = config_json['stu_name']
        # 重修网站路径
        self.chongxiu_url = f"https://jwgl.nwu.edu.cn/jwglxt/cxbm/cxbm_cxXscxbmList.html?gnmkdm=N1056&su={self.stuID}"

    # 处理json，返回成绩数据
    def handle_response(self, response_json, student):
        global number_of_scores
        # 解析响应数据
        json_data_list = response_json['items']
        # print(len(json_data_list))#数量
        temp_number_of_data = 0
        score_data = []
        for i in json_data_list:
            # 将无用信息去除
            temp_str = i['kcmc']
            temp_str = re.sub('<br>', '\n', temp_str)
            temp_str = re.sub(r'$', '\n', temp_str)
            temp_str = temp_str.replace('课程代码：', '')
            temp_str = temp_str.replace('学分：', '')
            temp_str = temp_str.replace('正考成绩：', '')
            # 将数据分开
            temp_iter = re.findall(r'.*\n', temp_str)
            # 去除无成绩的数据
            if len(temp_iter) < 4:
                break
            n = 0
            temp_number_of_data = temp_number_of_data + 1
            data_list = []
            # data_list.append(m)#序号
            for j in temp_iter:
                # 跳过
                if n != 1 and n != 2:
                    j = re.sub(r'\n', '', j)
                    data_list.append(j)
                    # print(j)
                n = n + 1
            score_data.append(data_list)

        number_of_scores = temp_number_of_data
        if debug_status:
            print("解析成功,共计{}条成绩".format(number_of_scores))
        # 判断当前学期
        if student.term_key == "1":
            self.term_0_number = temp_number_of_data
            self.number_of_scores_last = student.term_0_chongxiu_grade_number

        elif student.term_key == "2":
            self.term_1_number = temp_number_of_data
            self.number_of_scores_last = student.term_1_chongxiu_grade_number

        # 判断数据是否变化，有变换就更新上次数量
        if temp_number_of_data == self.number_of_scores_last:
            self.data_is_change = False
        else:
            self.data_is_change = True
            self.number_of_scores_last = temp_number_of_data
        score_data.sort(key=lambda ele: ele[1], reverse=True)

        return score_data, temp_number_of_data

    # 获得表格数据
    def get_table(self, data_of_scores, student):
        global number_of_scores
        mat = "{:30}\t{:20}"
        str1 = mat.format("课程名称", "课程成绩") + "\n"
        print(mat.format("课程名称", "课程成绩"))
        for i in data_of_scores:
            str1 = str1 + mat.format(i[0], i[1]) + "\n"
        print(str1)

        markdown = str1
        # 判断是否为有新成绩通知
        if change_notify_status:
            if self.data_is_change:
                print("有新成绩")
                if student.term_key == "1":
                    student.term_0_chongxiu_grade_number = number_of_scores
                    data_json['term_0_chongxiu_grade_number'] = number_of_scores
                    markdown = '第一学期重修成绩' + markdown
                    push_message.push_mail(markdown, f'第一学期重修成绩已更新，共有{number_of_scores}条成绩')

                elif student.term_key == "2":
                    student.term_1_chongxiu_grade_number = number_of_scores
                    # 将json文件的学期数据保存
                    data_json['term_1_chongxiu_grade_number'] = number_of_scores
                    markdown = '第二学期重修成绩' + markdown
                    push_message.push_mail(markdown, f'第二学期重修成绩已更新，共有{number_of_scores}条成绩')

            else:
                if debug_status:
                    print("没有新数据")
        else:
            print("没有新数据")
            push_message.push_mail(markdown, f'成绩已更新，共有{number_of_scores}条成绩')

        write_back_json(data_json)
        return markdown


class push_system:
    mail_switch = False

    def __init__(self, config_json):
        self.mail_switch = config_json['mail_switch']
        if self.mail_switch:
            self.init_mail(config_json)
            print("邮件服务器开启")
        else:
            print("邮件服务器关闭")

    def init_mail(self, config_json):
        self.sender = config_json['sender']
        self.receiver = config_json['receiver']
        self.mail_host = config_json['mail_host']
        self.mail_user = config_json['mail_user']
        self.mail_pass = config_json['mail_pass']

    def push(self, data):
        if self.mail_switch:
            self.push_mail(data)

    # 邮箱推送

    def push_mail(self, data):
        global number_of_scores
        print("开始发送邮件")
        # 设置email信息
        # 邮件内容设置
        message = MIMEText(data, 'plain', 'utf-8')
        # 邮件主题
        message['Subject'] = f'成绩已更新，共有{number_of_scores}条成绩'
        print(f'成绩已更新，共有{number_of_scores}条成绩')
        # 发送方信息
        message['From'] = self.sender
        # 接受方信息
        message['To'] = self.receiver

        # 登录并发送邮件
        try:
            smtp_obj = smtplib.SMTP()
            # 连接到服务器
            smtp_obj.connect(self.mail_host, 25)
            # 登录到服务器
            smtp_obj.login(self.mail_user, self.mail_pass)
            # 发送
            smtp_obj.sendmail(self.sender, self.receiver, message.as_string())
            # 退出
            smtp_obj.quit()
            print("邮件发送成功")
        except smtplib.SMTPException as e:
            print("邮件发送失败", e)

    # 带标题的推送
    def push_mail(self, data, title):
        global number_of_scores
        print("开始发送邮件")
        # 设置email信息
        # 邮件内容设置
        message = MIMEText(data, 'plain', 'utf-8')
        # 邮件主题
        message['Subject'] = title
        print(title)
        # 发送方信息
        message['From'] = self.sender
        # 接受方信息
        message['To'] = self.receiver

        # 登录并发送邮件
        try:
            smtp_obj = smtplib.SMTP()
            # 连接到服务器
            smtp_obj.connect(self.mail_host, 25)
            # 登录到服务器
            smtp_obj.login(self.mail_user, self.mail_pass)
            # 发送
            smtp_obj.sendmail(self.sender, self.receiver, message.as_string())
            # 退出
            smtp_obj.quit()
            print("邮件发送成功")
        except smtplib.SMTPException as e:
            print("邮件发送失败", e)


def get_json():
    with open('config.json', 'r') as f:
        config_json = json.load(f)
    f.close
    return config_json


def write_back_json(json_dict):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(json_dict, f, indent=2, sort_keys=True, ensure_ascii=False)
    f.close


if __name__ == '__main__':
    print("重修成绩查询程序启动")
    # 获取配置文件
    data_json = get_json()
    # 获取配置文件中的数据
    # print(data_json)

    number_of_scores = 0

    # 登陆~
    # 初始化系统
    temp_system = eduction_sysem(data_json)
    # 初始化学生
    stu = Student(data_json, temp_system)
    # 初始化消息推送
    push_message = push_system(data_json)

    # 循环模式状态
    repeat_status = False
    # 打开推送
    open_push_status = True

    # 当变化时通知
    change_notify_status = True
    # 系统日志debug模式
    debug_status = True
    stu.get_chongxiu_grade()
