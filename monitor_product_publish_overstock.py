#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb
import smtplib
import logging
from email.mime.text import MIMEText
from email.header import Header

mail_from = "358829805@qq.com"  # 发件人
mail_to = ["123232433@qq.com"]  # 收件人
mail_host = "smtp.qq.com"  # 发送服务器
mail_user = "358829805@qq.com"  # 用户名
mail_pass = "jjujucelsijhcagf"  # 口令
mail_sub = Header("天猫产品发品积压监控，测试邮件", "utf-8")  # 主题


# create logger
def create_logger(log_name):
    logging.basicConfig(level=logging.INFO, filename="info.log", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    console_handle = logging.StreamHandler()  # create console handler and set level to debug
    console_handle.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # create formatter
    console_handle.setFormatter(formatter)  # add formatter to ch
    logger.addHandler(console_handle)  # add ch to logger
    return logger


# 发送邮件
def send_mail(fro, to, sub, content):
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = sub
    msg['From'] = fro
    msg['To'] = ";".join(to)
    msg['Accept-Language'] = 'zh-CN'
    msg['Accept-Charset'] = 'utf-8'
    try:
        server = smtplib.SMTP_SSL(mail_host, 465)
        server.login(mail_user, mail_pass)
        server.sendmail(fro, to, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(e)
        return False


# 查询TMALLCloudDB.product_publish_handle中待发布的商品数量
def query_db():
    try:
        db = MySQLdb.connect("10.255.209.111", "dev_writer", "dev_writer", "TMALLCloudDB", 8306)  # 打开数据库连接
        cursor = db.cursor()  # 获取操作游标
        cursor.execute("SELECT COUNT(*) num FROM product_publish_handle WHERE status = 0 AND NOW() >= IFNULL(next_deal_time,NOW())")
        data = cursor.fetchone()  # 获取一条数据库。
        db.close()  # 关闭数据库连接
        return data[0]  # 未处理的产品数量
    except Exception as e:
        print(e)
        return 0


# 主函数入口
if __name__ == '__main__':
    log = create_logger("main")
    num = query_db()
    send_result = False
    content = ""
    log.info("待发布产品数为%d", num)
    if num > 100000:
        content += "产品发布积压>100000，请尽快处理！"
    elif num > 2000:
        content += "产品发布积压>2000，请尽快处理！"
    elif num > 1000:
        content += "产品发布积压>1000，请尽快处理！"
    elif num > 200:
        content += "产品发布积压>200，请尽快处理！"
    elif num > 100:
        content += "产品发布积压>100，请尽快处理！"
    elif num > 20:
        content += "产品发布积压>20，请尽快处理！"
    elif num > 5:
        content += "产品发布积压>5，请尽快处理！"
    if not "".endswith(content):
        if send_mail(mail_from, mail_to, mail_sub, content):
            log.info("发送邮件成功！")
        else:
            log.info("发送邮件失败！")
