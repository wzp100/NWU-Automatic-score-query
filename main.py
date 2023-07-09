from aamsystem import AAMSystem
from student import *
from utils.json_utils import is_json_exist

# 重修成绩查询
def get_chongxiu_grade(system: AAMSystem, student: Student, configName: str):
    # 系统登录
    system.login(student)
    # 成绩查询
    student = system.get_chongxiu_grade()
    # 打印成绩
    student.print_grade()
    # 保存数据
    student.save_student_info(configName)

    choice = input("按回车退出，或者按1重新登录，按2更改学年重新查询：")
    if choice == "1":
        print("重新查询，请输入学号和密码")
        system.logout()
        return "1"
    elif choice == "2":
        print("更改学年重新查询")
        year = input("学年（例如2022）：")
        student.change_school_year(year)
        return "2"
    else:
        print("退出程序")
        # 退出系统
        system.exit_system()
        return "0"



if __name__ == '__main__':
    print("重修成绩查询程序启动")
    test = True
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
        stu.save()
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




