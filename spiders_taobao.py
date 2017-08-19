#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import threading
import requests
import re
import pymongo
import tkinter as tk
from tkinter import messagebox
import time
import xlsxwriter
import matplotlib.pyplot as plt
import numpy as np
import random

# from pylab import *

is_running = False


def get_html(url):
    '''
    访问url链接，取得html源码并返回
    :param url: url链接地址
    :return: 获取正常，返回html源码；出现异常，返回None
    '''
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
        headers = {'User_agent': user_agent}
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        r.encoding = "utf-8"
        return r.text
    except Exception as e:
        info = "获取html出现异常：\n" + str(e)
        print(info)
        print_info(info)
        return None


def parse_data(result, html):
    '''
    从html中提取每个信息，并格式化为字典，存储在result这个列表中的同时，保存到数据库中去
    :param result: 结果列表
    :param html: html源码
    '''

    try:
        titles = re.findall(r'\"raw_title\":\".*?\"', html)
        prices = re.findall(r'\"view_price\":\"[\d.]*\"', html)
        deals = re.findall(
            r'\"view_sales\":\"[0-9]*[1-9][0-9]*[\u4e00-\u9fa5]+\"', html)
        pics = re.findall(r'\"pic_url\":\".*?"', html)
        detailurls = re.findall(r'\"detail_url":\".*?\"', html)
        locations = re.findall(r'\"item_loc\":\"\D*?\"', html)
        shops = re.findall(r'\"nick\":\".*?\"', html)
        shopurls = re.findall(r'\"shopLink\":\".*?\"', html)

        for i in range(len(titles)):
            product = {
                'title':
                    eval(str(titles[i].split(":")[1])),
                'price':
                    eval(str(prices[i].split(":")[1])),
                'deal':
                    eval(str(deals[i].split(":")[1]))[:-3],
                'pic':
                    "https:" + eval(str(pics[i].split(":")[1])),
                'detailurl':
                    ("https:" + eval(str(detailurls[i].split(":")[1]))
                     ).encode("unicode_escape").decode("unicode_escape"),
                'location':
                    eval(str(locations[i].split(":")[1])),
                'shop':
                    eval(str(shops[i].split(":")[1])),
                'shopurl':
                    "https:" + eval(str(shopurls[i].split(":")[1])).encode(
                        "unicode_escape").decode("unicode_escape")
            }
        print(product)
        result.append(product)

    except Exception as e:
        info = "提取信息出现异常：\n" + str(e)
        print(info)
        print_info(info)

def save_to_db(dburl, dbport, dbname, dbuser, dbpwd, dbtable, products):
    info = "正在保存数据到数据库。"
    print_info(info)
    print(info)

    client = pymongo.MongoClient(host=dburl, port=int(dbport))

    if dbuser and dbpwd:
        client['admin'].authenticate(dbuser, dbpwd, dbname, 'DEFAULT')

    db = client[dbname]

    try:
        db[dbtable].insert_many(products)
    except Exception as e:
        info = "保存到数据库出现异常：\n" + str(e) + "\n"
        print_info(info)
        print(info)

    info = "保存到数据库成功。"
    print_info(info)
    print(info)


def spider_crawl(dburl, dbport, dbname, dbuser, dbpwd, dbtable, keyword, depth, mode):
    link = "https://s.taobao.com/search?q=" + keyword + "&sort=sale-desc"
    products = []
    for i in range(int(depth)):
        info = "正在读取第 " + str(i + 1) + " 页。"
        print_info(info)
        print(info)
        try:
            url = link + "&s=" + str(44 * i)
            html = get_html(url)
            parse_data(products, html)
        except Exception as e:
            info = "spider_crawl出现异常：\n" + str(e)
            print_info(info)
            print(info)
            continue
    result_info = "爬取完毕，共获取到 " + str(len(products)) + " 条商品信息。"
    print_info(result_info)
    print(result_info)
    if mode == 1:
        save_to_db(dburl, dbport, dbname, dbuser, dbpwd, dbtable, products)
    elif mode == 2:
        write_to_excel(keyword, dbname, dbtable, products)
    elif mode == 3:
        save_to_db(dburl, dbport, dbname, dbuser, dbpwd, dbtable, products)
        write_to_excel(keyword, dbname, dbtable, products)

    info = "提示：此次爬取信息过程完整结束。"
    print_info(info)
    print(info)
    is_running = False


def write_to_excel(keyword, dbname, dbtable, products):
    # time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time())
    info = "正在保存数据到Excel文件。"
    print_info(info)
    print(info)

    filename = keyword + '_' + dbname + '_' + dbtable + '_' + time.strftime(
        "%Y-%m-%d_%H-%M-%S",
        time.localtime(time.time())) + '_' + str(len(products)) + '.xlsx'
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    headers = [
        '_id', 'title', 'price', 'deal', 'shop', 'location', 'pic',
        'detailurl', 'shopurl'
    ]
    # headers = ['title', 'price', 'deal', 'shop', 'location']
    header_row = 0
    for header in headers:
        col = headers.index(header)
        worksheet.write(header_row, col, header)

    # worksheet.write_rich_string(data_row, col, str(_value))
    data_row = 1
    for product in products:
        for _key, _value in product.items():
            col = headers.index(_key)
            if _key == '_id' or _key == 'pic' or _key == 'detailurl' or _key == 'shopurl':
                worksheet.write_rich_string(data_row, col, str(_value))
            else:
                worksheet.write(data_row, col, str(_value))
        data_row += 1
    workbook.close()
    info = "成功保存数据到Excel文件。"
    print_info(info)
    print(info)


def crawl():
    is_running = True

    db_url = entry_db_url.get()
    db_port = entry_db_port.get()
    db_name = entry_db_name.get()
    db_user = entry_db_user.get()
    db_pwd = entry_db_pwd.get()
    db_table = entry_db_table.get()
    keyword = entry_keyword.get()
    depth = entry_depth.get()

    mode = var_radio.get()

    if mode == 0:
        messagebox.showerror(title='错误！', message='没有选择数据保存方式！')
    elif mode == 1 or mode == 3:
        if db_url and db_port and db_name and db_table and keyword and depth:
            if int(depth) > 100:
                depth = 100
            elif int(depth) <= 0:
                depth = 1
            run_in_thread(spider_crawl, db_url, db_port, db_name, db_user, db_pwd, db_table,
                          keyword, depth, mode)
        else:
            messagebox.showerror(title='错误！', message='如果您的数据库不需要登录，则④⑤两项可以不填；否则，①~⑧项必须全部填写！')
    elif mode == 2:
        if keyword and depth:
            run_in_thread(spider_crawl, db_url, db_port, db_name, db_table,
                          keyword, depth, mode)
        else:
            messagebox.showerror(title='错误！', message='⑦⑧项必须全部填写！')
def run_in_thread(func, *args):
    t = threading.Thread(target=func, args=args)
    t.setDaemon(True)
    t.start()


def exit_app():
    if is_running:
        messagebox.showerror(title='不能退出！', message='程序还在运行，请等待程序运行完毕后再退出。')
    else:
        root.quit()


def print_info(info):
    result_text.insert('end',
                       "\n" + info + "\n------------------------------------")
    result_text.see("end")


def radio_selector():
    return var_radio.get()


def read_from_db():
    dburl = entry_db_url.get()
    dbport = entry_db_port.get()
    dbname = entry_db_name.get()
    dbuser = entry_db_user.get()
    dbpwd = entry_db_pwd.get()
    dbtable = entry_db_table.get()

    client = pymongo.MongoClient(host=dburl, port=int(dbport))

    if dbuser and dbpwd:
        client['admin'].authenticate(dbuser, dbpwd, 'admin', 'DEFAULT')

    db = client[dbname]

    items = db[dbtable].find({}, {'price': 1, 'deal': 1, '_id': 0})

    results = {}
    for item in items:
        results[item['deal']] = item['price']
    return results


def show_linear_chart():

    # mpl.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    # mpl.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    datas = read_from_db()

    max_deal = max(datas.keys(), key=lambda x: int(x))
    min_deal = min(datas.keys(), key=lambda x: int(x))
    max_price = max(datas.values(), key=lambda x: float(x))
    min_price = min(datas.values(), key=lambda x: float(x))

    y_ticks = np.linspace(int(min_deal), int(max_deal), 10, endpoint=False)
    x_ticks = np.linspace(float(min_price), float(max_price), 10, endpoint=False)

    plt.figure()
    plt.title("线性图表",fontproperties='SimHei',fontsize=20,color='green')
    plt.xlabel("商品价格（元）",fontproperties='SimHei',fontsize=15,color='green')
    plt.ylabel("商品销量（件）",fontproperties='SimHei',fontsize=15,color='green')
    ax = plt.gca()
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    # y, x = zip(*sorted(datas.items()))
    # plt.plot(x, y)
    # plt.plot(*zip(*sorted(datas.items())))
    new_list = zip(datas.values(), datas.keys())
    new_datas = sorted(new_list, key=lambda x: float(x[0]))
    # print(new_datas)
    x, y = zip(*new_datas)
    plt.plot(x, y)
    plt.show()


def show_scatter_chart():
    datas = read_from_db()

    max_deal = max(datas.keys(), key=lambda x: int(x))
    min_deal = min(datas.keys(), key=lambda x: int(x))
    max_price = max(datas.values(), key=lambda x: float(x))
    min_price = min(datas.values(), key=lambda x: float(x))

    y_ticks = np.linspace(int(min_deal), int(max_deal), 10, endpoint=False)
    x_ticks = np.linspace(float(min_price), float(max_price), 10, endpoint=False)

    plt.figure()
    plt.title("散点图表",fontproperties='SimHei',fontsize=20,color='green')
    plt.xlabel("商品价格（元）",fontproperties='SimHei',fontsize=15,color='green')
    plt.ylabel("商品销量（件）",fontproperties='SimHei',fontsize=15,color='green')
    ax = plt.gca()
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)

    new_list = zip(datas.values(), datas.keys())
    new_datas = sorted(new_list, key=lambda x: float(x[0]))
    # print(new_datas)
    # y, x = zip(*sorted(datas.items()))
    x, y = zip(*new_datas)
    plt.scatter(x, y, c='r')
    plt.show()


def show_bar_chart():
    # 随着价格的升高，销量的变化
    datas = read_from_db()

    max_deal = max(datas.keys(), key=lambda x: int(x))
    min_deal = min(datas.keys(), key=lambda x: int(x))
    max_price = max(datas.values(), key=lambda x: float(x))
    min_price = min(datas.values(), key=lambda x: float(x))

    y_ticks = np.linspace(int(min_deal), int(max_deal), 10, endpoint=False)
    x_ticks = np.linspace(float(min_price), float(max_price), 10, endpoint=False)

    plt.figure()
    plt.title("柱状图表", fontproperties='SimHei', fontsize=20, color='green')
    plt.xlabel("商品价格（元）", fontproperties='SimHei', fontsize=15, color='green')
    plt.ylabel("商品销量（件）", fontproperties='SimHei', fontsize=15, color='green')
    ax = plt.gca()
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)

    # new_list = zip(datas.values(), datas.keys())
    new_list = sorted(zip(datas.values(), datas.keys()), key=lambda x: float(x[0]))
    sample = random.sample(new_list, int(len(new_list) * 0.3))
    sorted_sample = sorted(sample, key=lambda x: float(x[0]))
    print(sorted_sample)

    x_list = []
    y_list = []
    for x, y in sorted_sample:
        x_list.append(float(x))
        y_list.append(int(y))
    plt.bar(x_list, y_list, width=5.0, facecolor='blue', edgecolor='')
    plt.show()


title = '淘宝商品定向爬虫'
author = 'Powered by MRchenone'
font_normal_size = 14
root = tk.Tk()
root.title(title)
root.geometry('820x700')
root.anchor('center')
root.resizable(0, 0)

label_title = tk.Label(root, text=title, font=('', 26))
label_title.pack(anchor='center')

label_author = tk.Label(root, text=author, font=('', 14), fg='blue')
label_author.place(x=300, y=50)

label_db_url = tk.Label(root, text='①数据库地址：', font=('', font_normal_size))
label_db_url.place(x=100, y=100)
entry_db_url = tk.Entry(root, show=None, font=('', font_normal_size))
entry_db_url.insert('end', '108.61.162.201')
entry_db_url.place(x=250, y=100)

label_db_port = tk.Label(root, text='②数据库端口：', font=('', font_normal_size))
label_db_port.place(x=100, y=150)
entry_db_port = tk.Entry(root, show=None, font=('', font_normal_size))
entry_db_port.insert('end', '10000')
entry_db_port.place(x=250, y=150)

label_db_name = tk.Label(root, text='③数据库名称：', font=('', font_normal_size))
label_db_name.place(x=100, y=200)
entry_db_name = tk.Entry(root, show=None, font=('', font_normal_size))
entry_db_name.insert('end', 'jack')
entry_db_name.place(x=250, y=200)

label_db_user = tk.Label(root, text='④数据库用户：', font=('', font_normal_size))
label_db_user.place(x=100, y=250)
entry_db_user = tk.Entry(root, show=None, font=('', font_normal_size))
entry_db_user.insert('end', 'jack')
entry_db_user.place(x=250, y=250)

label_db_pwd = tk.Label(root, text='⑤数据库密码：', font=('', font_normal_size))
label_db_pwd.place(x=100, y=300)
entry_db_pwd = tk.Entry(root, show=None, font=('', font_normal_size))
entry_db_pwd.insert('end', '1238912389')
entry_db_pwd.place(x=250, y=300)

label_db_table = tk.Label(root, text='⑥数据库表名：', font=('', font_normal_size))
label_db_table.place(x=100, y=350)
entry_db_table = tk.Entry(root, show=None, font=('', font_normal_size))
entry_db_table.insert('end', 'coffee')
entry_db_table.place(x=250, y=350)

label_keyword = tk.Label(root, text='⑦商品关键词：', font=('', font_normal_size))
label_keyword.place(x=100, y=400)
entry_keyword = tk.Entry(root, show=None, font=('', font_normal_size))
entry_keyword.insert('end', '黑咖啡')
entry_keyword.place(x=250, y=400)

label_depth = tk.Label(root, text='⑧深度≤100：', font=('', font_normal_size))
label_depth.place(x=100, y=450)
entry_depth = tk.Entry(root, show=None, font=('', font_normal_size))
entry_depth.insert('end', '10')
entry_depth.place(x=250, y=450)

result_text = tk.Text(root, font=('', font_normal_size), width=53, height=8)
result_text.place(x=100, y=500)

button_run = tk.Button(
    root, text='开始爬取', font=('', font_normal_size), command=crawl)
button_run.place(x=520, y=250)

button_exit = tk.Button(
    root, text='退出程序', font=('', font_normal_size), command=exit_app)
button_exit.place(x=640, y=250)

button_tu_1 = tk.Button(
    root, text='线性图表', font=('', font_normal_size), command=show_linear_chart)
button_tu_1.place(x=520, y=300)

button_tu_2 = tk.Button(
    root, text='散点图表', font=('', font_normal_size), command=show_scatter_chart)
button_tu_2.place(x=640, y=300)

button_tu_3 = tk.Button(
    root, text='柱状图表', font=('', font_normal_size), command=show_bar_chart)
button_tu_3.place(x=520, y=350)

var_radio = tk.IntVar()
radio_db = tk.Radiobutton(
    root,
    text='保存到数据库',
    variable=var_radio,
    value=1,
    font=('', font_normal_size))
radio_db.place(x=520, y=100)

radio_excel = tk.Radiobutton(
    root,
    text='导出到Excel文件',
    variable=var_radio,
    value=2,
    font=('', font_normal_size))
radio_excel.place(x=520, y=150)

radio_both = tk.Radiobutton(
    root,
    text='两种方式同时执行',
    variable=var_radio,
    value=3,
    font=('', font_normal_size))
radio_both.place(x=520, y=200)

root.mainloop()
