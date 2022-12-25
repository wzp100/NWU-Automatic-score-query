# 西北大学成绩自动查询
## 基本介绍
使用python自动访问教务网站，通过“重修报名”获得成绩信息。
## 基本机制
重修报名可以第一时间或者成绩，只要老师完成登记，通过修改相应的post请求参数来实现成绩查询
## 基本功能
- 指定查看学期
- 通过邮箱发送通知（已实现）
- 接入青龙面板，通过青龙面板运行（待更新）

## 参考教程
### 一、下载相关代码
将上传的代码打包下载，包括相应的配置文件——xzfjwxt.py（主要的脚本文件）,config.json（相关的配置文件，要和代码在同一文件夹）。
![image](https://user-images.githubusercontent.com/62051751/209475426-664af8fe-76ba-4c31-ab65-d9fc6286f017.png)
### 二、配置相应的参数
打开config.json，按照提示填写相应的内容。


```
{
  "host": "jwgl.nwu.edu.cn",
  "mail_host": "邮箱地址",                例如网易邮箱地址smtp.yeah.net
  "mail_pass": "邮箱密码",                smtp的密码，可能需要额外配置
  "mail_switch": true,                   邮箱通知开关，关闭可以用false
  "mail_user": "邮箱用户名",
  "receiver": "接收邮箱地址",
  "sender": "发送邮箱地址",               也是上面密码所对应的邮箱
  "stu_name": "教务系统用户名",
  "stu_password": "教务系统密码",
  "temp_term": "1",
  "temp_year": "2020",
  "term_0_chongxiu_grade_number": 0,     用来暂时存当前查询到学期科目的数量
  "term_1_chongxiu_grade_number": 0
}
```
