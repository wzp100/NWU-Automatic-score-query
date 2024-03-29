import datetime

TEST = False

UPPER_TERM = "3"  # 第一个学期的代码
LOWER_TERM = "12"  # 第二个学期的代码

import sys
import re

import urllib3

# 禁用安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import binascii
from bs4 import BeautifulSoup
import rsa
import time
import urllib3
import requests

# 禁用安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import json


# 判断json文件是否存在
def is_json_exist(file_name: str) -> bool:
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except FileNotFoundError:
        return False


# 读取json文件
def get_json(file_name: str) -> dict:
    # 判断文件是否存在
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            config_json = json.load(f)
        return config_json
    except FileNotFoundError:
        print(f'文件{file_name}不存在')
        # 不存在则创建文件
        with open(file_name, 'w', encoding='utf-8') as f:
            json_dict = create_json()
            write_back_json(json_dict, file_name)
        return json_dict


def create_json():
    # 输入学号
    student_id = str(input('请输入学号：'))
    # 输入密码
    password = str(input('请输入密码：'))
    # 输入入学年份
    school_year = str(input('请输入入学年份：'))
    # 创建json文件
    json_dict = {
        "id": student_id,  # 学号
        "password": password,  # 密码
        "upper_term_grade_num": 0,  # 重修成绩数目
        "lower_term_grade_num": 0,  # 重修成绩数目
        "name": "",  # 学生姓名
        "school_year": school_year,  # 入学年份
    }
    return json_dict


# 写入json文件
def write_back_json(json_dict: dict, file_name: str) -> bool:
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(json_dict, f, indent=2, sort_keys=False, ensure_ascii=False)
    return True


# 构建学生类
class Student:
    university = "西北大学"  # 学校名字

    # 初始化学生类
    def __init__(self) -> None:
        # 定义一个暂时变量，存放查询后的成绩数目，一遍与之前的比较

        self.term_grade_dic = {'upper_term': {},
                               'lower_term': {}}
        self.lower_term_name_dic = None  # 下学期课程名字字典
        self.lower_term_grade_dic = None  # 下学期课程成绩字典
        self.upper_term_name_dic = None  # 上学期课程名字字典
        self.upper_term_grade_dic = None  # 上学期课程成绩字典
        self.config_name = None  # 配置文件名
        self.config_json = {}  # 配置文件
        self.upper_term_grade_num = 0  # 上学期成绩数目
        self.lower_term_grade_num = 0  # 下学期成绩数目
        # TODO: 实现姓名的自动获取
        self.name = None  # 学生姓名
        self.stu_ID = None  # 学生学号
        self.password = None  # 学生密码
        self.upper_term_grade = None  # 上学期成绩
        self.upper_term_grade_table = None  # 上学期成绩表格
        self.lower_term_grade = None  # 下学期成绩
        self.lower_term_grade_table = None  # 下学期成绩表格
        self.school_year = None  # 学年年份
        # 保存新增的成绩
        self.new_grade = {
            'upper_term': {},
            'lower_term': {}
        }

    # def __int__(self, config_json):
    #     # 定义一个暂时变量，存放查询后的成绩数目，一遍与之前的比较
    #     self.upper_term_grade_num = 0
    #     self.lower_term_grade_num = 0
    #     self.name = None  # 学生姓名
    #     self.stu_ID = None  # 学生学号
    #     self.password = None  # 学生密码
    #     self.upper_term_grade = None  # 上学期成绩
    #     self.upper_term_grade_table = None  # 上学期成绩表格
    #     self.lower_term_grade = None  # 下学期成绩
    #     self.lower_term_grade_table = None  # 下学期成绩表格
    #     self.read_config(config_json)
    def config(self, config_name):
        self.config_name = config_name
        self.read_config(self.config_name)

    # 读取config_json中的信息
    def read_config(self, config_name):
        config_json = get_json(config_name)
        try:
            self.upper_term_grade_num = config_json['upper_term_grade_num']  # 上学期成绩数目
            self.lower_term_grade_num = config_json['lower_term_grade_num']  # 下学期成绩数目
            self.name = config_json['name']  # 学生姓名
            self.term_grade_dic = config_json['term_grade_dic']  # 学生课程成绩字典
        except KeyError:
            pass
        # 仅当必要的数据缺失时才会重新填写
        try:
            self.stu_ID = config_json['id']  # 学生学号
            self.password = config_json['password']  # 学生密码
            self.school_year = config_json['school_year']  # 入学年份
        except KeyError:
            print("配置文件中缺少信息，请重新输入")
            self.input_stu_ID_and_password()
            self.save_student_info(config_name)

    # 输入学号和密码
    def input_stu_ID_and_password(self):
        print("如果查询结果为空，请检查入学年份是否正确，可以适当更改")
        self.stu_ID = input("学号：")
        self.password = input("密码：")
        self.school_year = input("入学年份（例如2022）：")

    # 保存,保存在相同的文件下
    def save(self):
        self.save_student_info(self.config_name)

    # 保存学生信息，另存为信息
    def save_student_info(self, file_name):
        self.config_name = file_name
        self.get_term_grade_dic()
        self.config_json['school_year'] = self.school_year
        self.config_json['name'] = self.name
        self.config_json['id'] = self.stu_ID
        self.config_json['password'] = self.password
        self.config_json['term_grade_dic'] = self.term_grade_dic
        self.config_json['upper_term_grade_num'] = self.upper_term_grade_num
        self.config_json['lower_term_grade_num'] = self.lower_term_grade_num
        write_back_json(self.config_json, file_name)
        print("保存成功")
        return self.config_json

    # 更改学年
    def change_school_year(self, year):
        self.school_year = year

    #  字典的去冗余，将grade_dic和name_dic中的重复项去掉，只保留一个，使用课程号作为key，课程名称和课程成绩作为value。然后将上下学期的字
    #  典合并，使用学期作为key，课程号、课程名称和课程成绩作为value，最后将字典保存到config_json中
    # 保存学期成绩
    @staticmethod
    def save_term_grade_to_dic(term_grade: list):
        # 首先创建一个课程代码为key，课程成绩为value的字典
        grade_dic = {}
        # 判断term_grade 是否为空
        if term_grade is None:
            return grade_dic
        # 遍历课程成绩列表
        for i in term_grade:
            # 将课程代码作为key，课程名称与成绩作为value，存入字典
            grade_dic[i[2]] = [i[0], i[1], i[3]]

        return grade_dic

    # 获得上下学期成绩的字典
    def get_term_grade_dic(self):
        # self.upper_term_grade_dic, self.upper_term_name_dic = self.save_term_grade_to_dic(self.upper_term_grade)
        # # self.lower_term_grade_dic, self.lower_term_name_dic = self.save_term_grade_to_dic(self.lower_term_grade)
        self.upper_term_grade_dic = self.save_term_grade_to_dic(self.upper_term_grade)
        self.lower_term_grade_dic = self.save_term_grade_to_dic(self.lower_term_grade)
        # 将上下学期成绩字典合并
        # self.term_grade_dic = {'upper_term': self.upper_term_grade_dic, 'lower_term': self.lower_term_grade_dic}
        self.add_grade_to_dict()
        return self.term_grade_dic

    # 实现成绩的增查，首先检测是否有重复的课程代码，如果有，提示是否覆盖，如果没有，直接添加
    # 添加到成绩字典中，对于已有的成绩进行替换，对于没有的数据进行添加
    def add_grade_to_dict(self) -> dict:
        # 遍历grade
        for temp_grade in self.upper_term_grade_dic:
            try:
                if temp_grade in self.term_grade_dic['upper_term'].keys():
                    self.term_grade_dic['upper_term'].update({temp_grade: self.upper_term_grade_dic[temp_grade]})
                else:
                    # 字典里没有
                    self.term_grade_dic['upper_term'].update({temp_grade: self.upper_term_grade_dic[temp_grade]})
                    # 保存到新增成绩列表中
                    self.new_grade['upper_term'].update({temp_grade: self.upper_term_grade_dic[temp_grade]})

            except TypeError:
                self.term_grade_dic = {'upper_term': {}, 'lower_term': {}}  # 重新创建一个字典
                self.new_grade = {'upper_term': {}, 'lower_term': {}}  # 重新创建一个字典
                self.term_grade_dic['upper_term'].update({temp_grade: self.upper_term_grade_dic[temp_grade]})
                self.new_grade['upper_term'].update({temp_grade: self.upper_term_grade_dic[temp_grade]})
        self.upper_term_grade_num = len(self.term_grade_dic['upper_term'].keys())

        for temp_grade in self.lower_term_grade_dic:
            if temp_grade in self.term_grade_dic['lower_term'].keys():
                self.term_grade_dic['lower_term'].update({temp_grade: self.lower_term_grade_dic[temp_grade]})
            else:
                # 字典里没有
                self.term_grade_dic['lower_term'].update({temp_grade: self.lower_term_grade_dic[temp_grade]})
                self.new_grade['lower_term'].update({temp_grade: self.lower_term_grade_dic[temp_grade]})
        self.lower_term_grade_num = len(self.term_grade_dic['lower_term'].keys())
        return self.term_grade_dic

    # 获得表格数据
    @staticmethod
    def get_table(data_of_scores) -> str:
        mat = "{:35}\t{:20}\t{:20}\t{:20}"
        str1 = mat.format("课程名称", "课程成绩", "课程代码", "课程学分") + "\n"
        # print(mat.format("课程名称", "课程成绩"))
        for i in data_of_scores:
            try:
                str1 = str1 + mat.format(i[0], i[1], i[2], i[3]) + "\n"
            except IndexError:
                str1 = str1 + mat.format(i[0], i[1], i[2], "无") + "\n"
        table = str1
        return table

    # 字典到列表的转换
    def grade_dict_display(self):
        upper_table = self.get_term_table('upper_term', self.term_grade_dic)
        lower_table = self.get_term_table('lower_term', self.term_grade_dic)
        self.print(upper_table, lower_table)

        return upper_table, lower_table

    # 获得上下学期的总成绩表格
    def get_term_table(self, term: str, term_grade_dic: dict):
        if term == 'upper_term':
            print(f"所有学年上学期所有课程(总计{len(term_grade_dic[term])}门)成绩如下：")
        elif term == 'lower_term':
            print(f"所有学年下学期所有课程(总计{len(term_grade_dic[term])}门)成绩如下：")
        else:
            print("输入有误")
            return
        temp_list = []
        for temp_dict in term_grade_dic[term]:
            try:
                temp_list.append([term_grade_dic[term][temp_dict][0],  # 课程名称
                                  term_grade_dic[term][temp_dict][1],  # 课程成绩
                                  temp_dict,  # 课程代码
                                  term_grade_dic[term][temp_dict][2]])  # 课程学分
            except IndexError:
                temp_list.append([term_grade_dic[term][temp_dict][0],  # 课程名称
                                  term_grade_dic[term][temp_dict][1],  # 课程成绩
                                  temp_dict,  # 课程代码
                                  "无"])  # 课程学分

        table = self.get_table(temp_list)
        # print(table)
        return table

    # 展示新增成绩
    def show_new_grade(self):
        upper_table = ""
        lower_table = ""
        if len(self.new_grade['upper_term']) == 0:
            print("上学期没有新增成绩")
        else:
            print(f"上学期新增{len(self.new_grade['upper_term'])}条成绩如下：")
            upper_table = self.get_term_table('upper_term', self.new_grade)
        if len(self.new_grade['lower_term']) == 0:
            print("下学期没有新增成绩")
        else:
            print(f"下学期新增{len(self.new_grade['lower_term'])}条成绩如下：")
            lower_table = self.get_term_table('lower_term', self.new_grade)
        self.print(upper_table, lower_table)
        # 刷新新增成绩
        self.new_grade = {'upper_term': {}, 'lower_term': {}}
        return upper_table, lower_table

    # 实现新增成绩查询的功能

    # 打印成绩
    def print_post_grade(self):
        self.print(self.upper_term_grade_table, self.lower_term_grade_table)

    # 打印
    @staticmethod
    def print(upper_table, lower_table):
        if upper_table == "":
            pass
        else:
            # 打印上学期成绩
            print('---------------------------------------------------------------------------------------')
            print("上学期成绩：")
            print(upper_table)
        if lower_table == "":
            pass
        else:
            print('---------------------------------------------------------------------------------------')
            # 打印下学期成绩
            print("下学期成绩：")
            print(lower_table)

    # 计算加权平均分
    def calculate_weighted_average(self):
        grade_liat = []  # 成绩列表，保存成绩与学分
        for temp_grade in self.term_grade_dic['upper_term']:
            try:
                grade_liat.append([self.deal_with_grade(self.term_grade_dic['upper_term'][temp_grade][1]),
                                   self.deal_with_grade(self.term_grade_dic['upper_term'][temp_grade][2])])
            except IndexError:
                print("成绩数据有误")
                pass
        for temp_grade in self.term_grade_dic['lower_term']:
            try:
                grade_liat.append([self.deal_with_grade(self.term_grade_dic['lower_term'][temp_grade][1]),
                                   self.deal_with_grade(self.term_grade_dic['lower_term'][temp_grade][2])])
            except IndexError:
                print("成绩数据有误")
                pass
        print(grade_liat)
        # 计算加权平均分
        weighted_average = 0
        total_credit = 0
        for temp_grade in grade_liat:
            weighted_average += temp_grade[0] * temp_grade[1]
            total_credit += temp_grade[1]
        weighted_average = weighted_average / total_credit
        print(f"加权平均分为{weighted_average:.2f}")
        return weighted_average

    # 处理文字成绩
    @staticmethod
    def deal_with_grade(grade: str):
        if grade == "优秀":
            return 95.0
        elif grade == "良好":
            return 85.0
        elif grade == "中等":
            return 75.0
        elif grade == "及格":
            return 65.0
        elif grade == "不及格":
            return 0.0
        # 判断是否为数字
        elif grade.isdigit():
            return float(grade)
        # 判断是否为小数
        elif grade.replace('.', '', 1).isdigit():
            return float(grade)
        else:
            return -1  # 无法处理,返回-1


# 加密类,用于加密密码,发送请求
class Encryption:
    def __init__(self, password, url, key_url, sessions):
        self.password = None  # 加密后的密码
        self.url = url
        self.key_url = key_url
        self.sessions = sessions
        self.time = int(time.time())  # 时间戳
        self.weibo_rsa_e = 65537  # 固定值
        self.modules = None
        self.exponent = None
        self.token = None
        self.temp_password = password  # 未加密的密码
        self.header = None
        self.request = None
        self.cookie = None

    # 获取公钥密码
    def get_public_key(self):
        # result = None
        # 学校的ssl证书有问题,所以verify=False
        try:
            result = self.sessions.get(self.key_url + str(self.time), verify=False).json()
        except requests.exceptions.ProxyError:
            print("网络错误,请检查网络是否开启代理（或者说是VPN，游戏加速器之类）")
            exit(0)
        self.modules = result["modulus"]
        # 说实话 这也太那啥了 这居然是没用的 怪不得去年栽在这里
        # self.exponent = result["exponent"]

    # 获取CsrfToken
    def get_csrf_token(self):
        r = self.sessions.get(self.url + str(self.time), verify=False)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        self.token = soup.find('input', attrs={'id': 'csrftoken'}).attrs['value']

    # 加密密码
    def process_public(self):
        message = str(self.temp_password).encode()
        rsa_n = binascii.b2a_hex(binascii.a2b_base64(self.modules))
        key = rsa.PublicKey(int(rsa_n, 16), self.weibo_rsa_e)
        encropy_pwd = rsa.encrypt(message, key)  # 加密
        self.password = binascii.b2a_base64(encropy_pwd)

    # 加密
    def encrypt(self) -> None:
        self.get_public_key()
        self.get_csrf_token()
        self.process_public()

# 教务系统类 AcademicAffairsManagementSystem(AAMSystem)
class AAMSystem:
    # 这里适合放一些固定的东西
    # 教务系统登录路径
    url = "https://jwgl.nwu.edu.cn/jwglxt/xtgl/login_slogin.html?language=zh_CN&_t="
    # 请求PublicKey的URL
    key_url = "https://jwgl.nwu.edu.cn/jwglxt/xtgl/login_getPublicKey.html?time="
    # 获取成绩路径
    grade_url = "https://jwgl.nwu.edu.cn/jwglxt/cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdm=N305005"
    # 重修网站路径
    chongxiu_url = "https://jwgl.nwu.edu.cn/jwglxt/cxbm/cxbm_cxXscxbmList.html?gnmkdm=N1056&su="

    # 初始化教务系统
    def __init__(self):
        # self.stuID = config_json['stu_name']
        # 网站信息
        self.lower_term_request = None
        self.upper_term_request = None
        self.chongxiu_request = None  # 重修网站请求结果
        self.header = None
        self.cookie = None  # 相当于临时密码
        self.sessions = requests.Session()  # 会话
        self.encry_info = None  # 加密信息
        self.chongxiu_url = None  # 重修网站路径

        # 学生信息
        self.student = None  # 学生信息
        # self.stu_ID = None  # 学号
        # self.upper_term_grade = None  # 上学期成绩
        # self.upper_term_grade_num = None  # 上学期成绩数量
        # self.upper_term_grade_table = None  # 上学期成绩表格
        # self.lower_term_grade = None  # 下学期成绩
        # self.lower_term_grade_num = None  # 下学期成绩数量
        # self.lower_term_grade_table = None  # 下学期成绩表格
        # 系统状态
        # 登录状态
        self.login_status = False

    # 检测是否登录，并进行提醒
    def check_login(self):
        if not self.login_status:
            print("请先登录教务系统")
            sys.exit()
        else:
            return True

    # 登录教务系统，一切信息得有学生登录才会有
    def login(self, student: Student) -> bool:
        """

        :param student:
        :return: bool
        """
        # 判断是否已经登录
        if self.login_status:
            print("已经登录，无需重复登录")
            return True
        # 学生信息
        self.student = student
        # 根据学生信息加载重修网站路径
        self.chongxiu_url = AAMSystem.chongxiu_url + student.stu_ID
        self.encry_info = Encryption(student.password, AAMSystem.url, AAMSystem.key_url, self.sessions)
        # 加密密码
        self.encry_info.encrypt()
        try:
            self.header = {
                'Accept': 'text/html, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
                'Connection': 'keep-alive',
                'Referer': AAMSystem.url + str(self.encry_info.time),
                'Upgrade-Insecure-Requests': '1',
            }
            data = {
                'csrftoken': self.encry_info.token,
                'mm': self.encry_info.password,
                'yhm': student.stu_ID
            }
            request = self.sessions.post(url=AAMSystem.url, headers=self.header,
                                         data=data, verify=False)
            self.cookie = request.request.headers['cookie']
            key_word = r'用户名或密码不正确'
            if re.findall(key_word, request.text):
                print('用户名或密码错误,请查验..')
                self.student.input_stu_ID_and_password()
                self.student.save_student_info(self.student.config_name)
                return False
            else:
                self.login_status = True
                print("登陆成功")
                return True
        except Exception as e:
            print(str(e))
            return False


    # 请求某学期的重修数据
    def post_grade_chongxiu_data(self, term: str):
        try:
            now_time = int(time.time())
            payload = {
                "cxxnm": self.student.school_year,  # 学年，十分重要，22级的查不到就是因为这个。可以选择自己的入学年份
                "cxxqm": term,  # 学期3为上学期,12为下学期
                "pc": "1",  # 页码
                "njdm_id": self.student.school_year,  # 年级代码,用处不大随便填
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
                "nd": now_time,  # 时间戳
                "queryModel.showCount": "100",  # 每页显示的数据条数
                "queryModel.currentPage": "1",  # 当前页
                "queryModel.sortName": "cj",  # 设置排序名字
                "queryModel.sortOrder": "asc",  # 设置排序方式
                "time": "0"  # 时间戳
            }
            self.chongxiu_request = self.sessions.post(url=self.chongxiu_url, data=payload,
                                                       headers=self.header, verify=False).json()
            # 保存响应数据为文件
            with open("chongxiu.json", "w", encoding="utf-8") as f:
                json.dump(self.chongxiu_request, f, ensure_ascii=False)
            return self.chongxiu_request
        except Exception as e:
            print(str(e))
            sys.exit()

    # 获得重修成绩,从响应数据中获得成绩信息
    def get_chongxiu_grade(self) -> Student:
        # 检测是否登录
        self.check_login()
        # 首先获取第一学期的重修数据
        # 将函数打包为一个函数，然后上下学期的数据都可以用这个函数来获取
        # print("正在获取第一学期的重修数据")
        # temp_response_json = self.post_grade_chongxiu_data(UPPER_TERM)
        # # 处理响应数据
        # self.student.upper_term_grade, temp_upper_term_grade_num = self.handle_response(temp_response_json)
        # self.compare_grade_num(self.student.upper_term_grade_num, temp_upper_term_grade_num)
        # self.student.upper_term_grade_num = temp_upper_term_grade_num
        # # 获得表格
        # self.student.upper_term_grade_table = self.get_table(self.student.upper_term_grade)
        # # 获取第二学期的重修数据
        # print("正在获取第二学期的重修数据")
        # temp_response_json = self.post_grade_chongxiu_data(LOWER_TERM)
        # # 处理响应数据
        # self.student.lower_term_grade, temp_lower_term_grade_num = self.handle_response(temp_response_json)
        # self.compare_grade_num(self.student.lower_term_grade_num, temp_lower_term_grade_num)
        # self.student.lower_term_grade_num = temp_lower_term_grade_num
        # # 获得表格
        # self.student.lower_term_grade_table = self.get_table(self.student.lower_term_grade)
        # 获得第一学期
        self.student.upper_term_grade_num, self.student.upper_term_grade, self.student.upper_term_grade_table = \
            self.get_term_grade(UPPER_TERM)
        # 获得第二学期
        self.student.lower_term_grade_num, self.student.lower_term_grade, self.student.lower_term_grade_table = \
            self.get_term_grade(LOWER_TERM)
        return self.student

    # 获得某个学期的成绩数据
    def get_term_grade(self, term: str):
        if term == UPPER_TERM:
            print("正在获取第一学期的重修数据")
        elif term == LOWER_TERM:
            print("正在获取第二学期的重修数据")
        else:
            print("学期参数错误")
            sys.exit()
        temp_response_json = self.post_grade_chongxiu_data(term)
        # 处理响应数据
        temp_term_grade, temp_upper_term_grade_num = self.handle_response(temp_response_json)
        # 获得表格
        temp_term_grade_table = self.get_table(temp_term_grade)
        return temp_upper_term_grade_num, temp_term_grade, temp_term_grade_table

    # 处理json，返回成绩数据
    @staticmethod
    def handle_response(response_json):
        # 解析响应数据
        grade_items = response_json['items']
        score_data = []
        for temp_item in grade_items:
            try:
                score_data.append([temp_item['kcmc'].split("<br>")[0],
                                   temp_item['cj'], temp_item['kch'], temp_item['xf']])
            except KeyError:
                pass
        temp_number_of_data = len(score_data)
        print(f"解析成功,共计{temp_number_of_data}条成绩")
        # 按照成绩排序
        score_data.sort(key=lambda ele: ele[1], reverse=True)
        return score_data, temp_number_of_data

    # 获得表格数据
    @staticmethod
    def get_table(data_of_scores) -> str:
        mat = "{:30}\t{:20}\t{:20}\t{:20}"
        str1 = mat.format("课程名称", "课程成绩", "课程代码", '课程学分') + "\n"
        # print(mat.format("课程名称", "课程成绩"))
        for i in data_of_scores:
            str1 = str1 + mat.format(i[0], i[1], i[2], i[3]) + "\n"
        table = str1
        return table

    # # 保存数据
    # def save_data(self, data_json, file_name: str):
    #     print("正在保存数据")
    #     # 保存第一学期的重修成绩数量数据
    #     data_json['upper_term_grade_num'] = self.student.upper_term_grade_num
    #     # 保存第二学期的重修成绩数量数据
    #     data_json['lower_term_grade_num'] = self.student.lower_term_grade_num
    #     json_utils.write_back_json(data_json, file_name)

    # 比对学生的保存成绩数量与当前成绩数量是否一致，并返回两者的差值
    @staticmethod
    def compare_grade_num(old_num: int, new_num: int) -> int:
        sub_num = new_num - old_num
        if old_num == 0:
            print("第一次查询重修数据")
            return sub_num
        # 比对成绩数量
        if sub_num == 0:
            print("重修数据没有更新")
        elif sub_num > 0:
            print(f"重修数据有{sub_num}条更新")
        else:
            print(f"重修数据有{sub_num}条减少,请检查当前查询的学年是否正确")
        return sub_num

    # 通过单个课程代码查询学生保存的成绩中数据是否存在
    def search_grade_by_lesson_code(self, lesson_code) -> bool:
        if (lesson_code in self.student.upper_term_grade.keys()) or \
                (lesson_code in self.student.lower_term_grade.keys()):
            return True
        return False

    # 登出系统
    def logout(self):
        self.sessions.close()
        self.__init__()

    # 退出系统
    def exit_system(self):
        print("退出系统")
        # 关闭会话
        self.sessions.close()


# 主菜单
def main_menu():
    print('-------------------------------------------------------------------------------------')
    print("欢迎使用教务系统查询工具")
    print("1. 查询成绩")
    print("2. 重新登录")
    print("3. 更改查询学年")
    print("4. 查询所有已查询的成绩")
    print("5. 仅查询显示新增成绩")
    print("6. 计算加权平均分")
    print("0. 退出程序")
    num = input("请输入你的选择：")
    print('-------------------------------------------------------------------------------------')
    return num


# 重修成绩查询
def get_chongxiu_grade(system: AAMSystem, student: Student, configName: str):
    # 系统登录
    if not system.login(student):
        exit(0)
    # 成绩查询
    student = system.get_chongxiu_grade()
    # 打印请求的成绩
    # student.print_post_grade()
    # 保存数据
    student.save_student_info(configName)
    # 显示总成绩
    # student.grade_dict_display()
    # 测试系统
    test_aamsystem(system)
    # 测试学生类
    test_student(student)


# 测试学生类
def test_student(student: Student):
    if TEST:
        student.grade_dict_display()


def test_aamsystem(system: AAMSystem):
    if TEST:
        system.exit_system()


# 获取年份
def get_year():
    now_year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    if month < 8:
        now_year = now_year - 1
    return now_year


# 获得近四年的学年列表
def get_year_list():
    year = get_year()
    year_list = []
    for i in range(4):
        year_list.append(str(year - i))
    return year_list


if __name__ == '__main__':
    print("重修成绩查询程序启动")
    if TEST:
        configName = 'test.json'
    else:
        configName = 'userData.json'
    # 初始化学生
    stu = Student()
    # 判断是否有配置文件
    if not is_json_exist(configName):
        # 如果没有配置文件，创建一个
        print("没有配置文件正在创建。。。。")
        stu.input_stu_ID_and_password()
        stu.save_student_info(configName)
    else:
        stu.config(configName)

    # 初始化系统
    system = AAMSystem()
    choice = 0
    while True:
        choice = main_menu()
        if choice == "1":
            get_chongxiu_grade(system, stu, configName)
            stu.print_post_grade()
            stu.show_new_grade()
        elif choice == "2":
            print("重新查询，请输入学号和密码")
            system.logout()
            stu = Student()
            stu.input_stu_ID_and_password()
            get_chongxiu_grade(system, stu, configName)
            stu.print_post_grade()
            stu.show_new_grade()

        elif choice == "3":
            print("更改学年重新查询")
            year = input("学年（例如2022）：")
            stu.change_school_year(year)
            get_chongxiu_grade(system, stu, configName)
            stu.print_post_grade()
            stu.show_new_grade()
        elif choice == "4":
            print("查询各个学年的总成绩")
            stu.grade_dict_display()
        elif choice == "5":
            print("仅查询显示新增成绩")
            get_chongxiu_grade(system, stu, configName)
            stu.show_new_grade()
        elif choice == "6":
            print("首先会查询近四年的成绩，然后计算加权平均分")
            four_year_list = get_year_list()
            for year in four_year_list:
                stu.change_school_year(year)
                get_chongxiu_grade(system, stu, configName)
            stu.calculate_weighted_average()
        else:
            system.exit_system()
            break
        print("---------------------------------------------------------------------------------")
    print("程序结束")
