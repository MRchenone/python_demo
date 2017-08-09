#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import itchat,time
from itchat.content import *
@itchat.msg_register([TEXT,MAP,CARD,NOTE,SHARING])
def text_reply(msg):
    itchat.send('%s:%s' % (msg['Type'],msg['Text']),msg['FromUserName'])
@itchat.msg_register([PICTURE,RECORDING,ATTACHMENT,VIDEO])
def download_files(msg):
    msg['Text'](msg['FileName'])
    itchat.send('@%s@%s'%('img' if msg['Type'] == 'Picture' else 'fil',msg['FileName']),msg['FromUserName'])
    return '@%s@%s' % ({'Picture':'img','Video':'vid'}.get(msg['Type'],'fil'),msg['FileName'])
@itchat.msg_register(FRIENDS)
def add_friend(msg):
    itchat.add_friend(**msg['Text'])# 该操作会自动将新好友的消息录入，不需要重载通讯录
    itchat.send_msg('Nice to meet you!',msg['RecommendInfo']['UserName'])
@itchat.msg_register(TEXT,isGroupChat=True)
def text_reply(msg):
    if msg['isAt']:
        itchat.send(u'@%s\u2005T received: %s' % (msg['ActualNickName'],msg['Content']),msg['FromUserName'])
itchat.auto_login(True)
itchat.run()
#用户多开
newInstance=itchat.new_instance()
newInstance.auto_login(hotReload=True,statusStorageDir='newInstance.pkl')
@newInstance.msg_register(TEXT)
def reply(msg):
    return msg['Text']
newInstance.run()