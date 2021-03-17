# -*- coding: utf-8 -*-
import login
import requests
import json
import logging
import traceback
import notify
import check
import sys
import os

#引入任务模块
import scheduler

#用户登录全局变量
client = None


#读取用户配置信息
#错误原因有两种：格式错误、未读取到错误
def readJson():
    try:
        #用户配置信息
        with open('./config.json','r') as fp:
            users = json.load(fp)
            return users
    except Exception as e:
        print(traceback.format_exc())
        logging.error('账号信息获取失败错误，原因为: ' + str(e))
        logging.error('1.请检查是否在Secrets添加了账号信息，以及添加的位置是否正确。')
        logging.error('2.填写之前，是否在网站验证过Json格式的正确性。')


def main(event, context):
    ip,country=check.getnetinfo()
    logging.info('【网络自检】: ' + str(ip) +'（'+ str(country) +'）')
    logging.info('【环境自检】: ' + check.system()+'('+check.cpu()+')')
    if check.system() == 'Linux':
        virtual_mode = str(check.virtual())
        logging.info('【环境自检】: 虚拟化类型：' + virtual_mode)
        if virtual_mode != 'none':
            logging.info('【环境自检】:您的系统异常，但本版本未做限制，通过！ ')
    if str(country)!='China':
        logging.info('【网络自检】:您的网络异常，但本版本未做限制，通过！ ')
    users = readJson()
    for user in users:
        #清空上一个用户的日志记录
        open('./log.txt',mode='w',encoding='utf-8')
        global client
        client = login.login(user['username'],user['password'],user['appId'])
        username = user['username']
        if ('lotteryNum' in user):
            lotteryNum = user['lotteryNum']
        else:
            lotteryNum = 0
        #任务调度代码
        if client != False:
            scheduler.runscheduler(client,username,lotteryNum)
        else:
            logging.error('发生登陆错误，退出')
            sys.exit()
        scheduler.resetJson('./','./',0)
        if ('email' in user) :
            notify.sendEmail(user['email'])
        if ('dingtalkWebhook' in user) :
            notify.sendDing(user['dingtalkWebhook'])
        if ('telegramBot' in user) :
            notify.sendTg(user['telegramBot'])
        if ('pushplusToken' in user):
            notify.sendPushplus(user['pushplusToken'])
        if('enterpriseWechat' in user):
            notify.sendWechat(user['enterpriseWechat'])
        if('IFTTT' in user):
            notify.sendIFTTT(user['IFTTT'])
        if('Barkkey' in user):
            notify.sendBarkkey(user['Barkkey'])

#主函数入口
if __name__ == '__main__':
    main("","")
