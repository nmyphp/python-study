#!/usr/local/bin/python3
# coding=utf-8

import os
import re
import time
import _thread
import itchat
from itchat.content import *

# 可以撤回的消息格式：文本、语音、视频、图片、位置、名片、分享、附件
# 存储收到的消息
# 格式：{msg_id:{msg_from,msg_to,msg_time,msg_time_rec,msg_tye,msg_content,msg_share_url}}
msg_dict = {}

# 存储消息中文件的临时目录，程序启动时，先清空
rev_tmp_dir = "/Users/chenlong/d1/wechat/rev/"
if not os.path.exists(rev_tmp_dir):
    os.mkdir(rev_tmp_dir)
else:
    for f in os.listdir(rev_tmp_dir):
        path = os.path.join(rev_tmp_dir, f)
        if os.path.isfile(path):
            os.remove(path)

# 表情有一个问题：消息和撤回提示的msg_id不一致
face_bug = None


# 监听微信消息（只限可撤回的消息类型），存储到本地，并清除超时的消息
# 可撤回的消息类型：TEXT、PICTURE、MAP、CARD、SHARING、RECORDING、ATTACHMENT、VIDEO、FRIENDS、NOTE
@itchat.msg_register([TEXT, PICTURE, MAP, CARD, SHARING, RECORDING, ATTACHMENT, VIDEO, FRIENDS, NOTE],
                     isFriendChat=True, isGroupChat=True, isMpChat=True)
def handler_reveive_msg(msg):
    global face_bug
    msg_time_rev = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    msg_id = msg['MsgId']
    msg_time = msg['CreateTime']
    msg_share_url = None
    group_name = None
    # 获取发送人
    if 'ActualNickName' in msg:
        sender_info = set_sender_group_chat(msg)
        msg_from = sender_info['msg_from']
        group_name = sender_info['group_name']
    else:
        msg_from = (itchat.search_friends(userName=msg['FromUserName']))['RemarkName']  # 优先使用备注
        if msg_from is None:
            msg_from = msg['FromUserName']

    # 获取消息内容
    if msg['Type'] == 'Text' or msg['Type'] == 'Friends':
        msg_content = msg['Text']
    elif msg['Type'] == 'Recording' or msg['Type'] == 'Attachment' \
            or msg['Type'] == 'Video' or msg['Type'] == 'Picture':
        msg_content = r"" + msg['FileName']
        msg['Text'](rev_tmp_dir + msg['FileName'])
    elif msg['Type'] == 'Card':
        msg_content = msg['RecommendInfo']['NickName'] + r" 的名片"
    elif msg['Type'] == 'Map':
        x, y, location = re.search("<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1,
                                                                                                                    2,
                                                                                                                    3)
        if location is None:
            msg_content = r"维度->" + x + " 经度->" + y
        else:
            msg_content = r"" + location
    elif msg['Type'] == 'Sharing':
        msg_content = msg['Text']
        msg_share_url = msg['Url']

    face_bug = msg_content
    # 缓存消息
    msg_dict.update({
        msg_id: {
            "msg_from": msg_from,
            "msg_time": msg_time,
            "msg_time_rev": msg_time_rev,
            "msg_type": msg['Type'],
            "msg_content": msg_content,
            "msg_share_url": msg_share_url,
            "group_name": group_name
        }
    })


# 遍历本地消息字典，清除2分钟之前的消息，并删除缓存的消息对应的文件
def clear_timeout_msg():
    need_del_msg_ids = []
    for m in msg_dict:
        msg_time = msg_dict[m]['msg_time']
        if int(time.time()) - msg_time > 120:
            need_del_msg_ids.append(m)

    if len(need_del_msg_ids) > 0:
        for i in need_del_msg_ids:
            old_msg = msg_dict.get(i)
            if old_msg['msg_type'] == PICTURE or old_msg['msg_type'] == RECORDING or old_msg['msg_type'] == VIDEO \
                    or old_msg['msg_type'] == ATTACHMENT:
                os.remove(rev_tmp_dir + old_msg['msg_content'])
            msg_dict.pop(i)


# 设置发送人，当消息是群消息的时候
def set_sender_group_chat(msg):
    msg_from = msg['ActualNickName']
    # 查找用户备注名称
    friends = itchat.get_friends(update=True)
    from_user = msg['ActualUserName']
    for f in friends:
        if from_user == f['UserName']:
            msg_from = f['RemarkName'] or f['NickName']
            break

    groups = itchat.get_chatrooms(update=True)
    for g in groups:
        if msg['FromUserName'] == g['UserName']:
            group_name = g['NickName']
            break

    return {'msg_from': msg_from, 'group_name': group_name}


# 监听通知，判断是撤回通知，则将消息发给文件助手
@itchat.msg_register([NOTE], isFriendChat=True, isGroupChat=True, isMpChat=True)
def send_msg_helper(msg):
    global face_bug
    if re.search(r"\<\!\[CDATA\[.*撤回了一条消息\]\]\>", msg['Content']) is not None:
        old_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
        old_msg = msg_dict.get(old_msg_id, {})
        if len(old_msg_id) < 11:
            itchat.send_file(rev_tmp_dir + face_bug, toUserName='filehelper')
            os.remove(rev_tmp_dir + face_bug)
        else:
            msg_body = old_msg.get('msg_from') + "撤回了" + old_msg.get('msg_type') \
                       + "消息\n" \
                       + old_msg.get('msg_time_rev') + "\n" \
                       + old_msg.get('msg_content')
            if old_msg.get('group_name') is not None:
                msg_body = old_msg.get('group_name') + ">" + msg_body
            if old_msg['msg_type'] == "Sharing":
                msg_body += "\n" + old_msg.get('msg_share_url')
            # 将撤回的消息发给文件助手
            itchat.send(msg_body, toUserName='filehelper')
            if old_msg['msg_type'] == PICTURE or old_msg['msg_type'] == RECORDING or old_msg['msg_type'] == VIDEO \
                    or old_msg['msg_type'] == ATTACHMENT:
                file = '@fil@%s' % (rev_tmp_dir + old_msg['msg_content'])
                itchat.send(msg=file, toUserName='filehelper')
                os.remove(rev_tmp_dir + old_msg['msg_content'])
            msg_dict.pop(old_msg_id)


if __name__ == '__main__':
    itchat.auto_login(hotReload=True, enableCmdQR=2)
    itchat.run()
    # 子线程清除超时消息
    _thread.start_new_thread(clear_timeout_msg)
