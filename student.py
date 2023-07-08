from utils import json_utils

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
        config_json = json_utils.get_json(config_name)
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
        json_utils.write_back_json(self.config_json, file_name)
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
