# 西北大学成绩自动查询
## 修订记录
### 2023年7月7日
- 修复了了config.json编码问题，将原来的gbk编码改为utf-8编码
- 增加了一个精简的查询脚本**miniQuery.py**，只能查询成绩，不能发送邮件，强烈推荐使用
- 将大的文件拆分为多个文件，方便二次开发
- 增加了一个userData.json文件，用来存储miniQuery.py用户的信息
- 打包了miniQuery.py，可以直接在电脑运行
## 文件构成
- miniQuery.py:精简的查询脚本，只能查询成绩，不能发送邮件
- userData.json：用来存储miniQuery.py用户的信息，具体配置见后文
- dist:里面有打包好的exe文件，可以直接运行。第一次运行需要输入账号密码，之后会自动保存
- README.md:说明文件
- requirements.txt:依赖文件
- xzfjwxt.py:主要的脚本文件（旧版本，未来将会被取消）
- config.json:配置文件（旧版配置文件）
## 基本介绍
使用python自动访问教务网站，通过“重修报名”获得成绩信息。
## 基本机制
重修报名可以第一时间或者成绩，只要老师完成登记，通过修改相应的post请求参数来实现成绩查询
## 基本功能
- 指定查看学期
- 通过邮箱发送通知（已实现）（旧版）
- 接入青龙面板，通过青龙面板运行（待更新）
- 打包exe文件，通过exe文件运行

## 参考教程
### 一、下载相关代码

将上传的代码打包下载，包括相应的配置文件——**miniQuery.py**（主要的脚本文件）,**userData.json**（相关的配置文件，要和代码在同一文件夹）。
以下不建议使用，因为代码已经更新，不再使用这种方式。可以考虑使用miniQuery.py，以及配置文件userData.json。
~~将上传的代码打包下载，包括相应的配置文件——xzfjwxt.py（主要的脚本文件）,config.json（相关的配置文件，要和代码在同一文件夹）。~~

![image](https://user-images.githubusercontent.com/62051751/209475426-664af8fe-76ba-4c31-ab65-d9fc6286f017.png)
### 二、配置相应的参数
#### 使用miniQuery.py（强烈推荐）
miniQuery.py需要打开userData.json进行配置
对应的json格式如下：
```json
{
  "id": "",                 // 学号，必填
  "lower_term_grade_num": 0,// 用来暂时存当前查询到学期科目的数量，可以不动
  "name": "",               // 姓名，可以不填
  "password": "",           // 密码，必填
  "upper_term_grade_num": 0 // 用来暂时存当前查询到学期科目的数量，可以不动
}
```
**注意：请不要在json文件中添加注释，否则会报错**
#### ~~使用xzfjwxt.py（不推荐）~~
~~打开config.json，按照提示填写相应的内容。~~
```json
{
  "host": "jwgl.nwu.edu.cn",
  "mail_host": "邮箱地址",                // 例如网易邮箱地址smtp.yeah.net
  "mail_pass": "邮箱密码",                // smtp的密码，可能需要额外配置
  "mail_switch": true,                  // 邮箱通知开关，关闭可以用false
  "mail_user": "邮箱用户名",
  "receiver": "接收邮箱地址",
  "sender": "发送邮箱地址",               // 也是上面密码所对应的邮箱
  "stu_name": "教务系统用户名",
  "stu_password": "教务系统密码",
  "temp_term": "1",
  "temp_year": "2020",
  "term_0_chongxiu_grade_number": 0,     // 用来暂时存当前查询到学期科目的数量
  "term_1_chongxiu_grade_number": 0
}
```
### 三、配置环境
如果打算直接使用打包好的exe文件，可以跳过这一步。
#### 使用miniQuery.py（强烈推荐）
1. 安装python3.8以上版本
2. 安装依赖包具体见requirements.txt
3. 在项目文件夹中打开终端，在命令行中运行如下命令安装依赖包
```pip install -r requirements.txt```
### 四、运行
#### 使用miniQuery.py（强烈推荐）
1. 在项目文件夹中打开终端，在命令行中运行如下命令运行脚本
```python miniQuery.py```
2. 第一次运行需要输入账号密码，之后会自动保存
#### 直接使用exe文件运行
1. 下载dist文件夹中的exe文件**miniQuery.exe**
2. 双击运行
3. 第一次运行需要输入账号密码，之后会自动保存
4. 如果需要修改账号密码，可以删除userData.json文件，重新运行exe文件，或者直接修改userData.json文件

### 五、其他
#### 使用miniQuery.py
##### 1. 程序打包
在项目文件夹中打开终端，在命令行中运行如下命令打包exe文件
```pyinstaller -F miniQuery.py```