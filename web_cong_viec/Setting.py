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

def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha1(salt.encode() + password.encode()).hexdigest() + ':' + salt

def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha1(salt.encode() + user_password.encode()).hexdigest()

def dt_to_str(x):
    return '{} {}/{}/{}'.format(str(x)[11:16],str(x)[8:10],str(x)[5:7],str(x)[:4])

def d_to_str(x):
    return '{}/{}/{}'.format(str(x)[8:10],str(x)[5:7],str(x)[:4])

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

def khung_gio(x,y):
    return ['07:00','21:00',15,14]

def index_to_time(x,y,z=''):
    if y == 'day':
        time_begin, time_finish, min_unit, work_hour = khung_gio(session['username'],session['day_selected'])
        a = [str(i) for i in range(1,int(work_hour*60/min_unit + 2))]
        b = [add_time(dt.time(int(time_begin[:2]),int(time_begin[-2:])),i) for i in range(0,int((work_hour*60/min_unit + 1)*min_unit),min_unit)]
        return dt_to_str(dt.datetime.combine(session['day_selected'].date(),[b[i] for i,r in enumerate(a) if r == x][0]))
    if y == 'week':
        week_selected = [dt.datetime.strptime("{}-{}-2017".format(r,session['day_selected'].isocalendar()[1]),"%w-%W-%Y") for r in range(1,7)]
        if z == 'N':
            list_finish = [khung_gio(session['username'],r)[1] + ' ' + d_to_str(r) for r in week_selected]
            return list_finish[int(x)-2]
        else:
            list_begin = [khung_gio(session['username'],r)[0] + ' ' + d_to_str(r) for r in week_selected]
            return list_begin[int(x)-1]

def index_to_time_management(x,y,z,w=''):
    if y == 'day':
        day_selected = session['day_selected']
        a = [str(i) for i in range(1,int(work_hour_default*60/min_unit_default + 2))]
        b = [add_time(dt.time(int(time_begin_default[:2]),int(time_begin_default[-2:])),i) for i in range(0,int((work_hour_default*60/min_unit_default + 1)*min_unit_default),min_unit_default)]
        return dt_to_str(dt.datetime.combine(session['day_selected'].date(),[b[i] for i,r in enumerate(a) if r == x][0]))
    if y == 'week':
        week_selected = [dt.datetime.strptime("{}-{}-2017".format(r,session['day_selected'].isocalendar()[1]),"%w-%W-%Y") for r in range(1,7)]
        if w == 'N':
            list_finish = [khung_gio(z,r)[1] + ' ' + d_to_str(r) for r in week_selected]
            return list_finish[int(x)-2]
        else:
            list_begin = [khung_gio(z,r)[0] + ' ' + d_to_str(r) for r in week_selected]
            return list_begin[int(x)-1]

# def time_dif(x,y):
#     list_ngay_dt = [x + dt.timedelta(days=i) for i in range(int((y.date() - x.date()).total_seconds()/(24*3600)) + 1)]
#     total_time = 0
#     if len(list_ngay_dt) == 1:
#         total_time = (y-x).total_seconds()
#     elif len(list_ngay_dt) == 2:
#         total_time += (str_to_dt(khung_gio(session['username'],list_ngay_dt[0])[1] + ' ' + d_to_str(list_ngay_dt[0])) - x).total_seconds()
#         total_time += (y - str_to_dt(khung_gio(session['username'],list_ngay_dt[1])[0] + ' ' + d_to_str(list_ngay_dt[1]))).total_seconds()
#     else:
#         total_time += (str_to_dt(khung_gio(session['username'],list_ngay_dt[0])[1] + ' ' + d_to_str(list_ngay_dt[0])) - x).total_seconds()
#         total_time += (y - str_to_dt(khung_gio(session['username'],list_ngay_dt[-1])[0] + ' ' + d_to_str(list_ngay_dt[-1]))).total_seconds()
#         for r in list_ngay_dt[1:-1]:
#             total_time += khung_gio(session['username'],r)[3]*3600
#     return total_time

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
        total_time += (str_to_dt(khung_gio(z,list_ngay_dt[0])[1] + ' ' + d_to_str(list_ngay_dt[0])) - x).total_seconds()
        total_time += (y - str_to_dt(khung_gio(z,list_ngay_dt[1])[0] + ' ' + d_to_str(list_ngay_dt[1]))).total_seconds()
    else:
        total_time += (str_to_dt(khung_gio(z,list_ngay_dt[0])[1] + ' ' + d_to_str(list_ngay_dt[0])) - x).total_seconds()
        total_time += (y - str_to_dt(khung_gio(z,list_ngay_dt[-1])[0] + ' ' + d_to_str(list_ngay_dt[-1]))).total_seconds()
        for r in list_ngay_dt[1:-1]:
            total_time += khung_gio(z,r)[3]*3600
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

def get_data_new(x,y):
    # Get session and other var
    day_selected = session['day_selected']
    time_begin, time_finish, min_unit, work_hour = khung_gio(session['username'],session['day_selected'])
    week_selected = [dt.datetime.strptime("{}-{}-2017".format(r,day_selected.isocalendar()[1]),"%w-%W-%Y") for r in range(1,7)]
    # Differ day or week
    if y == 'day':
        def condition(r,x):
            return condition_in(r[x.index('start_time')],r[x.index('end_time')],time_begin + ' ' + d_to_str(session['day_selected']),time_finish + ' ' + d_to_str(session['day_selected']))
    elif y == 'week':
        time_begin_week = khung_gio(session['username'],week_selected[0])[0]
        time_finish_week = khung_gio(session['username'],week_selected[-1])[1]
        def condition(r,x):
            return condition_in(r[x.index('start_time')],r[x.index('end_time')],time_begin_week + ' ' + d_to_str(week_selected[0]),time_finish_week + ' ' + d_to_str(week_selected[-1]))
    else:
        pass

    # Get all data and filter people
    result_task = sql("select {} from task where executer = ? or (supporter = ? or supporter like ? or supporter like ? or supporter like ?)".format(','.join(task_field)),[x,x,x + '|%','%|' + x + '|%','%|' + x])
    result_task.sort(key = lambda x : str_to_dt(x[task_field.index('start_time')]))
    result_event = sql("select {} from event where executer = ?".format(','.join(event_field)),[x])

    # Content (after filter time)
    content_base = [r for r in result_event if condition(r,event_field)]
    # content_base = [[r for r in content_base if r[event_field.index('task_id')] == set_r] for set_r in set_keep_order([r[event_field.index('task_id')] for r in content_base])]

    content_base_1 = []
    if [r for r in content_base if r[event_field.index('assigner')] == x and r[event_field.index('supporter')] != x]:
        content_base_1.append([r for r in content_base if r[event_field.index('assigner')] == x and r[event_field.index('supporter')] != x])
    if [r for r in content_base if (r[event_field.index('assigner')] == x and r[event_field.index('supporter')] == x) or r[event_field.index('assigner')] != x]:
        content_base_1.append([r for r in content_base if (r[event_field.index('assigner')] == x and r[event_field.index('supporter')] == x) or r[event_field.index('assigner')] != x])

    content_base = content_base_1
    
    # list_assigner = session['list_assigner'] + [list(sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where username = ?",[x])[0])]
    ds_assigner_rut_gon = [[r, list(sql("select name_n_1,name_n_2 from profile where username = ?",[session['username']])[0])[i]] + [';'.join([r2[i] for r2 in sql("select hash_1,hash_2,hash_3 from profile where username in ({})".format(','.join(["'" + r1 + "'" for r1 in r.split(';')])))]) for i in range(1)] for i,r in enumerate(list(sql("select n_1, n_2 from profile where username = ?",[session['username']])[0]))]

    content_floor = [[r for r in result_task if condition(r,task_field) and r[task_field.index('assigner')] in r1] for r1 in [r2[0] for r2 in session['list_assigner']]] + [[r for r in result_task if condition(r,task_field) and r[task_field.index('assigner')] == x and r[task_field.index('supporter')] == x]]

    while not check_trung_hang(content_floor):
        tach_hang(content_floor)

    # Block
    block_sub = []
    block_base = []
    for r in content_base:
        for r1 in r:
            if y == 'day':
                index = dt_to_index(r1[event_field.index('start_time')],r1[event_field.index('end_time')],time_begin + ' ' + d_to_str(session['day_selected']),time_finish + ' ' + d_to_str(session['day_selected']))
            elif y == 'week':
                index = dt_to_index(r1[event_field.index('start_time')],r1[event_field.index('end_time')],time_begin_week + ' ' + d_to_str(week_selected[0]),time_finish_week + ' ' + d_to_str(week_selected[-1]))
            else:
                pass
            index = [index[0],index[1]+1]
            block_sub.append(index)
        block_base.append(block_sub)
        block_sub = []
    if y == 'day':
        block_floor = [[dt_to_index(r[task_field.index('start_time')],r[task_field.index('end_time')],time_begin + ' ' + d_to_str(session['day_selected']),time_finish + ' ' + d_to_str(session['day_selected'])) for r in m] for m in content_floor]
    elif y == 'week':
        block_floor = [[dt_to_index(r[task_field.index('start_time')],r[task_field.index('end_time')],time_begin_week + ' ' + d_to_str(week_selected[0]),time_finish_week + ' ' + d_to_str(week_selected[-1])) for r in m] for m in content_floor]
    else:
        pass
    block_floor = [[[r[0],r[1]+1] for r in m] for m in block_floor]

    # Other var
    old_task = [[r[task_field.index('task_id')],r[task_field.index('name')],r[task_field.index('percentage')]] for r in result_task if r[task_field.index('percentage')] != '100%']
    return [block_floor, content_floor, block_base, content_base, day_selected, old_task, result_task,week_selected]

def get_data(x,y):
    # Get session and other var
    day_selected = session['day_selected']
    time_begin, time_finish, min_unit, work_hour = khung_gio(session['username'],session['day_selected'])
    list_assignee = sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where n_0 like '%{}%'".format(session['username'])) + sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where n_1 like '%{}%'".format(session['username'])) + sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where n_2 like '%{}%'".format(session['username'])) + sql("select username,mail_name,hash_1,hash_2,hash_3 from profile where username = ?",[session['username']])
    week_selected = [dt.datetime.strptime("{}-{}-2017".format(r,day_selected.isocalendar()[1]),"%w-%W-%Y") for r in range(1,7)]
    # Differ day or week
    if y == 'day':
        def condition(r,x):
            return condition_in(r[x.index('start_time')],r[x.index('end_time')],time_begin_default + ' ' + d_to_str(session['day_selected']),time_finish_default + ' ' + d_to_str(session['day_selected']))
    if y == 'week':
        def condition(r,x):
            return condition_in(r[x.index('start_time')],r[x.index('end_time')],time_begin_default + ' ' + d_to_str(week_selected[0]),time_finish_default + ' ' + d_to_str(week_selected[-1]))
    # Get all data and filter people
    all_task = [list(r) for r in sql("SELECT {} from task where assigner = ? and executer = ? and supporter != '' or assigner = ? and executer != ? order by convert(int,task_id)".format(','.join(task_field)),[x,x,x,x])]

    all_event = [list(r) for r in sql("select {} from event where executer in ({}) order by convert(int,task_id)".format(','.join(event_field),','.join(["'" + r[0] + "'" for r in list_assignee])))]
    # Content and block
    content_task = [r for r in all_task if condition(r,task_field)]
    content_task.sort(key = lambda x : str_to_dt(x[task_field.index('start_time')]))
    content_task = [[r for r in content_task if r[task_field.index('executer')] == set_r] for set_r in set_keep_order([r[task_field.index('executer')] for r in content_task])]
    while not check_trung_hang(content_task):
        tach_hang(content_task)

    # if [r for r in content_task if r[task_field.index('assigner')] == x and r[task_field.index('executer')] == x and r[task_field.index('supporter')] == x]:
    #     insert_test(1)
    #     content_task_1.insert(0,[r for r in content_task if r[task_field.index('assigner')] == x and r[task_field.index('executer')] == x and r[task_field.index('supporter')] == x])
    # content_task = content_task_1
    # content_task_1 = []
    # if [r for r in content_task if r[task_field.index('assigner')] != x and x not in r[task_field.index('supporter')].split('|')]:
    #     content_task_1.append([r for r in content_task if r[task_field.index('assigner')] != x and x not in r[task_field.index('supporter')].split('|')])
    # if [r for r in content_task if r[task_field.index('assigner')] == x]:
    #     content_task_1.append([r for r in content_task if r[task_field.index('assigner')] == x])
    # if [r for r in content_task if r[task_field.index('assigner')] != x and x in r[task_field.index('supporter')].split('|')]:
    #     content_task_1.append([r for r in content_task if r[task_field.index('assigner')] != x and x in r[task_field.index('supporter')].split('|')])
    # content_task = content_task_1

    content_event = [r for r in all_event if condition(r,event_field)]
    content_event = [[r for r in content_event if r[event_field.index('executer')] == set_r] for set_r in set_keep_order([r[event_field.index('executer')] for r in content_event])]
    block_sub = []
    block_task = []
    for r in content_task:
        for r1 in r:
            if y == 'day':
                index = dt_to_index(r1[task_field.index('start_time')],r1[task_field.index('end_time')],time_begin_default + ' ' + d_to_str(session['day_selected']),time_finish_default + ' ' + d_to_str(session['day_selected']))
            elif y == 'week':
                index = dt_to_index_management(r1[task_field.index('start_time')],r1[task_field.index('end_time')],time_begin_default + ' ' + d_to_str(week_selected[0]),time_finish_default + ' ' + d_to_str(week_selected[-1]))
            else:
                pass
            index = [index[0],index[1]+1]
            block_sub.append(index)
        block_task.append(block_sub)
        block_sub = []
        
    block_sub_event = []
    block_event = []
    for r in content_event:
        for r1 in r:
            if y == 'day':
                index = dt_to_index(r1[event_field.index('start_time')],r1[event_field.index('end_time')],time_begin_default + ' ' + d_to_str(session['day_selected']),time_finish_default + ' ' + d_to_str(session['day_selected']))
            elif y == 'week':
                index = dt_to_index_management(r1[event_field.index('start_time')],r1[event_field.index('end_time')],time_begin_default + ' ' + d_to_str(week_selected[0]),time_finish_default + ' ' + d_to_str(week_selected[-1]))
            else:
                pass
            index = [index[0],index[1]+1]
            block_sub_event.append(index)
        block_event.append(block_sub_event)
        block_sub_event = []
    # ?
    for i in range(len(content_event)):
        for j in range(len(content_event[i])):
            if content_event[i][j][7] != None:
                content_event[i][j].append(hash_user(content_event[i][j][7]))
    for i in range(len(content_task)):
        for j in range(len(content_task[i])):
            if content_task[i][j][7] != None:
                content_task[i][j].append(hash_user(content_task[i][j][7]))
    return [day_selected,content_task, block_task, content_event, block_event,week_selected]

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
    list_noti = sql("select top 20 * from noti where (username = ? or username like '%|{}' or username like '%|{}|%' or username like '{}|%') order by noti_id desc".format(x,x,x),[x])
    unread_number = len([r for r in list_noti if r[noti_field.index('read_fake')] == 'N'])
    return [list_assignee,list_noti,unread_number]

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

        ds_cv_theo_cong_ty = [u'Công tác hồ sơ giấy tờ', u'Công tác trình ký', u'Công việc nội bộ phục vụ thu nợ', u'Đánh giá hồ sơ', u'Đào tạo', u'Dự án chiên lược', u'Họp', u'Khảo sát khách hàng', u'Khảo sát TSĐB', u'Phối hợp XLN với các bên khác', u'Phối hợp XLN với các đơn vị nội bộ', u'Tác nghiệp', u'Văn hóa tổ chúc', u'Xây dựng phương án XLN/ Điều chỉnh phương án XLN']

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
        ds_cv_theo_cong_ty = [u'Công tác hồ sơ giấy tờ', u'Công tác trình ký', u'Công việc nội bộ phục vụ thu nợ', u'Đánh giá hồ sơ', u'Đào tạo', u'Dự án chiên lược', u'Họp', u'Khảo sát khách hàng', u'Khảo sát TSĐB', u'Phối hợp XLN với các bên khác', u'Phối hợp XLN với các đơn vị nội bộ', u'Tác nghiệp', u'Văn hóa tổ chúc', u'Xây dựng phương án XLN/ Điều chỉnh phương án XLN']
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

        ds_cv_theo_cong_ty = [u'Công tác hồ sơ giấy tờ', u'Công tác trình ký', u'Công việc nội bộ phục vụ thu nợ', u'Đánh giá hồ sơ', u'Đào tạo', u'Dự án chiên lược', u'Họp', u'Khảo sát khách hàng', u'Khảo sát TSĐB', u'Phối hợp XLN với các bên khác', u'Phối hợp XLN với các đơn vị nội bộ', u'Tác nghiệp', u'Văn hóa tổ chúc', u'Xây dựng phương án XLN/ Điều chỉnh phương án XLN']

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

        ds_cv_theo_cong_ty = [u'Công tác hồ sơ giấy tờ', u'Công tác trình ký', u'Công việc nội bộ phục vụ thu nợ', u'Đánh giá hồ sơ', u'Đào tạo', u'Dự án chiên lược', u'Họp', u'Khảo sát khách hàng', u'Khảo sát TSĐB', u'Phối hợp XLN với các bên khác', u'Phối hợp XLN với các đơn vị nội bộ', u'Tác nghiệp', u'Văn hóa tổ chúc', u'Xây dựng phương án XLN/ Điều chỉnh phương án XLN']

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

