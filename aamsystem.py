import sys
import requests
import re
import time
import json
from student import *
from encryption import Encryption
# from utils import json_utils
import urllib3
# 禁用安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    def login(self, student: Student) -> bool :
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
                sys.exit()
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
            str1 = str1 + mat.format(i[0], i[1] , i[2]) + "\n"
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
