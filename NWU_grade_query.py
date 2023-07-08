import sys
import requests
import re
import urllib3

# 禁用安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json
import binascii
from bs4 import BeautifulSoup
import rsa
import time

UPPER_TERM = "3"  # 第一个学期的代码
LOWER_TERM = "12"  # 第二个学期的代码


# 构建学生类
class Student:
    # 初始化学生类
    def __init__(self) -> None:
        # 定义一个暂时变量，存放查询后的成绩数目，一遍与之前的比较
        self.config_name = None
        self.config_json = {}
        self.upper_term_grade_num = 0
        self.lower_term_grade_num = 0
        self.name = None  # 学生姓名
        self.stu_ID = None  # 学生学号
        self.password = None  # 学生密码
        self.upper_term_grade = None  # 上学期成绩
        self.upper_term_grade_table = None  # 上学期成绩表格
        self.lower_term_grade = None  # 下学期成绩
        self.lower_term_grade_table = None  # 下学期成绩表格
        self.school_year = None  # 学年年份

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

    # 读取config_json中的信息
    def read_config(self, config_name):
        config_json = get_json(config_name)
        try:
            self.upper_term_grade_num = config_json['upper_term_grade_num']
            self.lower_term_grade_num = config_json['lower_term_grade_num']
            self.school_year = config_json['school_year']  # 入学年份
            self.name = config_json['name']  # 学生姓名
            self.stu_ID = config_json['id']  # 学生学号
            self.password = config_json['password']  # 学生密码
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

    # 保存学生信息
    def save_student_info(self, file_name):
        self.config_json['upper_term_grade_num'] = self.upper_term_grade_num
        self.config_json['lower_term_grade_num'] = self.lower_term_grade_num
        self.config_json['school_year'] = self.school_year
        self.config_json['name'] = self.name
        self.config_json['id'] = self.stu_ID
        self.config_json['password'] = self.password
        write_back_json(self.config_json, file_name)
        return self.config_json

    # 更改学年
    def change_school_year(self, year):
        self.school_year = year

    # 打印成绩
    def print_grade(self):
        # 打印上学期成绩
        print("上学期成绩：")
        print(self.upper_term_grade_table)
        # 打印下学期成绩
        print("下学期成绩：")
        print(self.lower_term_grade_table)


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
        result = self.sessions.get(self.key_url + str(self.time), verify=False).json()
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
    school_year = str(input('请输入查询的年份：'))
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
def write_back_json(json_dict, file_name: str) -> None:
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(json_dict, f, indent=2, sort_keys=True, ensure_ascii=False)


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
        print("正在获取第一学期的重修数据")
        temp_response_json = self.post_grade_chongxiu_data(UPPER_TERM)
        # 处理响应数据
        self.student.upper_term_grade, self.student.upper_term_grade_num = self.handle_response(temp_response_json)
        # 获得表格
        self.student.upper_term_grade_table = self.get_table(self.student.upper_term_grade)
        # 获取第二学期的重修数据
        print("正在获取第二学期的重修数据")
        temp_response_json = self.post_grade_chongxiu_data(LOWER_TERM)
        # 处理响应数据
        self.student.lower_term_grade, self.student.lower_term_grade_num = self.handle_response(temp_response_json)
        # 获得表格
        self.student.lower_term_grade_table = self.get_table(self.student.lower_term_grade)
        return self.student

    # 处理json，返回成绩数据
    @staticmethod
    def handle_response(response_json):
        # 解析响应数据
        grade_items = response_json['items']
        temp_number_of_data = 0
        score_data = []
        # for i in json_data_list:
        #     # 将无用信息去除
        #     temp_str = i['kcmc']
        #     temp_str = re.sub('<br>', '\n', temp_str)
        #     temp_str = re.sub(r'$', '\n', temp_str)
        #     temp_str = temp_str.replace('课程代码：', '')
        #     temp_str = temp_str.replace('学分：', '')
        #     temp_str = temp_str.replace('正考成绩：', '')
        #     # 将数据分开
        #     temp_iter = re.findall(r'.*\n', temp_str)
        #     # 去除无成绩的数据
        #     if len(temp_iter) < 4:
        #         break
        #     n = 0
        #     temp_number_of_data = temp_number_of_data + 1
        #     data_list = []
        #     # data_list.append(m)#序号
        #     for j in temp_iter:
        #         # 跳过
        #         if n != 1 and n != 2:
        #             j = re.sub(r'\n', '', j)
        #             data_list.append(j)
        #             # print(j)
        #         n = n + 1
        #     score_data.append(data_list)
        for temp_item in grade_items:
            try:
                # print((i['kcmc'].split("<br>"))[0] +"  "+i['cj'] + "  " + i['kcm'])
                # print(temp_item['kcmc'].split("<br>")[0] + "  " + "ceshi" + temp_item['cj'] + "  " + temp_item['kch'])
                score_data.append([temp_item['kcmc'].split("<br>")[0], temp_item['cj'], temp_item['kch']])
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
        mat = "{:30}\t{:20}\t{:20}"
        str1 = mat.format("课程名称", "课程成绩", "课程代码") + "\n"
        # print(mat.format("课程名称", "课程成绩"))
        for i in data_of_scores:
            str1 = str1 + mat.format(i[0], i[1], i[2]) + "\n"
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

    # 登出系统
    def logout(self):
        self.sessions.close()
        self.__init__()

    # 退出系统
    def exit_system(self):
        print("退出系统")
        # 关闭会话
        self.sessions.close()


# 重修成绩查询
def get_chongxiu_grade(system: AAMSystem, stu: Student, configName: str):
    # 系统登录
    system.login(stu)
    # 成绩查询
    stu = system.get_chongxiu_grade()
    # 打印成绩
    stu.print_grade()
    # 保存数据
    stu.save_student_info(configName)

    choice = input("按回车退出，或者按1重新登录，按2更改学年重新查询：")
    if choice == "1":
        print("重新查询，请输入学号和密码")
        system.logout()
        return "1"
    elif choice == "2":
        print("更改学年重新查询")
        year = input("学年（例如2022）：")
        stu.change_school_year(year)
        return "2"
    else:
        print("退出程序")
        # 退出系统
        system.exit_system()
        return "0"


if __name__ == '__main__':
    print("重修成绩查询程序启动")
    test = False
    if test:
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
    stu.read_config(configName)
    # 初始化系统
    system = AAMSystem()
    while True:
        choice = get_chongxiu_grade(system, stu, configName)
        if choice == "1":
            stu = Student()
            stu.input_stu_ID_and_password()
        elif choice == "2":
            pass
        else:
            break
    print("程序结束")
