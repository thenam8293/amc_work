# -*- coding: utf8 -*-

from __future__ import division
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, session, flash,jsonify
from functools import wraps
from web_cong_viec import app
import os
import pypyodbc
import uuid
import hashlib
import datetime as dt
import collections
import win32com.client
import random
import json
from operator import itemgetter
from uuid import getnode as get_mac
import ast
import subprocess

start_date_demo = dt.datetime(2017,8,16)
special_day = dt.datetime(1993,9,19)
time_begin_default = '07:00'
time_finish_default = '21:00'
work_hour_default = 14
min_unit_default = 15

task_field = ['task_id', 'name', 'type', 'type_strategy', 'content', 'status', 'percentage', 'executer', 'assigner', 'supporter', 'executer_name', 'assigner_name','supporter_name','customer','disable', 'start_time','end_time','last_update','rating','department','type_department','border_color']
event_field = ['task_id','event_id', 'name', 'type', 'type_strategy', 'content', 'status', 'percentage', 'executer', 'assigner','supporter', 'executer_name', 'assigner_name','supporter_name','customer','disable','start_time','end_time','complete','department','type_department','border_color']

department_field = ["department","type_department","type","type_strategy"]

noti_field = ['username','content','time','redirect','session','read_fake','read_real','user_cmt','noti_id']

cmt_field = ['task_id','user','cmt','time']

setting_log_field = ['username','time_begin','time_finish','min_unit','time_change']

list_type = [u'Đánh giá hồ sơ', u'Khảo sát khách hàng', u'Khảo sát TSĐB', u'Phối hợp XLN với các bên khác', u'Xây dựng phương án XLN/ Điều chỉnh phương án XLN', u'Công tác hồ sơ giấy tờ', u'Công tác trình ký', u'Tác nghiệp', u'Khác', u'Công việc nội bộ phục vụ thu nợ', u'Phối hợp XLN với các đơn vị nội bộ', u'Họp', u'Đào tạo', u'Văn hóa tổ chúc', u'Dự án chiên lược']

list_type_strategy =[u'Công việc hàng ngày', u'Khách hàng là trên hết', u'Tính thần phối hợp', u'Cam kết hành động', u'Xây dựng nguồn nhân lực', u'Văn hóa tổ chức', u'Chiến lược']

list_department = [u'Công ty AMC',u'Ban Điều hành',u'Trung tâm bán tài sản MB',u'Trung tâm thu giữ tài sản MB',u'Trung tâm quản trị nợ MB',u'Trung tâm quản trị thông tin',u'Trung tâm tố tụng MB',u'Trung tâm hỗ trợ vận hành và kiểm soát tuân thủ',u'Trung tâm thu hồi nợ tín chấp']

list_department_viettat = [u'Công ty AMC',u'Ban Điều hành',u'Trung tâm bán tài sản MB',u'Trung tâm thu giữ tài sản MB',u'Trung tâm quản trị nợ MB',u'Trung tâm quản trị thông tin',u'Trung tâm tố tụng MB',u'Trung tâm hỗ trợ vận hành và kiểm soát tuân thủ',u'Trung tâm thu hồi nợ tín chấp']

sub_mail = u'Hệ thống quản lý công việc - Công ty AMC'
body_giao_viec = u'{} đã giao cho {} công việc "{}"" cùng với người hỗ trợ {}. Vui lòng truy cập http://10.62.24.161:6868 để biết thêm chi tiết.'
body_hoan_thanh = u'{} đã hoàn thành công việc "{}". Vui lòng truy cập http://10.62.24.161:6868 để biết thêm chi tiết.'
body_edit = u'{} đã thay đổi công việc "{}". Vui lòng truy cập http://10.62.24.161:6868 để biết thêm chi tiết.'

list_ngay_nghi = [dt.date(2017,5,1),dt.date(2017,5,2),dt.date(2017,4,6),dt.date(2017,9,2),dt.date(2017,9,3),dt.date(2017,9,4)]

def hash_user(user):
    return hashlib.md5(user.encode('utf-8')).hexdigest()

def hash_2(user):
    return hashlib.sha1(user.encode('utf-8')).hexdigest()

def hash_3(user):
    return hashlib.sha256(user.encode('utf-8')).hexdigest()

def dt_to_str(x):
    return '{} {}/{}/{}'.format(str(x)[11:16],str(x)[8:10],str(x)[5:7],str(x)[:4])

def d_to_str(x):
    return '{}/{}/{}'.format(str(x)[8:10],str(x)[5:7],str(x)[:4])
def dt_to_str_nguoc(x):
    # Transfer datatime to string
    return str(x.date())[-2:] + '/'+str(x.date())[-5:-3] + '/' +  str(x.date())[:-6]
def dt_to_str2(x):
    # Use for day-picker
    if x.weekday() == 6:
        return u'Chủ Nhật*{}/{}'.format(str(x)[8:10],str(x)[5:7])
    else:
        return u'Thứ {}*{}/{}'.format(str(x.weekday()+2),str(x)[8:10],str(x)[5:7])

def str_to_dt(x):
    try:
        return dt.datetime.strptime(x,'%H:%M %d/%m/%Y')
    except:
        return dt.datetime.strptime(x,'%d/%m/%Y')

def add_time(x,y):
    # x is dateime.time; y is time(minutes)
    full_dt = dt.datetime(1993,9,19,x.hour,x.minute,x.second)
    full_dt = full_dt + dt.timedelta(minutes=y)
    return full_dt.time()

def khung_gio():
    return ['07:00','21:00',15,14]

def index_to_time(x):
    a = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57'] 
    b = [dt.time(7, 0), dt.time(7, 15), dt.time(7, 30), dt.time(7, 45), dt.time(8, 0), dt.time(8, 15), dt.time(8, 30), dt.time(8, 45), dt.time(9, 0), dt.time(9, 15), dt.time(9, 30), dt.time(9, 45), dt.time(10, 0), dt.time(10, 15), dt.time(10, 30), dt.time(10, 45), dt.time(11, 0), dt.time(11, 15), dt.time(11, 30), dt.time(11, 45), dt.time(12, 0), dt.time(12, 15), dt.time(12, 30), dt.time(12, 45), dt.time(13, 0), dt.time(13, 15), dt.time(13, 30), dt.time(13, 45), dt.time(14, 0), dt.time(14, 15), dt.time(14, 30), dt.time(14, 45), dt.time(15, 0), dt.time(15, 15), dt.time(15, 30), dt.time(15, 45), dt.time(16, 0), dt.time(16, 15), dt.time(16, 30), dt.time(16, 45), dt.time(17, 0), dt.time(17, 15), dt.time(17, 30), dt.time(17, 45), dt.time(18, 0), dt.time(18, 15), dt.time(18, 30), dt.time(18, 45), dt.time(19, 0), dt.time(19, 15), dt.time(19, 30), dt.time(19, 45), dt.time(20, 0), dt.time(20, 15), dt.time(20, 30), dt.time(20, 45), dt.time(21, 0)]

    return dt_to_str(dt.datetime.combine(session['day_selected'].date(),[b[i] for i,r in enumerate(a) if r == x][0]))



def time_dif(x,y,z=''):
    ## Return time different (second) between start time and end time
    # x : start time (datetime)
    # y : end time (datetime)
    # z : user
    if z == '':
        z = session['username']
    list_ngay_dt = [x + dt.timedelta(days=i) for i in range(int((y.date() - x.date()).total_seconds()/(24*3600)) + 1)]
    total_time = 0
    if len(list_ngay_dt) == 1:
        total_time = (y-x).total_seconds()
    elif len(list_ngay_dt) == 2:
        total_time += (str_to_dt(khung_gio()[1] + ' ' + d_to_str(list_ngay_dt[0])) - x).total_seconds()
        total_time += (y - str_to_dt(khung_gio()[0] + ' ' + d_to_str(list_ngay_dt[1]))).total_seconds()
    else:
        total_time += (str_to_dt(khung_gio()[1] + ' ' + d_to_str(list_ngay_dt[0])) - x).total_seconds()
        total_time += (y - str_to_dt(khung_gio()[0] + ' ' + d_to_str(list_ngay_dt[-1]))).total_seconds()
        for r in list_ngay_dt[1:-1]:
            total_time += khung_gio()[3]*3600
    return total_time

def dt_to_index(x1,x2,y1,y2):
    if str_to_dt(x1) < str_to_dt(y1):
        first_index = 0
    else:
        first_index = time_dif(str_to_dt(y1),str_to_dt(x1))/300
    if str_to_dt(x2) > str_to_dt(y2):
        if first_index == 0:
            second_index = time_dif(str_to_dt(y1),str_to_dt(y2))/300
        else:
            second_index = time_dif(str_to_dt(x1),str_to_dt(y2))/300
    else:
        if first_index == 0:
            second_index =  time_dif(str_to_dt(y1),str_to_dt(x2))/300
        else:
            second_index =  time_dif(str_to_dt(x1),str_to_dt(x2))/300
    return [int(first_index)+1,int(first_index+second_index)]

def time_dif_management(x,y):
    list_ngay_dt = [x + dt.timedelta(days=i) for i in range(int((y.date() - x.date()).total_seconds()/(24*3600)) + 1)]
    total_time = 0
    if len(list_ngay_dt) == 1:
        total_time = (y-x).total_seconds()
    elif len(list_ngay_dt) == 2:
        total_time += (str_to_dt('21:00 ' + d_to_str(list_ngay_dt[0])) - x).total_seconds()
        total_time += (y - str_to_dt('07:00 ' + d_to_str(list_ngay_dt[1]))).total_seconds()
    else:
        total_time += (str_to_dt('21:00 ' + d_to_str(list_ngay_dt[0])) - x).total_seconds()
        total_time += (y - str_to_dt('07:00 ' + d_to_str(list_ngay_dt[-1]))).total_seconds()
        for r in list_ngay_dt[1:-1]:
            total_time += (21-7)*3600
    return total_time

def dt_to_index_management(x1,x2,y1,y2):
    if str_to_dt(x1) < str_to_dt(y1):
        first_index = 0
    else:
        first_index = time_dif_management(str_to_dt(y1),str_to_dt(x1))/300
    if str_to_dt(x2) > str_to_dt(y2):
        second_index = time_dif_management(str_to_dt(x1),str_to_dt(y2))/300
    else:
        if first_index == 0:
            second_index =  time_dif_management(str_to_dt(y1),str_to_dt(x2))/300
        else:
            second_index =  time_dif_management(str_to_dt(x1),str_to_dt(x2))/300
    return [int(first_index)+1,int(first_index+second_index)]

def condition_in(x1,y1,x2,y2):
    if str_to_dt(x2) < str_to_dt(x1) < str_to_dt(y2) or str_to_dt(x2) < str_to_dt(y1) < str_to_dt(y2) or str_to_dt(x1) <= str_to_dt(x2) < str_to_dt(y2) <= str_to_dt(y1):
        return True
    else:
        return False

def sql(query,var=''):
    # connection = pypyodbc.connect('Driver={SQL Server};Server=10.62.24.123\SQL2008;Database=web_cong_viec_amc_mien_nam;uid=phunq;pwd=aos159753')
    connection = pypyodbc.connect('Driver={SQL Server};Server=10.62.24.161\SQLEXPRESS;Database=WEB_CONG_VIEC_AMC;uid=aos;pwd=aos159753')
    # cursor = connection.cursor()
    # connection = pypyodbc.connect('Driver={SQL Server};Server=10.62.24.123\SQL2008;Database=p;uid=phunq;pwd=aos159753')
    cursor = connection.cursor()
    cursor.execute(query,var)
    if query.lower()[:6] == 'select':
        x = cursor.fetchall()
        cursor.close()
        return x
    else:
        cursor.commit()
        cursor.close()
def sqlite(query,var=''):
    connection = sqlite3.connect(r'C:\Users\phunq\Desktop\p.db')
    # connection = sqlite3.connect(r'K:\Khoi Quan Tri Rui Ro\09 - Du lieu chung\AOS\p.db')
    # connection = sqlite3.connect(r'C:\Users\phunq\Desktop\web_cong_viec_t.db')
    # connection = sqlite3.connect(r'Z:\TEST MIEN NAM\web_cong_viec.db')
    cursor = connection.cursor()
    cursor.execute(query,var)
    if query.lower()[:6] == 'select':
        x = cursor.fetchall()
        cursor.close()
        return x
    elif query.lower()[:6] == 'create':
        cursor.close()
    else:
        connection.commit()
        cursor.close()

def set_keep_order(x):
    return [r[0] for r in collections.OrderedDict.fromkeys(x).items()]

def send_mail(to,cc,sub,body):
    outlook = win32com.client.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)
    for r in outlook.Session.Accounts:
        if r.SmtpAddress == 'qtrr.AOS@techcombank.com.vn':
            mail._oleobj_.Invoke(*(64209,0,8,0,r))
    mail.To = to + '@techcombank.com.vn'
    mail.CC = cc
    mail.Subject = sub
    mail.HTMLBody = body
    try:
        mail.Send()
    except:
        mail.Display()

def send_pass(x):
    new_pass = random.choice([i for i in range(100000,999999)])
    sql("update userr set password = ? where username = ?",[hash_user(str(new_pass)),x])
    send_mail(x,'','New Password','Your new password is {}'.format(new_pass))

def task_id_create():
    p = sql("select max(convert(int,task_id)) from ID_auto_create")[0][0]
    p1 = str(int(p)+1)
    p2 = p1 + '.0'
    sql("insert into ID_auto_create(task_id,event_id) values(?,?)",[p1,p2])
    return p1

def event_id_create(x):
    p = sql("select event_id from ID_auto_create where task_id=?",[x])[0][0].split('.')
    p1 = str(int(p[1])+1)
    p = p[0] + '.' + p1
    sql("update ID_auto_create set event_id=? where task_id=?",[p,x])
    return p

def noti_id_auto_create():
    p = sql("select max(convert(int,noti_id)) from noti")[0][0]
    if p:
        p1 = str(int(p)+1)
    else:
        p1 = '1'
    return p1

def insert(x1,y1,x2,y2):
    # 2 insert 1
    event_1 = sql("select {} from event where event_id = ? and start_time = ?".format(','.join(event_field)),[x1,y1])[0]
    event_2 = sql("select {} from event where event_id = ? and start_time = ?".format(','.join(event_field)),[x2,y2])[0]
    if str_to_dt(event_1[event_field.index('start_time')]) < str_to_dt(event_2[event_field.index('start_time')]) < str_to_dt(event_1[event_field.index('end_time')]) < str_to_dt(event_2[event_field.index('end_time')]) :
        sql("update event set end_time = ? where event_id = ? and end_time = ?",[event_2[event_field.index('start_time')],x1,event_1[event_field.index('end_time')]])
    if str_to_dt(event_2[event_field.index('start_time')]) < str_to_dt(event_1[event_field.index('start_time')]) < str_to_dt(event_2[event_field.index('end_time')]) < str_to_dt(event_1[event_field.index('end_time')]) :
        sql("update event set start_time = ? where event_id = ? and start_time = ?",[event_2[event_field.index('end_time')],x1,event_1[event_field.index('start_time')]])
    if str_to_dt(event_1[event_field.index('start_time')]) <= str_to_dt(event_2[event_field.index('start_time')]) < str_to_dt(event_2[event_field.index('end_time')]) <= str_to_dt(event_1[event_field.index('end_time')]) and (str_to_dt(event_1[event_field.index('start_time')]) != str_to_dt(event_2[event_field.index('start_time')]) or str_to_dt(event_2[event_field.index('end_time')]) != str_to_dt(event_1[event_field.index('end_time')])):
        sql("delete from event where event_id = ? and start_time = ?",[x1,event_1[event_field.index('start_time')]])
        new_event_1 = list(event_1)
        new_event_2 = list(event_1)
        new_event_1[event_field.index('start_time')] = event_1[event_field.index('start_time')]
        new_event_1[event_field.index('end_time')] = event_2[event_field.index('start_time')]
        new_event_2[event_field.index('start_time')] = event_2[event_field.index('end_time')]
        new_event_2[event_field.index('end_time')] = event_1[event_field.index('end_time')]
        if str_to_dt(event_1[event_field.index('start_time')]) == str_to_dt(event_2[event_field.index('start_time')]) and str_to_dt(event_2[event_field.index('end_time')]) != str_to_dt(event_1[event_field.index('end_time')]):
            sql("insert into event values({})".format(','.join(['?']*len(event_field))),new_event_2)
        elif str_to_dt(event_1[event_field.index('start_time')]) != str_to_dt(event_2[event_field.index('start_time')]) and str_to_dt(event_2[event_field.index('end_time')]) == str_to_dt(event_1[event_field.index('end_time')]):
            sql("insert into event values({})".format(','.join(['?']*len(event_field))),new_event_1)
        else:
            sql("insert into event values({})".format(','.join(['?']*len(event_field))),new_event_1)
            sql("insert into event values({})".format(','.join(['?']*len(event_field))),new_event_2)
    if str_to_dt(event_2[event_field.index('start_time')]) <= str_to_dt(event_1[event_field.index('start_time')]) < str_to_dt(event_1[event_field.index('end_time')]) <= str_to_dt(event_2[event_field.index('end_time')]) :
        sql("delete from event where event_id = ? and start_time = ?",[x1,event_1[event_field.index('start_time')]])

def check_dup(x):
    event_x = sql("select {} from event where event_id = ?".format(','.join(event_field)),[x])
    all_event = sql("select {} from event where event_id != ? and executer = ?".format(','.join(event_field)),[x,event_x[0][event_field.index('executer')]])
    return [[r[event_field.index('event_id')],r[event_field.index('start_time')],r1[event_field.index('event_id')],r1[event_field.index('start_time')]] for r1 in all_event for r in event_x if (str_to_dt(r[event_field.index('start_time')]) < str_to_dt(r1[event_field.index('start_time')]) < str_to_dt(r[event_field.index('end_time')]) or str_to_dt(r[event_field.index('start_time')]) < str_to_dt(r1[event_field.index('end_time')]) < str_to_dt(r[event_field.index('end_time')]) or str_to_dt(r1[event_field.index('start_time')]) <= str_to_dt(r[event_field.index('start_time')]) <= str_to_dt(r[event_field.index('end_time')]) <= str_to_dt(r1[event_field.index('end_time')]))]

def check_trung_hang(x):
    for i,r in enumerate(x):
        if len(r) > 1:
            for j in xrange(len(r)-1):
                if str_to_dt(r[j][task_field.index('end_time')]) > str_to_dt(r[j+1][task_field.index('start_time')]):
                    return False
        else:
            pass
    return True

def tach_hang(x):
    ds_trung = []
    done = False
    finish = False
    for i,r in enumerate(x):
        if not done:
            finish = False
            while not finish:
                if len(r) > 1:
                    for j in xrange(len(r)-1):
                        if str_to_dt(r[j][task_field.index('end_time')]) > str_to_dt(r[j+1][task_field.index('start_time')]):
                            ds_trung.append(r[j+1])
                            r.pop(j+1)
                            break
                        if j + 1 == len(r) - 1:
                            finish = True
                else:
                    finish = True
                if ds_trung and finish:
                    x.insert(i+1,ds_trung)
                    done = True

def insert_test(x='p'):
    sql("insert into t1 values (?)",[x])

def get_data(x):
    # Get session and other var
    day_selected = session['day_selected']
    time_begin, time_finish, min_unit, work_hour = khung_gio()
    list_assignee = sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where n_0 like '%{}%'".format(session['username'])) + sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where n_1 like '%{}%'".format(session['username'])) + sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where n_2 like '%{}%'".format(session['username'])) + sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where username = ?",[session['username']])

    def condition(r,x):
        return condition_in(r[x.index('start_time')],r[x.index('end_time')],time_begin_default + ' ' + d_to_str(session['day_selected']),time_finish_default + ' ' + d_to_str(session['day_selected']))
    # Get all data and filter people
    all_task = [list(r) for r in sql("SELECT {} from task where assigner = ? and executer = ? and supporter != '' or assigner = ? and executer != ? order by convert(int,task_id)".format(','.join(task_field)),[x,x,x,x])]
    # Content and block
    content_task = [r for r in all_task if condition(r,task_field)]
    content_task.sort(key = lambda x : str_to_dt(x[task_field.index('start_time')]))
    content_task = [[r for r in content_task if r[task_field.index('executer')] == set_r] for set_r in set_keep_order([r[task_field.index('executer')] for r in content_task])]
    while not check_trung_hang(content_task):
        tach_hang(content_task)

    block_sub = []
    block_task = []
    for r in content_task:
        for r1 in r:
            index = dt_to_index(r1[task_field.index('start_time')],r1[task_field.index('end_time')],time_begin_default + ' ' + d_to_str(session['day_selected']),time_finish_default + ' ' + d_to_str(session['day_selected']))
            index = [index[0],index[1]+1]
            block_sub.append(index)
        block_task.append(block_sub)
        block_sub = []
        
    for i in range(len(content_task)):
        for j in range(len(content_task[i])):
            if content_task[i][j][7] != None:
                content_task[i][j].append(hash_user(content_task[i][j][7]))
    return [day_selected,content_task, block_task]

def get_cmt(x):
    cmt = [list(r) for r in sql("select * from cmt where task_id = ?",[x])]
    for r in cmt:
        r[cmt_field.index('time')] = str_to_dt(r[cmt_field.index('time')])
    cmt = sorted(cmt, key=itemgetter(cmt_field.index('time')))
    for r in cmt:
        r[cmt_field.index('time')] = dt_to_str(r[cmt_field.index('time')])
    return cmt

def layout(x):
    list_assignee = sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where (n_0 = ? or n_0 like '%|{}' or n_0 like '%|{}|%' or n_0 like '{}|%')".format(x,x,x),[x]) + sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where (n_1 = ? or n_1 like '%|{}' or n_1 like '%|{}|%' or n_1 like '{}|%')".format(x,x,x),[x]) + sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where (n_2 = ? or n_2 like '%|{}' or n_2 like '%|{}|%' or n_2 like '{}|%')".format(x,x,x),[x]) + sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where (n_3 = ? or n_3 like '%|{}' or n_3 like '%|{}|%' or n_3 like '{}|%')".format(x,x,x),[x])
    return list_assignee

ds_user = [r1[0] for r1 in sql("select username from profile")]
ds_user_mailname = [r1[0] for r1 in sql("select mail_name from profile")]
ds_phong = [r1[0] for r1 in sql("select distinct phong from profile")]
ds_phong_bophan = [r1[0] + '|' + r1[1] for r1 in sql("select distinct phong,bophan from profile where bophan != ''")]

def calculate(x,start_time,end_time):
    if x in ds_user_mailname:
        user_mail_name = x
        x = sql("select username from profile where mail_name = ?",[x])[0][0]
        #1 So gio lam viec
        if not start_time:
            start_time = start_date_demo
        if not end_time:
            end_time = dt.datetime.now()
        end_time = dt.datetime.combine(end_time.date(),dt.time(23,59,59))
        event_data = sql("select {} from event where executer = ?".format(','.join(event_field)),[x])
        event_data = [list(r) for r in event_data if str_to_dt(r[event_field.index('end_time')]) > start_time]
        event_data = [list(r) for r in event_data if str_to_dt(r[event_field.index('start_time')]) < end_time]

        so_nguoi_thuc_hien = 1

        for i,r in enumerate(event_data):
            if str_to_dt(r[event_field.index('start_time')]) <= start_time < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                print event_data[i][event_field.index('start_time')]
                event_data[i][event_field.index('start_time')] = dt_to_str(start_time)
            elif start_time <= str_to_dt(r[event_field.index('start_time')]) < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                pass
            elif start_time <= str_to_dt(r[event_field.index('start_time')]) < end_time <= str_to_dt(r[event_field.index('end_time')]):
                event_data[i][event_field.index('end_time')] = dt_to_str(end_time)
            else:
                pass
        
        so_gio_lam_viec_raw = sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),x) for r in event_data])
        so_gio_lam_viec = str(int(round(so_gio_lam_viec_raw/3600,0)))

        #2 So cong viec duoc giao va so cong viec di giao
        task_data = sql("select {} from task where executer = ? or (supporter = ? or supporter like '%|{}' or supporter like '%|{}|%' or supporter like '{}|%')".format(','.join(task_field),x,x,x),[x,x])
        task_data = [r for r in task_data if start_time <= str_to_dt(r[task_field.index('start_time')]) <= end_time]
        so_cong_viec = len(task_data)

        task_data_giao_viec = sql("select {} from task where assigner = ? and supporter != ?".format(','.join(task_field)),[x,x])
        task_data_giao_viec = [r for r in task_data_giao_viec if start_time <= str_to_dt(r[task_field.index('start_time')]) <= end_time]
        so_cong_viec_giao = len(task_data_giao_viec)

        #3,4 So cong viec theo 10 ngay gan nhat, 10 ngay gan nhat (dang string)
        try:
            ds_10_ngay_gan_nhat = [start_time + dt.timedelta(days=i) for i in range(int(str(end_time - start_time).split(" ")[0])+1)]
        except:
            ds_10_ngay_gan_nhat = [start_time]

        ds_10_ngay_gan_nhat = [r for r in ds_10_ngay_gan_nhat if r >= start_time and r.weekday() != 6 and r.date() not in list_ngay_nghi]
        ds_cong_viec_trong_10_ngay = [str(len([r for r in task_data if str_to_dt(r[task_field.index('start_time')]).date() == r1.date()])) for r1 in ds_10_ngay_gan_nhat]
        ds_10_ngay_gan_nhat = [str(r.date())[5:] for r in ds_10_ngay_gan_nhat]

        #5 So ngay lam viec
        try:
            ds_ngay_lam_viec = [start_time + dt.timedelta(days=i) for i in range(int(str(end_time - start_time).split(" ")[0])+1)]
        except:
            ds_ngay_lam_viec = [start_time]
        ds_ngay_lam_viec = [r for r in ds_ngay_lam_viec if r.weekday() != 6 and r.date() not in list_ngay_nghi]
        so_ngay_lam_viec = len([r for r in ds_ngay_lam_viec if r.weekday() == 5])/2 + len([r for r in ds_ngay_lam_viec if r.weekday() != 5])

        #6,7,8,9,10,11 Phan bo cong viec theo trung tam, theo cong ty, theo toan hang, ds cong viec theo trung tam, theo cong ty, theo toan hang
        try:
            department = sql("select phong from profile where username = ?",[x])[0][0]
        except:
            department = ['']*10
        ds_cv_theo_trung_tam = [r[0] for r in sql("select type_department from department where department = ?  order by type_department",[department])]

        ds_cv_theo_cong_ty = [u'Công tác hồ sơ giấy tờ', u'Công tác trình ký', u'Công việc nội bộ phục vụ thu nợ', u'Đánh giá hồ sơ', u'Đào tạo', u'Dự án chiên lược', u'Họp', u'Khảo sát khách hàng', u'Khảo sát TSĐB', u'Phối hợp XLN với các bên khác', u'Phối hợp XLN với các đơn vị nội bộ', u'Tác nghiệp', u'Văn hóa tổ chúc', u'Xây dựng phương án XLN/ Điều chỉnh phương án XLN',u'Khác']

        ds_cv_theo_toan_hang = [u'Cam kết hành động', u'Chiến lược', u'Công việc hàng ngày', u'Khách hàng là trên hết', u'Tính thần phối hợp', u'Văn hóa tổ chức', u'Xây dựng nguồn nhân lực']
        if so_gio_lam_viec_raw:
            phan_bo_cv_theo_trung_tam = [str(int(round(sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),x) for r in [r1 for r1 in event_data if r1[event_field.index("type_department")] == r2]])*100/so_gio_lam_viec_raw,2))) + '%' for r2 in ds_cv_theo_trung_tam]

            phan_bo_cv_theo_cong_ty = [str(int(round(sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),x) for r in [r1 for r1 in event_data if r1[event_field.index("type")] == r2]])*100/so_gio_lam_viec_raw,2))) + '%' for r2 in ds_cv_theo_cong_ty]

            phan_bo_cv_theo_toan_hang = [str(int(round(sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),x) for r in [r1 for r1 in event_data if r1[event_field.index("type_strategy")] == r2]])*100/so_gio_lam_viec_raw,2))) + '%' for r2 in ds_cv_theo_toan_hang]
        else:
            phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang = ['']*3

        #12 Ty le tuan thu bao cao
        tong_tg_lam_viec_quy_dinh = len([r for r in ds_ngay_lam_viec if r.weekday() not in (5,6) and r.date() not in list_ngay_nghi])*8 + len([r for r in ds_ngay_lam_viec if r.weekday() == 5])*4
        ty_le_tuan_thu_bao_cao = str(round(so_gio_lam_viec_raw/3600/tong_tg_lam_viec_quy_dinh*100,2))
        ty_le_tuan_thu_bao_cao_theo_user = [[user_mail_name,round(so_gio_lam_viec_raw/3600,2),tong_tg_lam_viec_quy_dinh,ty_le_tuan_thu_bao_cao]]

        #13 Ty le qua han
        if so_cong_viec:
            ty_le_hoan_thanh_dung_han = str(round(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] == '100%'])/so_cong_viec*100,2))
            ty_le_hoan_thanh_qua_han = str(round(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] == '100%'])/so_cong_viec*100,2))
            ty_le_chua_hoan_thanh_dung_han = str(round(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] != '100%'])/so_cong_viec*100,2))
            ty_le_chua_hoan_thanh_qua_han = str(round(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] != '100%'])/so_cong_viec*100,2))
            ty_le_qua_han = ty_le_hoan_thanh_dung_han + '|' + ty_le_hoan_thanh_qua_han + '|' + ty_le_chua_hoan_thanh_dung_han + '|' + ty_le_chua_hoan_thanh_qua_han
            so_cong_viec_qua_han = str(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] == '100%']))+ '|' + str(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] == '100%']))+ '|' + str(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] != '100%']))+ '|' + str(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] != '100%']))
        else:
            so_cong_viec_qua_han = ''
            ty_le_qua_han = ''

        if so_cong_viec_giao:
            ty_le_hoan_thanh_dung_han = str(round(len([r for r in task_data_giao_viec if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] == '100%'])/so_cong_viec_giao*100,2))
            ty_le_hoan_thanh_qua_han = str(round(len([r for r in task_data_giao_viec if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] == '100%'])/so_cong_viec_giao*100,2))
            ty_le_chua_hoan_thanh_dung_han = str(round(len([r for r in task_data_giao_viec if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] != '100%'])/so_cong_viec_giao*100,2))
            ty_le_chua_hoan_thanh_qua_han = str(round(len([r for r in task_data_giao_viec if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] != '100%'])/so_cong_viec_giao*100,2))
            ty_le_qua_han_giao_viec = ty_le_hoan_thanh_dung_han + '|' + ty_le_hoan_thanh_qua_han + '|' + ty_le_chua_hoan_thanh_dung_han +'|' + ty_le_chua_hoan_thanh_qua_han

            so_cong_viec_giao_qua_han = str(len([r for r in task_data_giao_viec if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] == '100%']))+'|'+str(len([r for r in task_data_giao_viec if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] == '100%']))+'|'+str(len([r for r in task_data_giao_viec if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] != '100%']))+'|'+str(len([r for r in task_data_giao_viec if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] != '100%']))
        else:
            ty_le_qua_han_giao_viec = ''
            so_cong_viec_giao_qua_han = ''

        ds_10_ngay_gan_nhat = '|'.join(ds_10_ngay_gan_nhat)
        ds_cong_viec_trong_10_ngay = '|'.join(ds_cong_viec_trong_10_ngay)
        phan_bo_cv_theo_trung_tam = '|'.join(phan_bo_cv_theo_trung_tam)
        phan_bo_cv_theo_cong_ty = '|'.join(phan_bo_cv_theo_cong_ty)
        phan_bo_cv_theo_toan_hang = '|'.join(phan_bo_cv_theo_toan_hang)
        ds_cv_theo_trung_tam = '|'.join(ds_cv_theo_trung_tam)
        ds_cv_theo_cong_ty = '|'.join(ds_cv_theo_cong_ty)
        ds_cv_theo_toan_hang = '|'.join(ds_cv_theo_toan_hang)
        return [so_gio_lam_viec,so_cong_viec,ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay,so_ngay_lam_viec,phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam,ds_cv_theo_cong_ty,ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao,ty_le_qua_han,ty_le_qua_han_giao_viec,so_cong_viec_qua_han,so_cong_viec_giao_qua_han,so_nguoi_thuc_hien,ty_le_tuan_thu_bao_cao_theo_user]
    elif x == 'AMC':
        if not start_time:
            start_time = start_date_demo
        if not end_time:
            end_time = dt.datetime.now()
        end_time = dt.datetime.combine(end_time.date(),dt.time(23,59,59))
        #1 So gio lam viec
        event_data = sql("select {} from event".format(','.join(event_field)))
        event_data = [list(r) for r in event_data if str_to_dt(r[event_field.index('end_time')]) > start_time]
        event_data = [list(r) for r in event_data if str_to_dt(r[event_field.index('start_time')]) < end_time]

        so_nguoi_thuc_hien = len(set([r[event_field.index('executer')] for r in event_data]))

        for i,r in enumerate(event_data):
            if str_to_dt(r[event_field.index('start_time')]) <= start_time < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                print event_data[i][event_field.index('start_time')]
                event_data[i][event_field.index('start_time')] = dt_to_str(start_time)
            elif start_time <= str_to_dt(r[event_field.index('start_time')]) < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                pass
            elif start_time <= str_to_dt(r[event_field.index('start_time')]) < end_time <= str_to_dt(r[event_field.index('end_time')]):
                event_data[i][event_field.index('end_time')] = dt_to_str(end_time)
            else:
                pass

        so_gio_lam_viec_raw = sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in event_data])
        so_gio_lam_viec = str(int(round(so_gio_lam_viec_raw/3600,0)))

        #2 So cong viec
        task_data = sql("select {} from task".format(','.join(task_field)))
        so_cong_viec = len(task_data)

        #3,4 So cong viec theo 10 ngay gan nhat, 10 ngay gan nhat (dang string)
        try:
            ds_10_ngay_gan_nhat = [start_time + dt.timedelta(days=i) for i in range(int(str(end_time - start_time).split(" ")[0])+1)]
        except:
            ds_10_ngay_gan_nhat = [start_time]

        ds_10_ngay_gan_nhat = [r for r in ds_10_ngay_gan_nhat if r >= start_time and r.weekday() != 6 and r.date() not in list_ngay_nghi]
        ds_cong_viec_trong_10_ngay = [str(len([r for r in task_data if str_to_dt(r[task_field.index('start_time')]).date() == r1.date()])) for r1 in ds_10_ngay_gan_nhat]
        ds_10_ngay_gan_nhat = [str(r.date())[5:] for r in ds_10_ngay_gan_nhat]

        #5 So ngay lam viec
        try:
            ds_ngay_lam_viec = [start_time + dt.timedelta(days=i) for i in range(int(str(end_time - start_time).split(" ")[0])+1)]
        except:
            ds_ngay_lam_viec = [start_time]
        ds_ngay_lam_viec = [r for r in ds_ngay_lam_viec if r.weekday() != 6 and r.date() not in list_ngay_nghi]
        so_ngay_lam_viec = len([r for r in ds_ngay_lam_viec if r.weekday() == 5])/2 + len([r for r in ds_ngay_lam_viec if r.weekday() != 5])

        #6,7,8,9,10,11 Phan bo cong viec theo trung tam, theo cong ty, theo toan hang, ds cong viec theo trung tam, theo cong ty, theo toan hang

        ds_cv_theo_trung_tam = ''
        ds_cv_theo_cong_ty = [u'Công tác hồ sơ giấy tờ', u'Công tác trình ký', u'Công việc nội bộ phục vụ thu nợ', u'Đánh giá hồ sơ', u'Đào tạo', u'Dự án chiên lược', u'Họp', u'Khảo sát khách hàng', u'Khảo sát TSĐB', u'Phối hợp XLN với các bên khác', u'Phối hợp XLN với các đơn vị nội bộ', u'Tác nghiệp', u'Văn hóa tổ chúc', u'Xây dựng phương án XLN/ Điều chỉnh phương án XLN',u'Khác']
        ds_cv_theo_toan_hang = [u'Cam kết hành động', u'Chiến lược', u'Công việc hàng ngày', u'Khách hàng là trên hết', u'Tính thần phối hợp', u'Văn hóa tổ chức', u'Xây dựng nguồn nhân lực']

        if so_gio_lam_viec_raw:
            phan_bo_cv_theo_trung_tam = ''

            phan_bo_cv_theo_cong_ty = [str(int(round(sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in [r1 for r1 in event_data if r1[event_field.index("type")] == r2]])*100/so_gio_lam_viec_raw,2))) + '%' for r2 in ds_cv_theo_cong_ty]

            phan_bo_cv_theo_toan_hang = [str(int(round(sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in [r1 for r1 in event_data if r1[event_field.index("type_strategy")] == r2]])*100/so_gio_lam_viec_raw,2))) + '%' for r2 in ds_cv_theo_toan_hang]
        else:
            phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang = ['']*3

        #12 Ty le tuan thu bao cao
        tong_tg_lam_viec_quy_dinh = len([r for r in ds_ngay_lam_viec if r.weekday() not in (5,6) and r.date() not in list_ngay_nghi])*8 + len([r for r in ds_ngay_lam_viec if r.weekday() == 5])*4
        ty_le_tuan_thu_bao_cao = str(round(so_gio_lam_viec_raw/so_nguoi_thuc_hien/3600/tong_tg_lam_viec_quy_dinh*100,2))

        ds_mailname_trong_amc = [r[0] for r in sql("select mail_name from profile order by username")]
        ds_user_active_amc = [r[0] for r in sql("select username from profile order by username")]
        ty_le_tuan_thu_bao_cao_theo_user = []
        for j,rx in enumerate(ds_user_active_amc):
            #1 So gio lam viec

            event_data_1 = sql("select {} from event where executer = ?".format(','.join(event_field)),[rx])
            event_data_1 = [list(r) for r in event_data_1 if str_to_dt(r[event_field.index('end_time')]) > start_time]
            event_data_1 = [list(r) for r in event_data_1 if str_to_dt(r[event_field.index('start_time')]) < end_time]


            for i,r in enumerate(event_data_1):
                if str_to_dt(r[event_field.index('start_time')]) <= start_time < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                    event_data_1[i][event_field.index('start_time')] = dt_to_str(start_time)
                elif start_time <= str_to_dt(r[event_field.index('start_time')]) < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                    pass
                elif start_time <= str_to_dt(r[event_field.index('start_time')]) < end_time <= str_to_dt(r[event_field.index('end_time')]):
                    event_data_1[i][event_field.index('end_time')] = dt_to_str(end_time)
                else:
                    pass
            
            so_gio_lam_viec_raw_1 = sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),rx) for r in event_data_1])
            so_gio_lam_viec_1 = str(int(round(so_gio_lam_viec_raw_1/3600,0)))

            #5 So ngay lam viec
            try:
                ds_ngay_lam_viec_1 = [start_time + dt.timedelta(days=i) for i in range(int(str(end_time - start_time).split(" ")[0])+1)]
            except:
                ds_ngay_lam_viec_1 = [start_time]
            ds_ngay_lam_viec_1 = [r for r in ds_ngay_lam_viec_1 if r.weekday() != 6 and r.date() not in list_ngay_nghi]
            so_ngay_lam_viec_1 = len(ds_ngay_lam_viec_1)

            #12 Ty le tuan thu bao cao
            tong_tg_lam_viec_quy_dinh_1 = len([r for r in ds_ngay_lam_viec_1 if r.weekday() not in (5,6) and r.date() not in list_ngay_nghi])*8 + len([r for r in ds_ngay_lam_viec_1 if r.weekday() == 5])*4
            ty_le_tuan_thu_bao_cao_1 = str(round(so_gio_lam_viec_raw_1/3600/tong_tg_lam_viec_quy_dinh_1*100,2))
            ty_le_tuan_thu_bao_cao_theo_user.append([ds_mailname_trong_amc[j],so_gio_lam_viec_raw_1/3600,tong_tg_lam_viec_quy_dinh_1,ty_le_tuan_thu_bao_cao_1])


        #13 Ty le qua han
        if so_cong_viec:
            ty_le_hoan_thanh_dung_han = str(round(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] == '100%'])/so_cong_viec*100,2))
            ty_le_hoan_thanh_qua_han = str(round(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] == '100%'])/so_cong_viec*100,2))
            ty_le_chua_hoan_thanh_dung_han = str(round(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] != '100%'])/so_cong_viec*100,2))
            ty_le_chua_hoan_thanh_qua_han = str(round(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] != '100%'])/so_cong_viec*100,2))
            ty_le_qua_han = ty_le_hoan_thanh_dung_han + '|' + ty_le_hoan_thanh_qua_han + '|' + ty_le_chua_hoan_thanh_dung_han + '|' + ty_le_chua_hoan_thanh_qua_han

            so_cong_viec_qua_han = str(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] == '100%']))+ '|' + str(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] == '100%']))+ '|' + str(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] != '100%']))+ '|' + str(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] != '100%']))
        else:
            so_cong_viec_qua_han = ''
            ty_le_qua_han = ''

        ds_10_ngay_gan_nhat = '|'.join(ds_10_ngay_gan_nhat)
        ds_cong_viec_trong_10_ngay = '|'.join(ds_cong_viec_trong_10_ngay)
        phan_bo_cv_theo_trung_tam = '|'.join(phan_bo_cv_theo_trung_tam)
        phan_bo_cv_theo_cong_ty = '|'.join(phan_bo_cv_theo_cong_ty)
        phan_bo_cv_theo_toan_hang = '|'.join(phan_bo_cv_theo_toan_hang)
        ds_cv_theo_trung_tam = '|'.join(ds_cv_theo_trung_tam)
        ds_cv_theo_cong_ty = '|'.join(ds_cv_theo_cong_ty)
        ds_cv_theo_toan_hang = '|'.join(ds_cv_theo_toan_hang)
        ty_le_qua_han_giao_viec = []
        so_cong_viec_giao_qua_han = []

        return [so_gio_lam_viec,so_cong_viec,ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay,so_ngay_lam_viec,phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam,ds_cv_theo_cong_ty,ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao,ty_le_qua_han,ty_le_qua_han_giao_viec,so_cong_viec_qua_han,so_cong_viec_giao_qua_han,so_nguoi_thuc_hien,ty_le_tuan_thu_bao_cao_theo_user]

    elif x in ds_phong:
        if not start_time:
            start_time = start_date_demo
        if not end_time:
            end_time = dt.datetime.now()
        end_time = dt.datetime.combine(end_time.date(),dt.time(23,59,59))
        ds_user_active = [r[0] for r in sql("select username from profile where phong = ?  order by username",[x])]
        #1 So gio lam viec
        event_data = sql("select {} from event where department = ?".format(','.join(event_field)),[x])
        event_data = [list(r) for r in event_data if str_to_dt(r[event_field.index('end_time')]) > start_time]
        event_data = [list(r) for r in event_data if str_to_dt(r[event_field.index('start_time')]) < end_time]

        so_nguoi_thuc_hien = len(set([r[event_field.index('executer')] for r in event_data]))

        for i,r in enumerate(event_data):
            if str_to_dt(r[event_field.index('start_time')]) <= start_time < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                print event_data[i][event_field.index('start_time')]
                event_data[i][event_field.index('start_time')] = dt_to_str(start_time)
            elif start_time <= str_to_dt(r[event_field.index('start_time')]) < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                pass
            elif start_time <= str_to_dt(r[event_field.index('start_time')]) < end_time <= str_to_dt(r[event_field.index('end_time')]):
                event_data[i][event_field.index('end_time')] = dt_to_str(end_time)
            else:
                pass

        so_gio_lam_viec_raw = sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in event_data])
        so_gio_lam_viec = str(int(round(so_gio_lam_viec_raw/3600,0)))

        #2 So cong viec
        task_data = sql("select {} from task where department = ?".format(','.join(task_field)),[x])
        so_cong_viec = len(task_data)

        #3,4 So cong viec theo 10 ngay gan nhat, 10 ngay gan nhat (dang string)
        try:
            ds_10_ngay_gan_nhat = [start_time + dt.timedelta(days=i) for i in range(int(str(end_time - start_time).split(" ")[0])+1)]
        except:
            ds_10_ngay_gan_nhat = [start_time]

        ds_10_ngay_gan_nhat = [r for r in ds_10_ngay_gan_nhat if r >= start_time and r.weekday() != 6 and r.date() not in list_ngay_nghi]
        ds_cong_viec_trong_10_ngay = [str(len([r for r in task_data if str_to_dt(r[task_field.index('start_time')]).date() == r1.date()])) for r1 in ds_10_ngay_gan_nhat]
        ds_10_ngay_gan_nhat = [str(r.date())[5:] for r in ds_10_ngay_gan_nhat]

        #5 So ngay lam viec
        try:
            ds_ngay_lam_viec = [start_time + dt.timedelta(days=i) for i in range(int(str(end_time - start_time).split(" ")[0])+1)]
        except:
            ds_ngay_lam_viec = [start_time]
        ds_ngay_lam_viec = [r for r in ds_ngay_lam_viec if r.weekday() != 6 and r.date() not in list_ngay_nghi]
        so_ngay_lam_viec = len([r for r in ds_ngay_lam_viec if r.weekday() == 5])/2 + len([r for r in ds_ngay_lam_viec if r.weekday() != 5])

        #6,7,8,9,10,11 Phan bo cong viec theo trung tam, theo cong ty, theo toan hang, ds cong viec theo trung tam, theo cong ty, theo toan hang
        ds_cv_theo_trung_tam = [r[0] for r in sql("select type_department from department where department = ?  order by type_department",[x])]

        ds_cv_theo_cong_ty = [u'Công tác hồ sơ giấy tờ', u'Công tác trình ký', u'Công việc nội bộ phục vụ thu nợ', u'Đánh giá hồ sơ', u'Đào tạo', u'Dự án chiên lược', u'Họp', u'Khảo sát khách hàng', u'Khảo sát TSĐB', u'Phối hợp XLN với các bên khác', u'Phối hợp XLN với các đơn vị nội bộ', u'Tác nghiệp', u'Văn hóa tổ chúc', u'Xây dựng phương án XLN/ Điều chỉnh phương án XLN',u'Khác']

        ds_cv_theo_toan_hang = [u'Cam kết hành động', u'Chiến lược', u'Công việc hàng ngày', u'Khách hàng là trên hết', u'Tính thần phối hợp', u'Văn hóa tổ chức', u'Xây dựng nguồn nhân lực']

        if so_gio_lam_viec_raw:
            phan_bo_cv_theo_trung_tam = [str(int(round(sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in [r1 for r1 in event_data if r1[event_field.index("type_department")] == r2]])*100/so_gio_lam_viec_raw,2))) + '%' for r2 in ds_cv_theo_trung_tam]


            phan_bo_cv_theo_cong_ty = [str(int(round(sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in [r1 for r1 in event_data if r1[event_field.index("type")] == r2]])*100/so_gio_lam_viec_raw,2))) + '%' for r2 in ds_cv_theo_cong_ty]

            phan_bo_cv_theo_toan_hang = [str(int(round(sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in [r1 for r1 in event_data if r1[event_field.index("type_strategy")] == r2]])*100/so_gio_lam_viec_raw,2))) + '%' for r2 in ds_cv_theo_toan_hang]
        else:
            phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang = ['']*3

        #12 Ty le tuan thu bao cao
        tong_tg_lam_viec_quy_dinh = len([r for r in ds_ngay_lam_viec if r.weekday() not in (5,6) and r.date() not in list_ngay_nghi])*8 + len([r for r in ds_ngay_lam_viec if r.weekday() == 5])*4
        ty_le_tuan_thu_bao_cao = str(round(so_gio_lam_viec_raw/so_nguoi_thuc_hien/3600/tong_tg_lam_viec_quy_dinh*100,2))

        ds_mailname_trong_phong = [r[0] for r in sql("select mail_name from profile where phong = ?  order by username",[x])]
        ty_le_tuan_thu_bao_cao_theo_user = []
        for j,rx in enumerate(ds_user_active):
            #1 So gio lam viec

            event_data_1 = sql("select {} from event where executer = ?".format(','.join(event_field)),[rx])
            event_data_1 = [list(r) for r in event_data_1 if str_to_dt(r[event_field.index('end_time')]) > start_time]
            event_data_1 = [list(r) for r in event_data_1 if str_to_dt(r[event_field.index('start_time')]) < end_time]


            for i,r in enumerate(event_data_1):
                if str_to_dt(r[event_field.index('start_time')]) <= start_time < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                    event_data_1[i][event_field.index('start_time')] = dt_to_str(start_time)
                elif start_time <= str_to_dt(r[event_field.index('start_time')]) < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                    pass
                elif start_time <= str_to_dt(r[event_field.index('start_time')]) < end_time <= str_to_dt(r[event_field.index('end_time')]):
                    event_data_1[i][event_field.index('end_time')] = dt_to_str(end_time)
                else:
                    pass
            
            so_gio_lam_viec_raw_1 = sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),rx) for r in event_data_1])
            so_gio_lam_viec_1 = str(int(round(so_gio_lam_viec_raw_1/3600,0)))

            #5 So ngay lam viec
            try:
                ds_ngay_lam_viec_1 = [start_time + dt.timedelta(days=i) for i in range(int(str(end_time - start_time).split(" ")[0])+1)]
            except:
                ds_ngay_lam_viec_1 = [start_time]
            ds_ngay_lam_viec_1 = [r for r in ds_ngay_lam_viec_1 if r.weekday() != 6 and r.date() not in list_ngay_nghi]
            so_ngay_lam_viec_1 = len(ds_ngay_lam_viec_1)

            #12 Ty le tuan thu bao cao
            tong_tg_lam_viec_quy_dinh_1 = len([r for r in ds_ngay_lam_viec_1 if r.weekday() not in (5,6) and r.date() not in list_ngay_nghi])*8 + len([r for r in ds_ngay_lam_viec_1 if r.weekday() == 5])*4
            ty_le_tuan_thu_bao_cao_1 = str(round(so_gio_lam_viec_raw_1/3600/tong_tg_lam_viec_quy_dinh_1*100,2))
            ty_le_tuan_thu_bao_cao_theo_user.append([ds_mailname_trong_phong[j],so_gio_lam_viec_raw_1/3600,tong_tg_lam_viec_quy_dinh_1,ty_le_tuan_thu_bao_cao_1])

        #13 Ty le qua han
        if so_cong_viec:
            ty_le_hoan_thanh_dung_han = str(round(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] == '100%'])/so_cong_viec*100,2))
            ty_le_hoan_thanh_qua_han = str(round(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] == '100%'])/so_cong_viec*100,2))
            ty_le_chua_hoan_thanh_dung_han = str(round(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] != '100%'])/so_cong_viec*100,2))
            ty_le_chua_hoan_thanh_qua_han = str(round(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] != '100%'])/so_cong_viec*100,2))
            ty_le_qua_han = ty_le_hoan_thanh_dung_han + '|' + ty_le_hoan_thanh_qua_han + '|' + ty_le_chua_hoan_thanh_dung_han + '|' + ty_le_chua_hoan_thanh_qua_han

            so_cong_viec_qua_han = str(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] == '100%']))+ '|' + str(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] == '100%']))+ '|' + str(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] != '100%']))+ '|' + str(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] != '100%']))
        else:
            so_cong_viec_qua_han = ''
            ty_le_qua_han = ''

        
        ds_10_ngay_gan_nhat = '|'.join(ds_10_ngay_gan_nhat)
        ds_cong_viec_trong_10_ngay = '|'.join(ds_cong_viec_trong_10_ngay)
        phan_bo_cv_theo_trung_tam = '|'.join(phan_bo_cv_theo_trung_tam)
        phan_bo_cv_theo_cong_ty = '|'.join(phan_bo_cv_theo_cong_ty)
        phan_bo_cv_theo_toan_hang = '|'.join(phan_bo_cv_theo_toan_hang)
        ds_cv_theo_trung_tam = '|'.join(ds_cv_theo_trung_tam)
        ds_cv_theo_cong_ty = '|'.join(ds_cv_theo_cong_ty)
        ds_cv_theo_toan_hang = '|'.join(ds_cv_theo_toan_hang)
        ty_le_qua_han_giao_viec = []
        so_cong_viec_giao_qua_han = []
        
        return [so_gio_lam_viec,so_cong_viec,ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay,so_ngay_lam_viec,phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam,ds_cv_theo_cong_ty,ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao,ty_le_qua_han,ty_le_qua_han_giao_viec,so_cong_viec_qua_han,so_cong_viec_giao_qua_han,so_nguoi_thuc_hien,ty_le_tuan_thu_bao_cao_theo_user]

    elif x in ds_phong_bophan:
        if not start_time:
            start_time = start_date_demo
        if not end_time:
            end_time = dt.datetime.now()
        end_time = dt.datetime.combine(end_time.date(),dt.time(23,59,59))
        ds_user_trg_bo_phan = [r[0] for r in sql("select username from profile where phong = ? and bophan = ? order by username",[x.split('|')[0],x.split('|')[1]])]
        #1 So gio lam viec
        event_data = sql("select {} from event where executer in ({})".format(','.join(event_field),','.join(["'" + r + "'" for r in ds_user_trg_bo_phan])))
        event_data = [list(r) for r in event_data if str_to_dt(r[event_field.index('end_time')]) > start_time]
        event_data = [list(r) for r in event_data if str_to_dt(r[event_field.index('start_time')]) < end_time]

        so_nguoi_thuc_hien = len(set([r[event_field.index('executer')] for r in event_data]))

        for i,r in enumerate(event_data):
            if str_to_dt(r[event_field.index('start_time')]) <= start_time < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                print event_data[i][event_field.index('start_time')]
                event_data[i][event_field.index('start_time')] = dt_to_str(start_time)
            elif start_time <= str_to_dt(r[event_field.index('start_time')]) < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                pass
            elif start_time <= str_to_dt(r[event_field.index('start_time')]) < end_time <= str_to_dt(r[event_field.index('end_time')]):
                event_data[i][event_field.index('end_time')] = dt_to_str(end_time)
            else:
                pass

        so_gio_lam_viec_raw = sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in event_data])
        so_gio_lam_viec = str(int(round(so_gio_lam_viec_raw/3600,0)))

        #2 So cong viec
        task_data = sql("select {} from task where executer in ({})".format(','.join(task_field),','.join(["'" + r + "'" for r in ds_user_trg_bo_phan])))
        so_cong_viec = len(task_data)

        #3,4 So cong viec theo 10 ngay gan nhat, 10 ngay gan nhat (dang string)
        try:
            ds_10_ngay_gan_nhat = [start_time + dt.timedelta(days=i) for i in range(int(str(end_time - start_time).split(" ")[0])+1)]
        except:
            ds_10_ngay_gan_nhat = [start_time]

        ds_10_ngay_gan_nhat = [r for r in ds_10_ngay_gan_nhat if r >= start_time and r.weekday() != 6 and r.date() not in list_ngay_nghi]
        ds_cong_viec_trong_10_ngay = [str(len([r for r in task_data if str_to_dt(r[task_field.index('start_time')]).date() == r1.date()])) for r1 in ds_10_ngay_gan_nhat]
        ds_10_ngay_gan_nhat = [str(r.date())[5:] for r in ds_10_ngay_gan_nhat]

        #5 So ngay lam viec
        try:
            ds_ngay_lam_viec = [start_time + dt.timedelta(days=i) for i in range(int(str(end_time - start_time).split(" ")[0])+1)]
        except:
            ds_ngay_lam_viec = [start_time]
        ds_ngay_lam_viec = [r for r in ds_ngay_lam_viec if r.weekday() != 6 and r.date() not in list_ngay_nghi]
        so_ngay_lam_viec = len([r for r in ds_ngay_lam_viec if r.weekday() == 5])/2 + len([r for r in ds_ngay_lam_viec if r.weekday() != 5])

        #6,7,8,9,10,11 Phan bo cong viec theo trung tam, theo cong ty, theo toan hang, ds cong viec theo trung tam, theo cong ty, theo toan hang
        ds_cv_theo_trung_tam = [r[0] for r in sql("select type_department from department where department = ?  order by type_department",[x.split('|')[0]])]

        ds_cv_theo_cong_ty = [u'Công tác hồ sơ giấy tờ', u'Công tác trình ký', u'Công việc nội bộ phục vụ thu nợ', u'Đánh giá hồ sơ', u'Đào tạo', u'Dự án chiên lược', u'Họp', u'Khảo sát khách hàng', u'Khảo sát TSĐB', u'Phối hợp XLN với các bên khác', u'Phối hợp XLN với các đơn vị nội bộ', u'Tác nghiệp', u'Văn hóa tổ chúc', u'Xây dựng phương án XLN/ Điều chỉnh phương án XLN',u'Khác']

        ds_cv_theo_toan_hang = [u'Cam kết hành động', u'Chiến lược', u'Công việc hàng ngày', u'Khách hàng là trên hết', u'Tính thần phối hợp', u'Văn hóa tổ chức', u'Xây dựng nguồn nhân lực']

        if so_gio_lam_viec_raw:
            phan_bo_cv_theo_trung_tam = [str(int(round(sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in [r1 for r1 in event_data if r1[event_field.index("type_department")] == r2]])*100/so_gio_lam_viec_raw,2))) + '%' for r2 in ds_cv_theo_trung_tam]

            phan_bo_cv_theo_cong_ty = [str(int(round(sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in [r1 for r1 in event_data if r1[event_field.index("type")] == r2]])*100/so_gio_lam_viec_raw,2))) + '%' for r2 in ds_cv_theo_cong_ty]

            phan_bo_cv_theo_toan_hang = [str(int(round(sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in [r1 for r1 in event_data if r1[event_field.index("type_strategy")] == r2]])*100/so_gio_lam_viec_raw,2))) + '%' for r2 in ds_cv_theo_toan_hang]
        else:
            phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang = ['']*3

        #12 Ty le tuan thu bao cao
        tong_tg_lam_viec_quy_dinh = len([r for r in ds_ngay_lam_viec if r.weekday() not in (5,6) and r.date() not in list_ngay_nghi])*8 + len([r for r in ds_ngay_lam_viec if r.weekday() == 5])*4
        ty_le_tuan_thu_bao_cao = str(round(so_gio_lam_viec_raw/so_nguoi_thuc_hien/3600/tong_tg_lam_viec_quy_dinh*100,2))

        ds_mailname_trong_phong_bophan = [r[0] for r in sql("select mail_name from profile where phong = ? and bophan = ?  order by username",[x.split('|')[0],x.split('|')[1]])]
        ty_le_tuan_thu_bao_cao_theo_user = []
        for j,rx in enumerate(ds_user_trg_bo_phan):
            #1 So gio lam viec

            event_data_1 = sql("select {} from event where executer = ?".format(','.join(event_field)),[rx])
            event_data_1 = [list(r) for r in event_data_1 if str_to_dt(r[event_field.index('end_time')]) > start_time]
            event_data_1 = [list(r) for r in event_data_1 if str_to_dt(r[event_field.index('start_time')]) < end_time]


            for i,r in enumerate(event_data_1):
                if str_to_dt(r[event_field.index('start_time')]) <= start_time < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                    event_data_1[i][event_field.index('start_time')] = dt_to_str(start_time)
                elif start_time <= str_to_dt(r[event_field.index('start_time')]) < str_to_dt(r[event_field.index('end_time')]) <= end_time:
                    pass
                elif start_time <= str_to_dt(r[event_field.index('start_time')]) < end_time <= str_to_dt(r[event_field.index('end_time')]):
                    event_data_1[i][event_field.index('end_time')] = dt_to_str(end_time)
                else:
                    pass
            
            so_gio_lam_viec_raw_1 = sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),rx) for r in event_data_1])
            so_gio_lam_viec_1 = str(int(round(so_gio_lam_viec_raw_1/3600,0)))

            #5 So ngay lam viec
            try:
                ds_ngay_lam_viec_1 = [start_time + dt.timedelta(days=i) for i in range(int(str(end_time - start_time).split(" ")[0])+1)]
            except:
                ds_ngay_lam_viec_1 = [start_time]
            ds_ngay_lam_viec_1 = [r for r in ds_ngay_lam_viec_1 if r.weekday() != 6 and r.date() not in list_ngay_nghi]
            so_ngay_lam_viec_1 = len(ds_ngay_lam_viec_1)

            #12 Ty le tuan thu bao cao
            tong_tg_lam_viec_quy_dinh_1 = len([r for r in ds_ngay_lam_viec_1 if r.weekday() not in (5,6) and r.date() not in list_ngay_nghi])*8 + len([r for r in ds_ngay_lam_viec_1 if r.weekday() == 5])*4
            ty_le_tuan_thu_bao_cao_1 = str(round(so_gio_lam_viec_raw_1/3600/tong_tg_lam_viec_quy_dinh_1*100,2))
            ty_le_tuan_thu_bao_cao_theo_user.append([ds_mailname_trong_phong_bophan[j],round(so_gio_lam_viec_raw_1/3600,2),tong_tg_lam_viec_quy_dinh_1,ty_le_tuan_thu_bao_cao_1])

        #13 Ty le qua han
        if so_cong_viec:
            hoan_thanh_dung_han = str(round(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] == '100%'])/so_cong_viec*100,2))
            hoan_thanh_qua_han = str(round(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] == '100%'])/so_cong_viec*100,2))
            dang_thuc_hien_dung_han = str(round(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] != '100%'])/so_cong_viec*100,2))
            dang_thuc_hien_qua_han = str(100 - float(hoan_thanh_dung_han) - float(hoan_thanh_qua_han) - float(dang_thuc_hien_dung_han))

            ty_le_qua_han = hoan_thanh_dung_han + '|' + hoan_thanh_qua_han + '|' + dang_thuc_hien_dung_han + '|' + dang_thuc_hien_qua_han

            so_cong_viec_qua_han = str(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] == '100%']))+ '|' + str(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] == '100%']))+ '|' + str(len([r for r in task_data if r[task_field.index("status")] != 'Y' and r[task_field.index("percentage")] != '100%']))+ '|' + str(len([r for r in task_data if r[task_field.index("status")] == 'Y' and r[task_field.index("percentage")] != '100%']))
        else:
            so_cong_viec_qua_han = ''
            ty_le_qua_han = ''

        ds_10_ngay_gan_nhat = '|'.join(ds_10_ngay_gan_nhat)
        ds_cong_viec_trong_10_ngay = '|'.join(ds_cong_viec_trong_10_ngay)
        phan_bo_cv_theo_trung_tam = '|'.join(phan_bo_cv_theo_trung_tam)
        phan_bo_cv_theo_cong_ty = '|'.join(phan_bo_cv_theo_cong_ty)
        phan_bo_cv_theo_toan_hang = '|'.join(phan_bo_cv_theo_toan_hang)
        ds_cv_theo_trung_tam = '|'.join(ds_cv_theo_trung_tam)
        ds_cv_theo_cong_ty = '|'.join(ds_cv_theo_cong_ty)
        ds_cv_theo_toan_hang = '|'.join(ds_cv_theo_toan_hang)
        ty_le_qua_han_giao_viec = []
        so_cong_viec_giao_qua_han = []
        
        return [so_gio_lam_viec,so_cong_viec,ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay,so_ngay_lam_viec,phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam,ds_cv_theo_cong_ty,ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao,ty_le_qua_han,ty_le_qua_han_giao_viec,so_cong_viec_qua_han,so_cong_viec_giao_qua_han,so_nguoi_thuc_hien,ty_le_tuan_thu_bao_cao_theo_user]



app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=900)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:   
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

def viewtask_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'task_id' in session:    
            return f(*args, **kwargs)
        else:
            return redirect(url_for('nam'))
    return wrap

def station_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'type_view' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('station'))
    return wrap
##
def get_mac(ip):
    if ip == '10.62.24.79':
        return '70-4d-7b-89-c7-ea'
    mac_sample = "2c-4d-54-47-7f-91"
    p1 = subprocess.Popen(['arp', '-a', ip], stdout=subprocess.PIPE)
    mac = p1.communicate()[0][-len('2c-4d-54-47-7f-91          dynamic'):-len(mac_sample)]
    return mac
#################################################

@app.route('/_check_mac', methods=['GET', 'POST'])
def check_mac():
    if 'sign_out' in session:
        ds_user_mac = sql("select top 6 username,mail_name,email,full_name,ten_viet_tat,so_luong from mac_profile where mac = ? order by so_luong desc",[get_mac(request.environ['REMOTE_ADDR'])])
        session['ds_user_mac'] = [[r[0],r[1],r[2],r[3],r[4]] for r in ds_user_mac]
        session.pop('sign_out', None)
        return redirect(url_for('login'))

    # Lấy thông tin IP và MAC đang truy cập
    session['ip'] = request.environ['REMOTE_ADDR']
    # Lấy danh sách các user đã đăng nhập trên MAC này
    ds_user_mac = sql("select top 6 username,mail_name,email,full_name,ten_viet_tat,so_luong from mac_profile where ip = ? order by so_luong desc",[session['ip']])
    # Engine phân luồng
        # Nếu (chỉ có 1 user) hoặc (có nhiều user nhưng user nhiều nhất nhiều hơn gấp đôi user thứ 2) thì user nhiều nhất đi thẳng
        # Trong các trường hợp còn lại, show ra tất cả các user đã đăng nhập theo thứ tự nhiều đến ít
    if len(ds_user_mac) == 1:
        session['logged_in'] = True
        session['username'] = (ds_user_mac[0][0]).lower()
        so_lan_dang_nhap = ds_user_mac[0][-1] + 1
        sql("update mac_profile set so_luong = ? where ip = ? and username = ?",[so_lan_dang_nhap,session['ip'],session['username']])
        return redirect(url_for('welcome_back'))
    elif len(ds_user_mac) > 1:
        he_so_limit = 0.5
        so_luong_limit = int(ds_user_mac[0][-1])*he_so_limit
        ds_user_limit = [[r[0],r[1],r[2],r[3],r[4]] for r in ds_user_mac if r[-1] > so_luong_limit]
        if len(ds_user_limit) == 1:
            session['logged_in'] = True
            session['username'] = (ds_user_limit[0][0]).lower()
            so_lan_dang_nhap = ds_user_mac[0][-1] + 1
            sql("update mac_profile set so_luong = ? where ip = ? and username = ?",[so_lan_dang_nhap,session['ip'],session['username']])
            return redirect(url_for('welcome_back'))
        else:
            session['ds_user_mac'] = [[r[0],r[1],r[2],r[3],r[4]] for r in ds_user_mac]
            return redirect(url_for('login'))
    else:
        session['ds_user_mac'] = []
        return redirect(url_for('login'))

#################################################
@app.route('/welcome_back', methods=['GET', 'POST'])
def welcome_back():
    new_mail_name = sql("select mail_name from profile where username = ?",[session['username']])[0][0]
    new_mail_name = ' '.join([r.capitalize() for r in new_mail_name.split(' ')]).replace('Qtrr','QTRR')
    new_email = session['username'] + '@techcombank.com.vn'
    new_full_name = sql("select hoten from profile where username = ?",[session['username']])[0][0]
    new_ten_viet_tat = new_mail_name.strip().split(' ')[-1][0] + new_mail_name.strip().split(' ')[0][0]
    
    user_info = [new_mail_name, new_email, new_full_name, new_ten_viet_tat]
    if request.form.get('redirect_station'):
        return redirect(url_for('station'))
    return render_template('welcome_back.html',user_info = user_info)

#################################################
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if 'ds_user_mac' not in session:
    #     return redirect(url_for('check_mac'))

    ds_user_mac = ''
    ds_all_user = sql("select username,mail_name,mail,hoten from profile order by username")
    return render_template('login.html',ds_user_mac = ds_user_mac,ds_all_user = ds_all_user)


##
#################################################
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    send_pass(request.args['forgot_password'])
    result = u"Mật khẩu mới đã được gửi về email của anh/chị. Nếu không nhận được mật khẩu, thử lại sau 1 phút"
    return jsonify({'result':result})
#################################################
@app.route('/authentication', methods=['GET', 'POST'])
def authentication():
    username = request.args['username']
    password = hash_user(request.args['password'])
    if request.environ['REMOTE_ADDR'] in ['10.62.24.161']:
        session['logged_in'] = True
        session['username'] = username.lower()
        result = u"authenticated"
        return jsonify({'result':result})
    if not sql("select * from Userr where username=? and password=?",[username,password]):
        result = u"Mật khẩu sai. Hãy thử lại."
        return jsonify({'result':result})   
    else:
        session['logged_in'] = True
        session['username'] = username.lower()

        # Check xem user đã đăng nhập trên MAC này lần nào chưa? Nếu rồi thì updata số lần đăng nhập, nếu chưa thì insert dòng dữ liệu mới.
        # check_user_on_mac = sql("select mac,username,so_luong from mac_profile where ip = ? and username = ?",[session['ip'],session['username']])

        # if check_user_on_mac:
        #     so_luong = check_user_on_mac[0][2] + 1
        #     sql("update mac_profile set so_luong = ? where ip = ? and username = ?",[so_luong,session['ip'],session['username']])
        # else:
        #     new_mail_name = sql("select mail_name from profile where username = ?",[session['username']])[0][0]
        #     new_mail_name = ' '.join([r.capitalize() for r in new_mail_name.split(' ')]).replace('Qtrr','QTRR')
        #     new_email = session['username'] + '@techcombank.com.vn'
        #     new_full_name = sql("select hoten from profile where username = ?",[session['username']])[0][0]
        #     new_ten_viet_tat = new_mail_name.strip().split(' ')[-1][0] + new_mail_name.strip().split(' ')[0][0]
        #     sql("insert into mac_profile values(?,?,?,?,?,?,?,?)",[session['ip'],session['username'],1,session['ip'],new_mail_name, new_email, new_full_name,new_ten_viet_tat])
        result = u"authenticated"
        return jsonify({'result':result})
@app.route('/logout')
@login_required
def logout():
    session['sign_out'] = ''
    session.pop('logged_in', None)
    session.pop('executer', None)
    session.pop('start_time', None)
    return redirect(url_for('login'))

@app.route('/_station')
def station():
    session['department'],session['mail_name'] = sql("select phong,mail_name from profile where username = ?",[session['username']])[0]
    session['day_selected'] = dt.datetime.now()
    session['type_department'] = sql("select type_department, type, type_strategy from department where department = ?",[session['department']])
    return redirect(url_for('intro'))

@app.route('/viewtask',methods=['GET', 'POST'])
@login_required
@viewtask_required
def viewtask():
    # Get data
    list_assignee = layout(session['username'])
    task_content = sql("select * from task where task_id = ?",[session['task_id']])[0]
    event_content = [list(r) for r in sql("select * from event where task_id = ?",[session['task_id']])]
    event_content.sort(key = lambda x : int(x[1].split('.')[-1]))
    list_people_cmt = task_content[task_field.index('executer')] + task_content[task_field.index('assigner')] + task_content[task_field.index('supporter')]
    user_cmt = sql("select user_cmt from noti where session = ?",[session['task_id']])
    cmt = get_cmt(session['task_id'])
    for i in user_cmt:
        if i[0] not in list_people_cmt:
            list_people_cmt.append(i[0])
    day_now = dt.datetime.now()
    
    if request.form.get('submit_comment'):
        sql("insert into cmt values({})".format(','.join(['?']*len(cmt_field))),[session['task_id'],session['mail_name'],request.form.get('comment'),dt_to_str(dt.datetime.now())])
        for i in list_people_cmt:
            if i != session['username']:
                sql("insert into noti values({})".format(','.join(['?']*len(noti_field))),[i,u'{} đã thảo luận về một công việc'.format(session['mail_name']),dt_to_str(dt.datetime.now()),'viewtask',session['task_id'],'N','N',session['username'],noti_id_auto_create()])
        return redirect(url_for('viewtask'))

    if request.form.get('comment'):
        sql("insert into cmt values({})".format(','.join(['?']*len(cmt_field))),[session['task_id'],session['mail_name'],request.form.get('comment'),dt_to_str(dt.datetime.now())])
        for i in list_people_cmt:
            if i != session['username']:
                sql("insert into noti values({})".format(','.join(['?']*len(noti_field))),[i,u'{} đã thảo luận về một công việc'.format(session['mail_name']),dt_to_str(dt.datetime.now()),'viewtask',session['task_id'],'N','N',session['username'],noti_id_auto_create()])
        return redirect(url_for('viewtask'))

    if request.form.get('go_to_date'):
        session['day_selected'] = dt.datetime.strptime(request.form.get('go_to_date'),'%d/%m/%Y')
        return redirect(url_for('nam'))

    if request.form.get('btn_noti_content'):
        i_noti = request.form.get('btn_noti_content')
        if request.form.get('redirect_noti_' + i_noti) == 'viewtask':
            session['task_id'] = request.form.get('input_noti_' + i_noti)
        if request.form.get('redirect_noti_' + i_noti) == 'nam':
            session['day_selected'] = str_to_dt(request.form.get('input_noti_' + i_noti).split('|')[0])
            session['task_id'] = request.form.get('input_noti_' + i_noti).split('|')[1]
        sql("update noti set read_real = 'Y' where noti_id = ?",[request.form.get('noti_id_' + i_noti)])
        return redirect(url_for(request.form.get('redirect_noti_' + i_noti) ))

    if len(event_content) == 0:
        assessment_1 = u'Chưa có báo cáo cho công việc này'
    else:
        assessment_1 = u'Có {} báo cáo cho công việc này'.format(len(event_content))

    if str_to_dt(task_content[task_field.index('end_time')]) < dt.datetime.now():
        assessment_2 = u'Đã quá hạn {} ngày đối với công việc này'.format(round((dt.datetime.now() -  str_to_dt(task_content[task_field.index('end_time')])).total_seconds()/(24*3600),2))
    else:
        assessment_2 = u'Còn lại {} ngày đối với công việc này'.format(round((str_to_dt(task_content[task_field.index('end_time')]) - dt.datetime.now()).total_seconds()/(24*3600),2))

    if task_content[task_field.index('executer')] == task_content[task_field.index('assigner')] :
        assessment_2 = assessment_1
        assessment_1 = u'Đây là công việc do {} tự thực hiện'.format(task_content[task_field.index('executer_name')])

    if request.form.get('go_task'):
        session['day_selected'] = str_to_dt(request.form.get('go_task'))
        return redirect(url_for('nam'))
       
    return render_template('task/viewtask.html',task_content=task_content,event_content = event_content,cmt=cmt,list_people_cmt=list_people_cmt,assessment_1=assessment_1,assessment_2=assessment_2,day_now=day_now,)

@app.route('/myjob',methods=['GET', 'POST'])
@login_required
def nam():
    # Prepare    
    ds_gio = ['07:00', '07:15', '07:30', '07:45', '08:00', '08:15', '08:30', '08:45', '09:00', '09:15', '09:30', '09:45', '10:00', '10:15', '10:30', '10:45', '11:00', '11:15', '11:30', '11:45', '12:00', '12:15', '12:30', '12:45', '13:00', '13:15', '13:30', '13:45', '14:00', '14:15', '14:30', '14:45', '15:00', '15:15', '15:30', '15:45', '16:00', '16:15', '16:30', '16:45', '17:00', '17:15', '17:30', '17:45', '18:00', '18:15', '18:30', '18:45', '19:00', '19:15', '19:30', '19:45', '20:00', '20:15', '20:30', '20:45', '21:00']
    ds_index = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 52, 55, 58, 61, 64, 67, 70, 73, 76, 79, 82, 85, 88, 91, 94, 97, 100, 103, 106, 109, 112, 115, 118, 121, 124, 127, 130, 133, 136, 139, 142, 145, 148, 151, 154, 157, 160, 163, 166, 169]
    list_moc_thoi_gian = ['07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']
    content_floor = sql("select {} from task where assigner != ? and (executer = ? or (supporter = ? or supporter like ? or supporter like ? or supporter like ?)) and start_time like '%'+?+'%'".format(','.join(task_field)),[session['username'],session['username'],session['username'],session['username'] + '|%','%|' + session['username'] + '|%','%|' + session['username'],d_to_str(session['day_selected'])])


    content_base = sql("select * from event where executer = ? and start_time like {}".format("'%"+d_to_str(session['day_selected'])+"'"),[session['username']])
    block_base = [[ds_index[ds_gio.index(r[event_field.index('start_time')][:5])],ds_index[ds_gio.index(r[event_field.index('end_time')][:5])]] for r in content_base]
    block_floor = [[ds_index[ds_gio.index(r[task_field.index('start_time')][:5])],ds_index[ds_gio.index(r[task_field.index('end_time')][:5])]] for r in content_floor]
    old_task = sql("select task_id, name, percentage from task where executer = ? and percentage != '100%'",[session['username']])

    day_selected = session['day_selected']
    day_now = dt.datetime.now()
    list_type_department = [r[0] for r in session['type_department']]
    if not content_base:
        content_base = []
        block_base = []
    else:
        content_base = [content_base]
        block_base = [block_base]
    if not content_floor:
        content_floor = []
        block_floor = []
    else:
        content_floor = [content_floor]
        block_floor = [block_floor]

    if request.form.get('tracking'):
        session['task_id'] = request.form.get('tracking')
        return redirect(url_for('viewtask'))

    if request.form.get('btn_noti_content'):
        i_noti = request.form.get('btn_noti_content')
        if request.form.get('redirect_noti_' + i_noti) == 'viewtask':
            session['task_id'] = request.form.get('input_noti_' + i_noti)
        if request.form.get('redirect_noti_' + i_noti) == 'nam':
            session['day_selected'] = str_to_dt(request.form.get('input_noti_' + i_noti).split('|')[0])
            session['task_id'] = request.form.get('input_noti_' + i_noti).split('|')[1]
        sql("update noti set read_real = 'Y' where noti_id = ?",[request.form.get('noti_id_' + i_noti)])
        return redirect(url_for(request.form.get('redirect_noti_' + i_noti) ))

    if request.form.get('select_day'):
        session['day_selected'] = dt.datetime.strptime(request.form.get('select_day'),'%d/%m/%Y')
        return redirect(url_for('nam'))

    return render_template('adminday/nam.html',block_base = block_base, content_base = content_base, day_selected = day_selected, old_task = old_task,day_now = day_now, list_type_department=list_type_department,list_moc_thoi_gian = list_moc_thoi_gian,content_floor=content_floor,block_floor=block_floor)


##
#################################################
@app.route('/ajax_add_new_task', methods=['POST'])
def ajax_add_new_task():
    block_base = ast.literal_eval(request.form['block_base'])
    content_base = ast.literal_eval(request.form['content_base'])

    new_id = task_id_create()
    name = request.form['Task_name_rp']
    type_department = request.form['type_department']
    job_type = [r[1] for r in session['type_department'] if r[0] == type_department][0]
    type_strategy = [r[2] for r in session['type_department'] if r[0] == type_department][0]
    content = request.form['Description_rp']
    status = 'In progress'
    percentage = request.form['Percentage']
    border_color = '#901e1d'
    executer = assigner = session['username']
    executer_name = assigner_name = session['mail_name']

    start = index_to_time(request.form['time_start'])
    last_update = end = index_to_time(request.form['time_end'])

    rating = ''
    complete = percentage
    supporter,supporter_name, customer, disable = ['']*4
    # Insert task
    sql("insert into task({}) values({})".format(','.join(task_field),','.join(['?']*len(task_field))),[new_id, name,job_type,type_strategy, content, status, percentage, executer, assigner,supporter, executer_name, assigner_name,supporter_name, customer, disable, start,end,last_update,rating,session['department'],type_department,border_color])
    # Insert event
    event_id = event_id_create(new_id)
    sql("insert into event({}) values({})".format(','.join(event_field),','.join(['?']*len(event_field))),[new_id, event_id, name,job_type,type_strategy, content, status, percentage, executer, assigner,supporter, executer_name, assigner_name,supporter_name, customer, disable, start,end,complete,session['department'],type_department,border_color])
    # Insert event_log
    sql("insert into event_log values(?,?,?,?,?,?)",[new_id,event_id,'B',session['username'],dt_to_str(dt.datetime.now()),'new task'])

    # Update block_base, content_base, old_task
    if block_base:
        block_base = [block_base[0] + [[(int(request.form['time_start'])-1)*3+1, (int(request.form['time_end'])-1)*3+1]]]
        content_base = [content_base[0] + [[new_id, event_id, name,job_type,type_strategy, content, status, percentage, executer, assigner,supporter, executer_name, assigner_name,supporter_name, customer, disable, start,end,complete,session['department'],type_department,border_color]]]
    else:
        block_base = [[[(int(request.form['time_start'])-1)*3+1, (int(request.form['time_end'])-1)*3+1]]]
        content_base = [[[new_id, event_id, name,job_type,type_strategy, content, status, percentage, executer, assigner,supporter, executer_name, assigner_name,supporter_name, customer, disable, start,end,complete,session['department'],type_department,border_color]]]

    # Other var
    old_task = sql("select task_id, name, percentage from task where executer = ? and percentage != '100%'",[session['username']])
    list_type_department = [r[0] for r in session['type_department']]

    return jsonify({'data': render_template('adminday/job_render.html',block_base=block_base,content_base=content_base,list_type_department=list_type_department,old_task = old_task),'data_2':render_template('adminday/old_task_render.html',old_task=old_task,list_type_department=list_type_department)})

#################################################
@app.route('/ajax_del_event', methods=['POST'])
def ajax_del_event():
    block_base = ast.literal_eval(request.form['block_base'])
    content_base = ast.literal_eval(request.form['content_base'])

    sql("delete from event where event_id = ? ",[request.form['delete_event']])
    # Update Task and Event
    if sql("select event_id, percentage from event where task_id = ?",[request.form['delete_event'].split('.')[0]]):
        list_event = [int(r[0].split('.')[1]) for r in sql("select event_id, percentage from event where task_id = ?",[request.form['delete_event'].split('.')[0]])]
        last_event = sql("select event_id, percentage from event where task_id = ?",[request.form['delete_event'].split('.')[0]])[list_event.index(max(list_event))]
        sql("update task set percentage = ? where task_id = ? ",[last_event[1],last_event[0].split('.')[0]])
        sql("update event set complete = ? where task_id = ? ",[last_event[1],last_event[0].split('.')[0]])
    else:
        sql("update task set percentage = ? where task_id = ? ",['',request.form['delete_event'].split('.')[0]])
    sql("insert into event_log values(?,?,?,?,?,?)",['',request.form['delete_event'],'B',session['username'],dt_to_str(dt.datetime.now()),'delete event'])
    if not sql("select * from event where task_id = ? ",[request.form['delete_event'].split('.')[0]]) and sql("select assigner from task where task_id = ?",[request.form['delete_event'].split('.')[0]])[0][0] == session['username'] :
        sql("delete from task where task_id=?",[request.form['delete_event'].split('.')[0]])
    block_base = [[r for i,r in enumerate(block_base[0]) if content_base[0][i][1] != request.form['delete_event']]]
    content_base = [[r for r in content_base[0] if r[1] != request.form['delete_event']]]

    old_task = sql("select task_id, name, percentage from task where executer = ? and percentage != '100%'",[session['username']])
    list_type_department = [r[0] for r in session['type_department']]
    work_hour = 14
    if block_base == [[]]:
        block_base = []
        content_base = []
    else:
        pass

    return jsonify({'data': render_template('adminday/job_render.html',block_base=block_base,content_base=content_base,
        list_type_department=list_type_department, work_hour=work_hour, old_task = old_task),'data_2':render_template('adminday/old_task_render.html',old_task=old_task,list_type_department=list_type_department)})

#################################################
@app.route('/ajax_edit_event', methods=['POST'])
def ajax_edit_event():
    block_base = ast.literal_eval(request.form['block_base'])
    content_base = ast.literal_eval(request.form['content_base'])

    old_event_id = request.form['edit_event']
    old_id = old_event_id.split('.')[0]
    name_edit = request.form['Task_name']
    type_department = request.form['type_department']
    job_type = [r[1] for r in session['type_department'] if r[0] == type_department][0]
    type_strategy = [r[2] for r in session['type_department'] if r[0] == type_department][0]
    content = request.form['Content']
    status = ''
    percentage = request.form['Percentage']
    executer_name = session['mail_name']
    # border_color = request.form.get('get_color_value' + old_event_id)

    # Update Event
    sql("update event set name=?,content = ?,type_department=?,percentage  = ? where event_id = ?",[ name_edit,content,type_department,percentage,old_event_id])
    # Update Task and Event
    sql("update task set percentage = ?,type_department = ?, type = ?, type_strategy = ? where task_id = ?",[percentage,type_department, job_type, type_strategy,old_id])

    sql("update event set complete = ?,type_department = ?, type = ?, type_strategy = ? where task_id = ?",[sql("select percentage from task where task_id = ?",[old_id])[0][0],type_department, job_type, type_strategy,old_id])
    sql("insert into event_log values(?,?,?,?,?,?)",[old_id,old_event_id,'B',session['username'],dt_to_str(dt.datetime.now()),'edit task'])
    content_base = [[list(r) for r in content_base[0]]]
    for i,r in enumerate(content_base[0]):
        if r[1] == request.form['edit_event']:
            content_base[0][i][event_field.index('name')] = name_edit
            content_base[0][i][event_field.index('content')] = content
            content_base[0][i][event_field.index('type_department')] = type_department
            content_base[0][i][event_field.index('percentage')] = percentage

            content_base[0][i][event_field.index('complete')] = sql("select percentage from task where task_id = ?",[old_id])[0][0]
            content_base[0][i][event_field.index('type_department')] = type_department
            content_base[0][i][event_field.index('type')] = job_type
            content_base[0][i][event_field.index('type_strategy')] = type_strategy

    old_task = sql("select task_id, name, percentage from task where executer = ? and percentage != '100%'",[session['username']])
    list_type_department = [r[0] for r in session['type_department']]
    work_hour = 14

    return jsonify({'data': render_template('adminday/job_render.html',block_base=block_base,content_base=content_base,list_type_department=list_type_department, work_hour=work_hour, old_task = old_task),'data_2':render_template('adminday/old_task_render.html',old_task=old_task,list_type_department=list_type_department)})

#################################################
@app.route('/ajax_add_old_task', methods=['POST'])
def ajax_add_old_task():
    block_base = ast.literal_eval(request.form['block_base'])
    content_base = ast.literal_eval(request.form['content_base'])

    result_task = sql("select * from task where executer = ? and percentage != '100%'",[session['username']])
    # Insert Database
    id_cong_viec_cu = request.form['select_cong_viec']
    
    event_id = event_id_create(id_cong_viec_cu)
    name = [r[task_field.index('name')] for r in result_task if r[0] == id_cong_viec_cu][0]
    type_department = [r[task_field.index('type_department')] for r in result_task if r[0] == id_cong_viec_cu][0]
    job_type = [r[task_field.index('type')] for r in result_task if r[0] == id_cong_viec_cu][0]
    type_strategy = [r[task_field.index('type_strategy')] for r in result_task if r[0] == id_cong_viec_cu][0]
    content = request.form['Content']
    status = ''
    percentage = request.form['Percentage']
    border_color = '#901e1d'
    executer = [r[task_field.index('executer')] for r in result_task if r[0] == id_cong_viec_cu][0]
    assigner = [r[task_field.index('assigner')] for r in result_task if r[0] == id_cong_viec_cu][0]
    executer_name = [r[task_field.index('executer_name')] for r in result_task if r[0] == id_cong_viec_cu][0]
    assigner_name = [r[task_field.index('assigner_name')] for r in result_task if r[0] == id_cong_viec_cu][0]
    start = index_to_time(request.form['time_start'])
    

    end = index_to_time(request.form['time_end'])
    last_update = index_to_time(request.form['time_end'])

    complete = ''
    department = [r[task_field.index('department')] for r in result_task if r[0] == id_cong_viec_cu][0]
    type_department = [r[task_field.index('type_department')] for r in result_task if r[0] == id_cong_viec_cu][0]
    supporter,supporter_name, customer, disable = ['']*4
    
    # Insert Event
    sql("insert into event({}) values({})".format(','.join(event_field),','.join(['?']*len(event_field))),[id_cong_viec_cu, event_id, name,job_type,type_strategy, content, status, percentage, executer, assigner,supporter,  executer_name, assigner_name,supporter_name, customer, disable,start, end,complete,department,type_department,border_color])
    # Update Task and Event
    sql("update task set last_update = ?, percentage = ? where task_id = ?",[last_update,percentage,id_cong_viec_cu])
    sql("update event set complete = ? where task_id = ?",[sql("select percentage from task where task_id = ?",[id_cong_viec_cu])[0][0],id_cong_viec_cu])
    if executer == assigner:
        sql("update task set end_time = ? where task_id = ?",[end,id_cong_viec_cu])
    else:
        pass

    sql("insert into event_log values(?,?,?,?,?,?)",[id_cong_viec_cu,event_id,'B',session['username'],dt_to_str(dt.datetime.now()),'old task'])

    # Update block_base, content_base
    if block_base:
        block_base = [block_base[0] + [[(int(request.form['time_start'])-1)*3+1, (int(request.form['time_end'])-1)*3+1]]]
        content_base = [content_base[0] + [[id_cong_viec_cu, event_id, name,job_type,type_strategy, content, status, percentage, executer, assigner,supporter,  executer_name, assigner_name,supporter_name, customer, disable,start, end,complete,department,type_department,border_color]]]
    else:
        block_base = [[[(int(request.form['time_start'])-1)*3+1, (int(request.form['time_end'])-1)*3+1]]]
        content_base = [[[id_cong_viec_cu, event_id, name,job_type,type_strategy, content, status, percentage, executer, assigner,supporter,  executer_name, assigner_name,supporter_name, customer, disable,start, end,complete,department,type_department,border_color]]]

    list_type_department = [r[0] for r in session['type_department']]
    work_hour = 14
    old_task = sql("select task_id, name, percentage from task where executer = ? and percentage != '100%'",[session['username']])
    
    return jsonify({'data': render_template('adminday/job_render.html',block_base=block_base,content_base=content_base,list_type_department=list_type_department, work_hour=work_hour, old_task = old_task),'data_2':render_template('adminday/old_task_render.html',old_task=old_task,list_type_department=list_type_department)})


@app.route('/management',methods=['GET', 'POST'])
@login_required
def management():
    # Prepare
    list_assignee = layout(session['username'])
    list_assignee.insert(0,sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where username = ?",[session['username']])[0])
    list_type_department = [r[0] for r in session['type_department']]
    day_selected = session['day_selected']
    list_moc_thoi_gian = ['07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']
    # Get profile
    if len(list_assignee) < 1:
        return redirect(url_for('nam'))
    #
    # ds_gio = ['07:00', '07:15', '07:30', '07:45', '08:00', '08:15', '08:30', '08:45', '09:00', '09:15', '09:30', '09:45', '10:00', '10:15', '10:30', '10:45', '11:00', '11:15', '11:30', '11:45', '12:00', '12:15', '12:30', '12:45', '13:00', '13:15', '13:30', '13:45', '14:00', '14:15', '14:30', '14:45', '15:00', '15:15', '15:30', '15:45', '16:00', '16:15', '16:30', '16:45', '17:00', '17:15', '17:30', '17:45', '18:00', '18:15', '18:30', '18:45', '19:00', '19:15', '19:30', '19:45', '20:00', '20:15', '20:30', '20:45', '21:00']
    # ds_index = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 52, 55, 58, 61, 64, 67, 70, 73, 76, 79, 82, 85, 88, 91, 94, 97, 100, 103, 106, 109, 112, 115, 118, 121, 124, 127, 130, 133, 136, 139, 142, 145, 148, 151, 154, 157, 160, 163, 166, 169]
   
    # content_task = sql("SELECT {} from task where assigner = ? and executer = ? and supporter != '' or assigner = ? and executer != ? and start_time like '%'+?+'%' order by convert(int,task_id)".format(','.join(task_field)),[session['username'],session['username'],session['username'],session['username'],d_to_str(session['day_selected'])])
    # block_task = [[ds_index[ds_gio.index(r[task_field.index('start_time')][:5])],ds_index[ds_gio.index(r[task_field.index('end_time')][:5])]] for r in content_task]
    day_selected,content_task,block_task = get_data(session['username'])

    # Get other var for html and JS
    day_now = dt.datetime.now()
    week_now = dt.datetime.now().isocalendar()[1]

    # Function
    if request.form.get('submit') == 'new_task_assignment':
        # Get from JS
        new_id = task_id_create()
        name = request.form.get('Task_name')
        type_department = request.form.get('type_department')
        content = request.form.get('Description')
        status = 'In progress'
        percentage = '0%'
        executer = [r[0] for r in list_assignee if r[2] == request.form.get('Executer')][0]

        if executer == session['username'] and not request.form.getlist('Supporter'):
            supporter = session['username']
            supporter_name = session['mail_name']
        else:
            supporter = '|'.join([r[0] for r1 in request.form.getlist('Supporter') for r in list_assignee if r[2] == r1])
            supporter_name = '|'.join([r[1] for r1 in request.form.getlist('Supporter') for r in list_assignee if r[2] == r1])

        assigner = session['username']
        executer_name = [r[1] for r in list_assignee if r[0] == executer][0]
        border_color = '#901d1e'
        assigner_name = session['mail_name']
        customer = ''
        disable = ''
        start = index_to_time(request.form.get('time_start'))

        end = index_to_time(request.form.get('time_end'))
        last_update = 'None'
        rating = ''
        department = session['department']
        job_type = [r[1] for r in session['type_department'] if r[0] == type_department][0]
        type_strategy = [r[2] for r in session['type_department'] if r[0] == type_department][0]

        # Insert Task and Noti
        sql("insert into task({}) values({})".format(','.join(task_field),','.join(['?']*len(task_field))),[new_id, name,job_type,type_strategy, content, status, percentage, executer, assigner, supporter, executer_name, assigner_name, supporter_name, customer, disable, start, end,last_update,rating,department,type_department,border_color])

        if assigner != executer:
            sql("insert into noti values({})".format(','.join(['?']*len(noti_field))),[executer,u'{} đã giao cho bạn công việc "{}"'.format(assigner_name,name),dt_to_str(dt.datetime.now()),'nam',start + '|' + new_id,'N','N',session['username'],noti_id_auto_create()])

            for i in supporter.split("|"):
                sql("insert into noti values({})".format(','.join(['?']*len(noti_field))),[i,u'{} đã giao cho bạn hỗ trợ công việc "{}"'.format(assigner_name,name),dt_to_str(dt.datetime.now()),'nam',start + '|' + new_id,'N','N',session['username'],noti_id_auto_create()])
        send_mail(executer,executer.replace('|',';'),sub_mail,body_giao_viec.format(assigner_name,executer_name,name,supporter_name.replace('|',',')))
        return redirect(url_for('management'))

    if request.form.get('delete_task'):
        if not sql("select * from event where task_id = ?",[request.form.get('delete_task')]):
            sql("delete from task where task_id = ? ",[request.form.get('delete_task')])
            sql("delete from noti where session = ? ",[request.form.get('delete_task')])
        else:
            pass
        return redirect(url_for('management'))    

    if request.form.get('edit_task_OK'):
        # Get from JS
        # ???
        old_id = request.form.get('edit_task_OK')
        name = request.form.get('Task_name' + str(old_id))
        type_department = request.form.get('type_department' + str(old_id))
        content = request.form.get('Content' + str(old_id))
        executer = [r[0] for r in list_assignee if r[2] == request.form.get('Executer' + str(old_id))][0]

        executer_name = [r[1] for r in list_assignee if r[0] == executer][0]
        # border_color = request.form.get('get_color_value' + str(old_id))

        supporter = '|'.join([r[0] for r1 in request.form.getlist('Supporter_x_' + str(old_id)) for r in list_assignee if r[2] == r1]) # ???

        supporter_name = '|'.join([r[1] for r1 in request.form.getlist('Supporter_x_' + str(old_id)) for r in list_assignee if r[2] == r1]) # ???

        assigner_name = session['mail_name']
        job_type = [r[1] for r in session['type_department'] if r[0] == type_department][0]
        type_strategy = [r[2] for r in session['type_department'] if r[0] == type_department][0]
        insert_test(supporter_name)
        # Update Task, Event and Insert Noti   

        sql("UPDATE task set name = ?, type_department = ?, type = ?, type_strategy = ?, content = ?, executer  = ?,  executer_name = ?, supporter = ?, supporter_name = ? where task_id = ?",[name, type_department,job_type, type_strategy, content, executer, executer_name, supporter, supporter_name, old_id])

        sql("UPDATE event set name = ?, type_department = ?, type  = ?, type_strategy = ?, content = ?, executer  = ?, executer_name = ?, supporter = ?, supporter_name = ? where task_id = ?",[name, type_department, job_type,  type_strategy, content, executer, executer_name, supporter, supporter_name, old_id])
        if executer != session['username'] and session['username'] not in supporter:
            sql("INSERT into noti values({})".format(','.join(['?']*len(noti_field))),[executer,u'{} đã thay đổi công việc "{}"'.format(assigner_name,name),dt_to_str(dt.datetime.now()),'viewtask',old_id,'N','N',session['username'],noti_id_auto_create()])

            for i in supporter.split("|"):
                sql("insert into noti values({})".format(','.join(['?']*len(noti_field))),[i,u'{} đã thay đổi công việc "{}"'.format(assigner_name,name),dt_to_str(dt.datetime.now()),'viewtask',old_id,'N','N',session['username'],noti_id_auto_create()])
        send_mail(executer,'',sub_mail,body_edit.format(assigner_name,name))
        return redirect(url_for('management'))

    if request.form.get('black'):
        old_id = request.form.get('black')
        border_color = request.form.get('get_color_value'+str(old_id))
        sql("UPDATE task set BORDER_COLOR = ? where task_id = ?",[border_color, old_id])
        return redirect(url_for('management'))
    if request.form.get('red'):
        old_id = request.form.get('red')
        border_color = request.form.get('get_color_value'+str(old_id))
        sql("UPDATE task set BORDER_COLOR = ? where task_id = ?",[border_color, old_id])
        return redirect(url_for('management'))
    if request.form.get('green'):
        old_id = request.form.get('green')
        border_color = request.form.get('get_color_value'+str(old_id))
        sql("UPDATE task set BORDER_COLOR = ? where task_id = ?",[border_color, old_id])
        return redirect(url_for('management'))
    if request.form.get('blue'):
        old_id = request.form.get('blue')
        border_color = request.form.get('get_color_value'+str(old_id))
        sql("UPDATE task set BORDER_COLOR = ? where task_id = ?",[border_color, old_id])
        return redirect(url_for('management'))
    if request.form.get('orange'):
        old_id = request.form.get('orange')
        border_color = request.form.get('get_color_value'+str(old_id))
        sql("UPDATE task set BORDER_COLOR = ? where task_id = ?",[border_color, old_id])
        return redirect(url_for('management'))

    if request.form.get('tracking'):
        session['task_id'] = request.form.get('tracking')
        return redirect(url_for('viewtask'))

    if request.form.get('select_day'):
        session['day_selected'] = dt.datetime.strptime(request.form.get('select_day'),'%d/%m/%Y')
        return redirect(url_for('management'))

    return render_template('adminday/ql.html',content_task = content_task, block_task = block_task, day_now=day_now,list_type_department=list_type_department,list_assignee=list_assignee,list_moc_thoi_gian=list_moc_thoi_gian,day_selected = day_selected)


@app.route('/task_report',methods=['GET', 'POST'])
@login_required
def task_report():
    list_assignee = layout(session['username'])
    ds_n_0 = [r1 for r in sql("select distinct n_0 from profile") for r1 in r[0].split('|')]
    ds_n_1 = [r1 for r in sql("select distinct n_1 from profile") for r1 in r[0].split('|')]
    ds_n_2 = [r1 for r in sql("select distinct n_2 from profile") for r1 in r[0].split('|')]
    if session['username'] in ds_n_0:
        ds_filter = [session['mail_name']] + ['AMC'] + [r[0] for r in sql("select distinct phong from profile")] + [r1[0] + '|' + r1[1] for r1 in sql("select distinct phong,bophan from profile where bophan != ''")] + [r[0] for r in sql("select distinct mail_name from profile where username != ?",[session['username']])]

    elif session['username'] in ds_n_1:
        ds_filter = [session['mail_name']] + [r[0] for r in sql("select distinct phong from profile where n_1 = ?",[session['username']])] + [r1[0] + '|' + r1[1] for r1 in sql("select distinct phong,bophan from profile where bophan != '' and n_1 = ?",[session['username']])] + [r[0] for r in sql("select distinct mail_name from profile where n_1 = ?",[session['username']])]

    elif session['username'] in ds_n_2:
        ds_filter = [session['mail_name']] + [r1[0] + '|' + r1[1] for r1 in sql("select distinct phong,bophan from profile where bophan != '' and n_2 = ?",[session['username']])] + [r[0] for r in sql("select distinct mail_name from profile where n_2 = ?",[session['username']])]

    else:
        ds_filter = []



    if request.form.get('submit_filter'):
        filter_value = request.form.get('filter_trungtam')
        start_time_str = str(request.form.get('start_time'))
        if start_time_str:
            start_time = str_to_dt('{}/{}/{}'.format(start_time_str[-2:],start_time_str[5:7],start_time_str[:4]))
        else:
            start_time = ''
        end_time_str = str(request.form.get('end_time'))
        if end_time_str:
            end_time = str_to_dt('{}/{}/{}'.format(end_time_str[-2:],end_time_str[5:7],end_time_str[:4]))
        else:
            end_time = ''
        so_gio_lam_viec,so_cong_viec,ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay,so_ngay_lam_viec,phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam,ds_cv_theo_cong_ty,ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao,ty_le_qua_han,ty_le_qua_han_giao_viec,so_cong_viec_qua_han,so_cong_viec_giao_qua_han,so_nguoi_thuc_hien,ty_le_tuan_thu_bao_cao_theo_user = calculate(request.form.get('filter_trungtam'),start_time,end_time)
        filter_trungtam = request.form.get('filter_trungtam')
        ds_10_ngay_gan_nhat = ds_10_ngay_gan_nhat.split('|')
        ds_cong_viec_trong_10_ngay = ds_cong_viec_trong_10_ngay.split('|')
        phan_bo_cv_theo_trung_tam = phan_bo_cv_theo_trung_tam.split('|')
        phan_bo_cv_theo_cong_ty = phan_bo_cv_theo_cong_ty.split('|')
        phan_bo_cv_theo_toan_hang = phan_bo_cv_theo_toan_hang.split('|')
        ds_cv_theo_trung_tam = ds_cv_theo_trung_tam.split('|')
        ds_cv_theo_cong_ty = ds_cv_theo_cong_ty.split('|')
        ds_cv_theo_toan_hang = ds_cv_theo_toan_hang.split('|')
        ty_le_qua_han = ty_le_qua_han.split('|')
        so_cong_viec_qua_han = so_cong_viec_qua_han.split('|')

        if ty_le_qua_han_giao_viec:
            ty_le_qua_han_giao_viec = ty_le_qua_han_giao_viec.split('|')
        else:
            ty_le_qua_han_giao_viec = []
        if so_cong_viec_giao_qua_han:
            so_cong_viec_giao_qua_han = so_cong_viec_giao_qua_han.split('|')
        else:
            so_cong_viec_giao_qua_han = []

        if phan_bo_cv_theo_trung_tam != ['']:
            ds_cv_theo_trung_tam = [r for i,r in enumerate(ds_cv_theo_trung_tam) if phan_bo_cv_theo_trung_tam[i] != '0%']
            phan_bo_cv_theo_trung_tam = [r for r in phan_bo_cv_theo_trung_tam if r != '0%' ]
            ty_le_chuyen_doi = 100/sum([float(r[:-1]) for r in phan_bo_cv_theo_trung_tam])
            phan_bo_cv_theo_trung_tam = [str(round(float(r[:-1])*ty_le_chuyen_doi,1)) + '%' for r in phan_bo_cv_theo_trung_tam]
        else:
            pass
        if phan_bo_cv_theo_cong_ty != ['']:
            ds_cv_theo_cong_ty = [r for i,r in enumerate(ds_cv_theo_cong_ty) if phan_bo_cv_theo_cong_ty[i] != '0%']
            phan_bo_cv_theo_cong_ty = [r for r in phan_bo_cv_theo_cong_ty if r != '0%' ]
            ty_le_chuyen_doi = 100/sum([float(r[:-1]) for r in phan_bo_cv_theo_cong_ty])
            phan_bo_cv_theo_cong_ty = [str(round(float(r[:-1])*ty_le_chuyen_doi,1)) + '%' for r in phan_bo_cv_theo_cong_ty]
        else:
            pass
        if phan_bo_cv_theo_toan_hang != ['']:
            ty_le_chuyen_doi = 100/sum([float(r[:-1]) for r in phan_bo_cv_theo_toan_hang])
            phan_bo_cv_theo_toan_hang = [str(round(float(r[:-1])*ty_le_chuyen_doi,1)) + '%' for r in phan_bo_cv_theo_toan_hang]
        else:
            pass
        return render_template('adminday/task_report.html',so_gio_lam_viec = so_gio_lam_viec,so_cong_viec = so_cong_viec,ds_10_ngay_gan_nhat = ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay = ds_cong_viec_trong_10_ngay,so_ngay_lam_viec = so_ngay_lam_viec,phan_bo_cv_theo_trung_tam = phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty = phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang = phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam = ds_cv_theo_trung_tam,ds_cv_theo_cong_ty = ds_cv_theo_cong_ty,ds_cv_theo_toan_hang = ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao = ty_le_tuan_thu_bao_cao,ty_le_qua_han = ty_le_qua_han,ds_filter = ds_filter,start_time_str=start_time_str,end_time_str=end_time_str,filter_trungtam=filter_trungtam,ty_le_qua_han_giao_viec=ty_le_qua_han_giao_viec,so_cong_viec_qua_han=so_cong_viec_qua_han,so_cong_viec_giao_qua_han=so_cong_viec_giao_qua_han,filter_value=filter_value,so_nguoi_thuc_hien=so_nguoi_thuc_hien,ty_le_tuan_thu_bao_cao_theo_user=ty_le_tuan_thu_bao_cao_theo_user)

    so_gio_lam_viec,so_cong_viec,ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay,so_ngay_lam_viec,phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam,ds_cv_theo_cong_ty,ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao,ty_le_qua_han,ty_le_qua_han_giao_viec,so_cong_viec_qua_han,so_cong_viec_giao_qua_han,so_nguoi_thuc_hien,ty_le_tuan_thu_bao_cao_theo_user = calculate(session['mail_name'],'','')
    filter_trungtam = session['mail_name']
    start_time_str = ''
    end_time_str = ''
    ds_10_ngay_gan_nhat = ds_10_ngay_gan_nhat.split('|')
    ds_cong_viec_trong_10_ngay = ds_cong_viec_trong_10_ngay.split('|')
    phan_bo_cv_theo_trung_tam = phan_bo_cv_theo_trung_tam.split('|')
    phan_bo_cv_theo_cong_ty = phan_bo_cv_theo_cong_ty.split('|')
    phan_bo_cv_theo_toan_hang = phan_bo_cv_theo_toan_hang.split('|')
    ds_cv_theo_trung_tam = ds_cv_theo_trung_tam.split('|')
    ds_cv_theo_cong_ty = ds_cv_theo_cong_ty.split('|')
    ds_cv_theo_toan_hang = ds_cv_theo_toan_hang.split('|')
    ty_le_qua_han = ty_le_qua_han.split('|')
    so_cong_viec_qua_han = so_cong_viec_qua_han.split('|')
    if ty_le_qua_han_giao_viec:
        ty_le_qua_han_giao_viec = ty_le_qua_han_giao_viec.split('|')
    else:
        ty_le_qua_han_giao_viec = []
    if so_cong_viec_giao_qua_han:
        so_cong_viec_giao_qua_han = so_cong_viec_giao_qua_han.split('|')
    else:
        so_cong_viec_giao_qua_han = []

    if phan_bo_cv_theo_trung_tam != ['']:
        ds_cv_theo_trung_tam = [r for i,r in enumerate(ds_cv_theo_trung_tam) if phan_bo_cv_theo_trung_tam[i] != '0%']
        phan_bo_cv_theo_trung_tam = [r for r in phan_bo_cv_theo_trung_tam if r != '0%' ]
        ty_le_chuyen_doi = 100/sum([float(r[:-1]) for r in phan_bo_cv_theo_trung_tam])
        phan_bo_cv_theo_trung_tam = [str(round(float(r[:-1])*ty_le_chuyen_doi,1)) + '%' for r in phan_bo_cv_theo_trung_tam]
    else:
        pass
    if phan_bo_cv_theo_cong_ty != ['']:
        ds_cv_theo_cong_ty = [r for i,r in enumerate(ds_cv_theo_cong_ty) if phan_bo_cv_theo_cong_ty[i] != '0%']
        phan_bo_cv_theo_cong_ty = [r for r in phan_bo_cv_theo_cong_ty if r != '0%' ]
        ty_le_chuyen_doi = 100/sum([float(r[:-1]) for r in phan_bo_cv_theo_cong_ty])
        phan_bo_cv_theo_cong_ty = [str(round(float(r[:-1])*ty_le_chuyen_doi,1)) + '%' for r in phan_bo_cv_theo_cong_ty]
    else:
        pass
    if phan_bo_cv_theo_toan_hang != ['']:
        ty_le_chuyen_doi = 100/sum([float(r[:-1]) for r in phan_bo_cv_theo_toan_hang])
        phan_bo_cv_theo_toan_hang = [str(round(float(r[:-1])*ty_le_chuyen_doi,1)) + '%' for r in phan_bo_cv_theo_toan_hang]
    else:
        pass
    return render_template('adminday/task_report.html',so_gio_lam_viec = so_gio_lam_viec,so_cong_viec = so_cong_viec,ds_10_ngay_gan_nhat = ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay = ds_cong_viec_trong_10_ngay,so_ngay_lam_viec = so_ngay_lam_viec,phan_bo_cv_theo_trung_tam = phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty = phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang = phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam = ds_cv_theo_trung_tam,ds_cv_theo_cong_ty = ds_cv_theo_cong_ty,ds_cv_theo_toan_hang = ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao = ty_le_tuan_thu_bao_cao,ty_le_qua_han = ty_le_qua_han,ds_filter = ds_filter,start_time_str=start_time_str,end_time_str=end_time_str,filter_trungtam=filter_trungtam,ds_n_0=ds_n_0,ds_n_1=ds_n_1,ds_n_2=ds_n_2,ty_le_qua_han_giao_viec=ty_le_qua_han_giao_viec,so_cong_viec_qua_han=so_cong_viec_qua_han,so_cong_viec_giao_qua_han=so_cong_viec_giao_qua_han,so_nguoi_thuc_hien=so_nguoi_thuc_hien,ty_le_tuan_thu_bao_cao_theo_user=ty_le_tuan_thu_bao_cao_theo_user)

@app.route('/department',methods=['GET', 'POST'])
@login_required
def department():
    if session['username'] not in ['lannt', 'phuctv2']:
        return redirect(url_for('intro'))
    list_phong = sql("select distinct phong from Profile")
    session["department"] = ''
    if request.form.get("select_department"):
        session["department"] = request.form.get("select_department")
        list_user_in_department = sql("select username,hoten,mail_name,n_1,n_2,n_3,bophan, maNV from profile where phong = ? order by username",[session["department"]])
        list_user_name = [''] + [r[0] for r in list_user_in_department]
        list_bo_phan = [r[0] for r in sql("select distinct bophan from profile where phong = ?",[session["department"]])]
        return render_template('department.html', 
                                list_phong=list_phong,
                                list_user_in_department=list_user_in_department,
                                list_user_name=list_user_name,
                                list_bo_phan=list_bo_phan)
    return render_template('department.html', list_phong=list_phong)

@app.route('/ajax_update_user_info',methods=['GET', 'POST'])
# @login_required
def ajax_update_user_info():
    Username = request.args['Username']
    name = request.args['name']
    mail = request.args['mail']
    ma_nv = request.args['ma_nv']

    select_bp = request.args['select_bp']
    assigner1 = request.args['assigner1']
    assigner2 = request.args['assigner2']
    assigner3 = request.args['assigner3']
    sql("""UPDATE profile 
           set hoten = ?,
               mail_name = ?,
               maNV = ?,
               bophan = ?,
               n_1 = ?,
               n_2 = ?,
               n_3 = ?
               where username = ?""",[name, mail, ma_nv, select_bp, assigner1, assigner2, assigner3, Username])
    return 1


@app.route('/ajax_add_user_info',methods=['GET', 'POST'])
# @login_required
def ajax_add_user_info():
    Username = request.args['Username']
    if  not sql("select * from profile where username = ?",[Username]):
        name = request.args['name']
        mail = request.args['mail']
        ma_nv = request.args['ma_nv']
        select_bp = request.args['select_bp']
        assigner1 = request.args['assigner1']
        assigner2 = request.args['assigner2']
        assigner3 = request.args['assigner3']
        try:
            name_n_1 = sql("select mail_name from profile where username = ?",[assigner1])[0][0]
        except:
            name_n_1 = ''
        try:
            name_n_2 = sql("select mail_name from profile where username = ?",[assigner2])[0][0]
        except:
            name_n_2 = ''
        try:
            name_n_3 = sql("select mail_name from profile where username = ?",[assigner3])[0][0]
        except:
            name_n_3 = ''

        f = ['username', 'hoTen', 'mail_name', 'maNV', 'phong', 'bophan', 'name_n_1', 'name_n_2', 'name_n_3', 'n_0', 'n_1', 'n_2', 'n_3']
        sql("""INSERT into profile({}) 
                VALUES({})""".format(",".join(f) ,",".join(["?"]*len(f))), [Username, name, mail, ma_nv,
                session['department'], select_bp, name_n_1, name_n_2, name_n_3, "hangbtt6|nhungth|huongttt4|thuytt31|thuypt31|nhungttt4|hoavm|hantn|ngant27|lamnt12|lannt|lynth2|hangvtt2|phuctv2",
                assigner1, assigner2, assigner3])
        sql("""INSERT into userr values(?,?,?,?)""",[Username, hash_user("123456"), 'user','123'])
    return 1


@app.route('/ajax_del_user_info',methods=['GET', 'POST'])
# @login_required
def ajax_del_user_info():
    Username = request.args['Username']
    sql("""DELETE from profile where username = ?""",[Username])
    return jsonify({'Username': Username})


@app.route('/',methods=['GET', 'POST'])    
@app.route('/intro',methods=['GET', 'POST'])
@login_required
def intro():
    # Prepare
    list_ngay_nghi = [dt.date(2017,5,1),dt.date(2017,5,2),dt.date(2017,4,6)]
    list_assignee = layout(session['username'])
    task_myself = sql("select * from task where executer = ? and assigner = ?",[session['username'],session['username']])
    task_myself_finish = [r for r in task_myself if r[task_field.index('percentage')] == '100%']
    task_myself_notfinish = [r for r in task_myself if r[task_field.index('percentage')] != '100%']
    task_assigned = sql("select * from task where executer = ? and assigner != ?",[session['username'],session['username']])
    task_assigned_finish = [r for r in task_assigned if r[task_field.index('percentage')] == '100%']
    task_assigned_finish_y = [r for r in task_assigned if r[task_field.index('percentage')] == '100%' and r[task_field.index('status')] != 'Y']
    task_assigned_notfinish = [r for r in task_assigned if r[task_field.index('percentage')] != '100%']
    data_task = sql("select * from task where executer = ?",[session['username']])
    data_task = [r for r in data_task if str_to_dt(r[task_field.index('end_time')]) <= dt.datetime.now()]
    data_event = sql("select * from event where executer = ?",[session['username']])
    data_event = [r for r in data_event if str_to_dt(r[task_field.index('end_time')]) <= dt.datetime.now()]
    data_event = [r for r in data_event if str_to_dt(r[event_field.index('start_time')]) >= start_date_demo]
    # total_time = sum([(str_to_dt(r[event_field.index('end_time')]) - str_to_dt(r[event_field.index('start_time')])).total_seconds() for r in data_event])/3600
    total_time = int(round(sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')])) for r in data_event if r[event_field.index("executer")] == session["username"]])/3600,0))
    count_day_from_start = ((dt.datetime.combine(dt.datetime.now().date(),special_day.time()) - start_date_demo).total_seconds()/24)/3600
    list_day_from_start = [start_date_demo + dt.timedelta(days=i) for i in xrange(int(count_day_from_start+1))]
    total_time_full = len([r for r in list_day_from_start if r.weekday() not in (5,6) and r.date() not in list_ngay_nghi])*8 + len([r for r in list_day_from_start if r.weekday() == 5])*4
    percen_time = total_time/total_time_full
    if percen_time > 1:
        percen_time = 1
    if [int(r[0]) for r in sql("select rating from task where executer = ? and rating != ''",[session['username']])]:
        avg_rating = sum([int(r[0]) for r in sql("select rating from task where executer = ? and rating != ''",[session['username']])])/len([int(r[0]) for r in sql("select rating from task where executer = ? and rating != ''",[session['username']])])
    else:
        avg_rating = 'N'
    list_rating = [len(sql("select rating from task where executer = ? and rating = ?",[session['username'],r])) for r in range(1,6)]
    if data_task:
        total_time_task = sum([(str_to_dt(r[task_field.index('end_time')]) - str_to_dt(r[task_field.index('start_time')])).total_seconds() for r in data_task])


        list_phan_bo_type = [[r1,round(sum([(str_to_dt(r[task_field.index('end_time')]) - str_to_dt(r[task_field.index('start_time')])).total_seconds()/len(r[task_field.index('type')].split(';')) for r in data_task if r1 in r[task_field.index('type')]])/total_time_task,2)] for r1 in list_type]
        list_phan_bo_type_strategy = [[r1,round(sum([(str_to_dt(r[task_field.index('end_time')]) - str_to_dt(r[task_field.index('start_time')])).total_seconds()/len(r[task_field.index('type_strategy')].split(';')) for r in data_task if r1 in r[task_field.index('type_strategy')]])/total_time_task,2)] for r1 in list_type_strategy]
        list_phan_bo_type = sorted(list_phan_bo_type, key=itemgetter(1),reverse = True)
        list_phan_bo_type_strategy = sorted(list_phan_bo_type_strategy, key=itemgetter(1),reverse = True)
        list_phan_bo_type = list_phan_bo_type[:5]
    else:
        list_phan_bo_type = []
        list_phan_bo_type_strategy = []
    if request.form.get('go_task'):
        session['task_id'] = request.form.get('go_task')
        return redirect(url_for('viewtask'))
    if request.form.get('btn_noti_content'):
        i_noti = request.form.get('btn_noti_content')
        if request.form.get('redirect_noti_' + i_noti) == 'viewtask':
            session['task_id'] = request.form.get('input_noti_' + i_noti)
        if request.form.get('redirect_noti_' + i_noti) == 'nam':
            session['day_selected'] = str_to_dt(request.form.get('input_noti_' + i_noti).split('|')[0])
            session['task_id'] = request.form.get('input_noti_' + i_noti).split('|')[1]
        sql("update noti set read_real = 'Y' where noti_id = ?",[request.form.get('noti_id_' + i_noti)])
        return redirect(url_for(request.form.get('redirect_noti_' + i_noti) ))
    last_time = ''
    last_user = ''
    return render_template(
        'intro.html',last_user=last_user,last_time=last_time,task_myself=task_myself, task_myself_finish=task_myself_finish, task_myself_notfinish=task_myself_notfinish, task_assigned=task_assigned, task_assigned_finish=task_assigned_finish, task_assigned_finish_y=task_assigned_finish_y, task_assigned_notfinish=task_assigned_notfinish,total_time=total_time, total_time_full=total_time_full,percen_time=percen_time,avg_rating=avg_rating, list_rating=list_rating, list_phan_bo_type=list_phan_bo_type, list_phan_bo_type_strategy=list_phan_bo_type_strategy,)


   ########################################
@app.route('/searchprofile',methods=['GET', 'POST'])
@login_required
def searchprofile():
 ##########
    b = sql("select hoten from Profile")
    list_phong = sql("select distinct phong from Profile")

    if request.method == 'POST':
        user = request.form['hoten']
        manv = request.form['maNV']
        donvi = request.form['donvi']
        session["donvi"] = request.form['donvi']
        ###!1111111111111111111111111111        
        if user =='' and manv !='' and donvi !='':
            u = sql("select * from Profile where maNV=(?) and phong=(?)",(manv,donvi,))               
        ###!22222222222222222222222222222!        
        elif user =='' and donvi =='' and manv !='':
            u = sql("select * from Profile where maNV=(?)",(manv,))
            if u == []:
                u = [('','','','','','','','','','','','')]
        ###!333333333333333333333333333333333        
        elif user =='' and manv =='' and donvi != '':
            u = sql("select * from Profile where phong=(?)",(donvi,))
        ###!44444444444444444444444444444444444        
        elif manv =='' and user !='' and donvi !='':
            u = sql("select * from Profile where hoten=(?) and phong=(?)",(user,donvi,))               
        ###!5555555555555555555555555555555555        
        elif manv =='' and donvi =='' and user !='':            
            u = sql("select * from Profile where hoten=(?)",(user,))            
               
        ###!666666666666666666666666666666        
        elif donvi =='' and user !='' and manv != '':            
            u = sql("select * from Profile where hoten=(?) and maNV=(?)",(user,manv,))
        return render_template(
        'profile/searchprofile.html',
        title=u'Thông tin cá nhân',u=u,user=user,b=b,list_phong=list_phong)            
####       
    return render_template(
        'profile/searchprofile.html',
        title=u'Thông tin cá nhân',list_phong=list_phong)



@app.route('/_rating')
def rating():
    star = request.args.get('star', 0, type=int)
    assigner = request.args.get('assigner', 0, type=str)
    assigner_name = request.args.get('assigner_name', 0, type=str)
    executer = request.args.get('executer', 0, type=str)

    sql("update task set rating = ? where task_id = ? and assigner = ?",[star,session['task_id'],assigner])

    if executer != session["username"]:
        sql("insert into noti values({})".format(','.join(['?']*len(noti_field))),[executer,u'{} đã chấm điểm công việc của bạn.'.format(assigner_name),dt_to_str(dt.datetime.now()),'viewtask',session['task_id'],'N','N',session['username'],noti_id_auto_create()])
    return jsonify()

#########################################
@app.route('/editprofile',methods=['GET', 'POST'])
@login_required
def editprofile():
    user = session['username']
    profile_user = sql("select * from profile where username = ?",[user])
    if request.method == 'POST':
    ##        manv = request.form['maNV']
    ##        hoten = request.form['hoTen']
        ngaysinh = request.form['ngaysinh']
        CMND = request.form['CMND']
    ##        ngayvaolam = request.form['ngayvaolam']
    ##        mail = request.form['mail']
        phone = request.form['phone']
        mobile = request.form['mobile']
        diachi = request.form['diaChi']
    ##        phong = request.form['phong']
        
        
        if request.form['submit'] == u'Chỉnh sửa':
            sql("""update Profile set ngaysinh=(?),CMND=(?),phone=(?),mobile=(?),diachi=(?) \
        where username=(?)""",(ngaysinh,CMND,phone,mobile,diachi,user,))
            return redirect(url_for('test'))
    return render_template(
                'profile/editprofile.html',
                title=u'Thông tin cá nhân',user=user,profile_user=profile_user,)

@app.route('/tutorial',methods=['GET', 'POST'])
@login_required
def tutorial():
    return render_template('adminday/tutorial.html',)


@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/list_event_2')
def station_2():
    session["end_time"] = dt_to_str_nguoc(dt.datetime.now())[:10]
    session["start_time"] = dt_to_str_nguoc(dt.datetime.now()-timedelta(days=7))[:10]
    session['time_end_select'] = dt.datetime.today().strftime('%Y-%m-%d')
    session['time_select'] = (dt.datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d')
    return redirect(url_for('list_event'))
##
@app.route('/list_event',methods=['GET', 'POST'])
@login_required
def list_event():
    list_assignee = layout(session['username'])
    report_content_field = ['executer','executer_name','name','type_department','type_strategy','content','percentage','start_time','end_time','task_id','assigner','supporter']
    if len(list_assignee) == 0:
        return redirect(url_for("intro"))
    list_content = ''
    if "executer" in session and "start_time" in session and "end_time" in session:
        list_content = sql("""select {} from event where executer = ?""".format(",".join(report_content_field)),[session["executer"]])
        list_content = [r for r in list_content if str_to_dt(session['start_time']) <= str_to_dt(r[report_content_field.index("start_time")]) and str_to_dt(session['end_time']) + dt.timedelta(days=1)>= str_to_dt(r[report_content_field.index("end_time")])]
        list_content = [list(r) + [u"Công việc được giao"] if r[report_content_field.index("assigner")] != session["executer"] else list(r) + [u"Công việc tự thực hiện"] if r[report_content_field.index("assigner")] == session["executer"] and r[report_content_field.index("supporter")] == '' else list(r) + [u"Công việc tự lập kế hoạch"] for r in list_content]
        # list_content = sorted(list_content, key = lambda x: (x[report_content_field.index("executer")],str_to_dt(x[report_content_field.index("start_time")])),reverse=True)
        list_content = [list(r) + [u"Công việc được giao"] if r[report_content_field.index("assigner")] != r[report_content_field.index("executer")] else list(r) + [u"Công việc tự thực hiện"] if r[report_content_field.index("assigner")] == r[report_content_field.index("executer")] and r[report_content_field.index("supporter")] == '' else list(r) + [u"Công việc tự lập kế hoạch"] for r in list_content]
    else:
        
        if "executer" in session and "start_time" not in session and "end_time" not in session:
            list_content = sql("select {} from event where {} ".format(",".join(report_content_field)," or ".join(["executer = ? "]*len(list_assignee))),[r[0] for r in list_assignee])
            list_content = [r for r in list_content if r[report_content_field.index("executer")] == session['executer']]
            list_content = [list(r) + [u"Công việc được giao"] if r[report_content_field.index("assigner")] != session["executer"] else list(r) + [u"Công việc tự thực hiện"] if r[report_content_field.index("assigner")] == session["executer"] and r[report_content_field.index("supporter")] == '' else list(r) + [u"Công việc tự lập kế hoạch"] for r in list_content]
            # list_content = sorted(list_content, key = lambda x: (x[report_content_field.index("executer")],str_to_dt(x[report_content_field.index("start_time")])),reverse=True)
            list_content = [list(r) + [u"Công việc được giao"] if r[report_content_field.index("assigner")] != r[report_content_field.index("executer")] else list(r) + [u"Công việc tự thực hiện"] if r[report_content_field.index("assigner")] == r[report_content_field.index("executer")] and r[report_content_field.index("supporter")] == '' else list(r) + [u"Công việc tự lập kế hoạch"] for r in list_content]
        if "executer" not in session and "start_time" in session and "end_time" in session:
            list_content = sql("select {} from event where {} ".format(",".join(report_content_field)," or ".join(["executer = ? "]*len(list_assignee))),[r[0] for r in list_assignee])
            list_content = [r for r in list_content if str_to_dt(session['start_time']) <= str_to_dt(r[report_content_field.index("start_time")]) and str_to_dt(session['end_time']) + dt.timedelta(days=1)>= str_to_dt(r[report_content_field.index("end_time")])]
            list_content = [list(r) + [u"Công việc được giao"] if r[report_content_field.index("assigner")] != r[report_content_field.index("executer")] else list(r) + [u"Công việc tự thực hiện"] if r[report_content_field.index("assigner")] == r[report_content_field.index("executer")] and r[report_content_field.index("supporter")] == '' else list(r) + [u"Công việc tự lập kế hoạch"] for r in list_content]
            # list_content = sorted(list_content, key = lambda x: (x[report_content_field.index("executer")],str_to_dt(x[report_content_field.index("start_time")])),reverse=True)
            list_content = [list(r) + [u"Công việc được giao"] if r[report_content_field.index("assigner")] != r[report_content_field.index("executer")] else list(r) + [u"Công việc tự thực hiện"] if r[report_content_field.index("assigner")] == r[report_content_field.index("executer")] and r[report_content_field.index("supporter")] == '' else list(r) + [u"Công việc tự lập kế hoạch"] for r in list_content]
        # else:
        #     list_content = [r for r in list_content if str_to_dt(r[report_content_field.index("start_time")]) >= dt.datetime.now() - dt.timedelta(days=30)]

    if request.form.get("view_content"):
        if request.form.get("executer"):
            session["executer_name"] = request.form.get("executer")
            try:
                session["executer"] = [r[0] for r in list_assignee if r[1] == request.form.get("executer")][0]
            except:
                pass
        else:
            session.pop('executer', None)
            session.pop('executer_name', None)
        try:
            int(session["executer"])
            session['task_id'] = session["executer"]
            return redirect(url_for('viewtask'))
        except:
            pass
        if request.form.get("start_time") != '':
            session["time_select"] = request.form.get("start_time")
            session["time_end_select"] = request.form.get("end_time")
            convert_date = request.form.get("start_time").split("-")
            convert_date_end = request.form.get("end_time").split("-")

            session["start_time"] = convert_date[2]+"/"+convert_date[1]+"/"+convert_date[0]
            session["end_time"] = convert_date_end[2]+"/"+convert_date_end[1]+"/"+convert_date_end[0]
            # session["start_time"] = request.form.get("start_time")
        else:
            session.pop('start_time', None)
            session.pop('end_time', None)
            session.pop('time_select', None)
            session.pop('time_end_select', None)
        return redirect(url_for("list_event"))
    if request.form.get("go_viewtask"):
        session['task_id'] = request.form.get("go_viewtask")
        return redirect(url_for("viewtask"))
    return render_template('list_event.html',list_content=list_content,list_assignee=list_assignee)  

@app.route('/profile',methods=['GET', 'POST'])
@login_required
def test():
    user = session['username']
    u = sql('select * from Profile where username=(?)',(user,))
    # list_noti = sql("select top 20 * from noti where username = ? order by noti_id desc",[session['username']])

    if u == []:
        u = [('','','','','','','','','','','','')]
    return render_template(
        'test.html',
        title= u'Thông tin cá nhân',u=u,user=user,)
##################################

@app.route('/changepass',methods=['GET', 'POST'])
@login_required
def changepass():
    if request.method == "POST":
        pwd = request.form.get('pwd')
        pwd1 = request.form.get('pwd1')
        pwd2 = request.form.get('pwd2')
        sql('update userr set password = ? where username = ?',[hash_user(pwd1),session['username']])
        return redirect(url_for('test'))

    return render_template(
        'profile/changepass.html',)


@app.route('/_cmt_task')
def cmt_task():
    """Add two numbers server side, ridiculous but well..."""
    a = request.args.get('a', 0, type=None)
    b = request.args.get('b', 0, type=None)
    
    username = [r[1] for r in profile if r[0] == session['username']][0]
    sql("insert into cmt values({})".format(','.join(['?']*len(cmt_field))),[session['task_id'],username,a,dt_to_str(dt.datetime.now())])
    t = get_cmt(session['task_id'])
    return jsonify(result=t,test=12345)
