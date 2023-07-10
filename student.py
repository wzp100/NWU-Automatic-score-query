from utils import json_utils

UPPER_TERM = "3"  # 第一个学期的代码
LOWER_TERM = "12"  # 第二个学期的代码


# 构建学生类
class Student:
    university = "西北大学"  # 学校名字
    # 初始化学生类
    def __init__(self) -> None:
        # 定义一个暂时变量，存放查询后的成绩数目，一遍与之前的比较
        self.term_grade_dic = None
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
        config_json = json_utils.get_json(config_name)
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
        self.get_term_grade_dic()
        self.config_json['school_year'] = self.school_year
        self.config_json['name'] = self.name
        self.config_json['id'] = self.stu_ID
        self.config_json['password'] = self.password
        self.config_json['term_grade_dic'] = self.term_grade_dic
        json_utils.write_back_json(self.config_json, file_name)
        return self.config_json

    # 更改学年
    def change_school_year(self, year):
        self.school_year = year

    #  字典的去冗余，将grade_dic和name_dic中的重复项去掉，只保留一个，使用课程号作为key，课程名称和课程成绩作为value。然后将上下学期的字
    #  典合并，使用学期作为key，课程号、课程名称和课程成绩作为value，最后将字典保存到config_json中
    # 保存学期成绩
    @staticmethod
    def save_term_grade_to_dic(term_grade:list):
        # 首先创建一个课程代码为key，课程成绩为value的字典
        grade_dic = {}
        # 判断term_grade 是否为空
        if term_grade is None:
            return grade_dic
        # 遍历课程成绩列表
        for i in term_grade:
            # 将课程代码作为key，课程名称与成绩作为value，存入字典
            grade_dic[i[2]] = [i[0], i[1]]

        return grade_dic


    # 获得上下学期成绩的字典
    def get_term_grade_dic(self):
        # self.upper_term_grade_dic, self.upper_term_name_dic = self.save_term_grade_to_dic(self.upper_term_grade)
        # self.lower_term_grade_dic, self.lower_term_name_dic = self.save_term_grade_to_dic(self.lower_term_grade)
        self.upper_term_grade_dic = self.save_term_grade_to_dic(self.upper_term_grade)
        self.lower_term_grade_dic = self.save_term_grade_to_dic(self.lower_term_grade)
        # 将上下学期成绩字典合并
        self.term_grade_dic = {'upper_term': self.upper_term_grade_dic, 'lower_term': self.lower_term_grade_dic}
        return self.term_grade_dic



    # TODO: 实现成绩的增查，首先检测是否有重复的课程代码，如果有，提示是否覆盖，如果没有，直接添加

    # TODO: 实现新增成绩查询的功能


    # 打印成绩
    def print_grade(self):
        # 打印上学期成绩
        print("上学期成绩：")
        print(self.upper_term_grade_table)
        # 打印下学期成绩
        print("下学期成绩：")
        print(self.lower_term_grade_table)
