#!/usr/local/bin/python3
# coding=utf-8

# 初始化用户列表为None
user_list = []


class User:
    def __init__(self, user_name=None, password=None):
        self.user_name = user_name
        self.password = password

    def __repr__(self):
        return 'userName=%s\tpassword=%s' % (self.user_name, self.password)

    def update(self, user_name, password):
        self.user_name = user_name
        self.password = password


# 显示所有的用户信息
def show_all():
    if len(user_list) == 0:
        print("系统中还没有用户")
        return
    print("用户列表如下：")
    for user in user_list:
        print(user)
    input("按Enter键继续...")


def add_user():
    user_name = input_valid_str("用户名", "用户名不能为空")
    password = input_valid_str("密码", "密码不能为空")
    user_list.append(User(user_name, password))
    print("用户添加成功")

# 输入非空值，对其校验，直到有效为止
def input_valid_str(label, prompt):
    while True:
        input_prompt = "请输入%s：" % label
        user_name = input(input_prompt).strip()
        if user_name == '':
            print(prompt)
        else:
            return user_name


# 删除指定用户名的用户
def delete_user(user_name):
    for user in user_list:
        if user.user_name == user_name:
            user_list.remove(user)
            print("已删除用户:" + str(user))
            break
    else:
        print("系统不存在该用户：" + user_name)


# 更新用户信息
def update_user(user_name):
    for user in user_list:
        if user.user_name == user_name:
            password = input_valid_str("密码", "密码不能为空")
            user.update(user_name, password)
            break
    else:
        print("系统不存在该用户：" + user_name)


# 查找用户
def find():
    user_name = input_valid_str("用户名", "用户名不能为空")
    for user in user_list:
        if user.user_name == user_name:
            return user
    print("系统不存在该用户：" + user_name)
    while True:
        yes_or_on = input("需要添加该用户吗？Y/N：")
        if yes_or_on == 'Y':
            password = input_valid_str("密码", "密码不能为空")
            user_list.append(User(user_name, password))
            print("用户添加成功")
            break
        elif yes_or_on == 'N':
            return None


# 程序入口
if __name__ == '__main__':
    ui = "=========欢迎进入用户信息管理系统==========\n\t1. 查看全部用户\n\t2. 查找用户/修改用户/删除用户\n\t3. 添加用户\n\t4. 保存用户数据\n\t5. 退出系统"
    while True:
        action = input(ui).strip()
        if not action.isalnum():
            print("请输入1~5之间的整数：")
            continue
        if action == '1':
            show_all()
        elif action == '2':
            user = find()
            if user is not None:
                print(user)
                action = input("\t1. 修改用户\n\t2. 删除用户\n\t3. 返回")
                if action == '1':
                    update_user(user.user_name)
                elif action == '2':
                    delete_user(user.user_name)
                elif action == '3':
                    continue
                else:
                    print("输入有误，默认返回")
                    continue
        elif action == '3':
            add_user()
        elif action == '4':
            input("暂未实现,按Enter键返回...")
        elif action == '5':
            break






