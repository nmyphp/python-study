#!/usr/local/bin/python3
# _*_ coding: UTF-8 _*_

import random

print("====开始猜数字游戏====")
temp = input("请输入你心中所想的数字：")
luckNumber = int(temp)
answer = random.randint(1,100)
while luckNumber != answer:
    temp = input("猜错了，再来一次：") 
    luckNumber = int(temp)
    if luckNumber > answer:
        print("大了哦")
    elif luckNumber < answer:
        print("小了哦")
    else:
        break
print("恭喜你猜对了")
print("游戏结束")
