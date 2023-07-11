from aamsystem import AAMSystem
from student import *
from utils.json_utils import is_json_exist

TEST = False


# 主菜单
def main_menu():
    print('-------------------------------------------------------------------------------------')
    print("欢迎使用教务系统查询工具")
    print("1. 查询成绩")
    print("2. 重新登录")
    print("3. 更改查询学年")
    print("4. 查询所有已查询的成绩")
    print("5. 仅查询显示新增成绩")
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
        else:
            system.exit_system()
            break
        print("---------------------------------------------------------------------------------")
    print("程序结束")




