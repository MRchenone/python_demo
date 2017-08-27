#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'MRchenone'
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os

class TBMR:
    #初始化，传入基本部分和参数部分
    def __init__(self):
        pass
    #获取首页的页面信息
    def getMMsInfo(self):
        url='https://www.taobao.com/markets/mm/mmku'
        driver=webdriver.Chrome()
        driver.get(url)
        try:
            element=WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,"skip-wrap"))) #查好10秒内是否有页码出现
            print("成功提取页码")
            soup=BeautifulSoup(driver.page_source,"html.parser")
            #获取到了全部的页码
            pageNum=soup.find('span',class_='skip-wrap').find('em').text
            print('开始爬去头像！')
            #同时得保存第一出现的图片，因为观察可得，原网页当前页是不能点击的，所以第一次不能通过点击完成
            #获取网页内容
            soup=BeautifulSoup(driver.page_source,'html.parser')
            mms=soup.find_all('div',class_='cons_li')
            #对于每一个mm对象，获取其名字和头像
            self.saveMMS(mms)
            #从第2页开始便利点击
            for i in range(2,int(pageNum)):
                #点击当前页
                curpage=driver.find_element_by_link_text(str(i))
                curpage.click()
                #等待当前页加载完成
                pics=WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,'skip-wrap')))
                #获取当前页面
                soup=BeautifulSoup(driver.page_source,'html.parser')
                mms=soup.find_all('div',class_='cons_li')
                #对于每一个mm对象,获取其名字和头像
                self.saveMMS(mms)
                print('当前完成：第'+str(i)+'页')
        finally:
            driver.quit()
    #从一个mms对象保存
    def saveMMS(self,mms):
        for mm in mms:
            name=mm.find('div',class_='item_name').find('p').text
            img=mm.find('div',class_='item_img').find('img').get('src')
            #如果路径不存在，设置存储路径
            dirpath=os.getcwd()+'\\美人\\'
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            namepath=os.getcwd()+'\\美人\\'+name+'.jpg'
            self.saveImg(img,namepath)
    #保存一张照片
    def saveImg(self,imageURL,fileName):
        if not 'http' in imageURL:# 去掉src布格化的图片：eg  //img.alicdn.com/imgextra/i3/728310618/TB2s7glc3NlpuFjy0FfXXX3CpXa_!!728310618-2-beehive-scenes.png_468x468q75.jpg，是无法识别的
            return
        u=requests.get(imageURL,stream=True).content

        try:
            with open(fileName,'wb') as jpg:
                jpg.write(u)
        except IOError:
            print('写入图片错误！')
    #开始函数
    def start(self):
        print('抓起淘女郎-美人库第一页的内容，并存储于\" 美人 \" 文件夹下')
        self.getMMsInfo()
        print('下载完成！')

tbmm=TBMR()
tbmm.start()