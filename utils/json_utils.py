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
def get_json(file_name:str) -> dict:
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
