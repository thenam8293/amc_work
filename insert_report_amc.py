# -*- coding: utf8 -*-

from __future__ import division
import pypyodbc
from datetime import datetime, timedelta
import os
import pypyodbc
import datetime as dt
import collections
import random
from operator import itemgetter
import xlrd
import hashlib
import time

def str_to_dt(x):
    try:
        return dt.datetime.strptime(x,'%H:%M %d/%m/%Y')
    except:
        return dt.datetime.strptime(x,'%d/%m/%Y')

def sql(query,var=''):
    connection = pypyodbc.connect('Driver={SQL Server};Server=10.62.24.161\SQLEXPRESS;Database=web_cv_amc;uid=aos;pwd=aos159753')
    cursor = connection.cursor()
    cursor.execute(query,var)
    if query.lower()[:6] == 'select':
        x = cursor.fetchall()
        cursor.close()
        return x
    else:
        cursor.commit()
        cursor.close()

def d_to_str(x):
    return '{}/{}/{}'.format(str(x)[8:10],str(x)[5:7],str(x)[:4])

def khung_gio(x,y):
    ## Return time begin, time finish, min unit time, work hour per day
    # x : user
    # y : day
    process_info.sort(key = lambda x : int(x[sub_process_field.index('sub_process_id')].split('_')[-1]))
    list_khung_gio = [list(r) for r in sql("select username,time_begin,time_finish,min_unit,time_change from setting_log where username = ?",[x])]
    list_khung_gio.sort(key = lambda x : str_to_dt(x[setting_log_field.index('time_change')]))
    list_khung_gio = [r for r in list_khung_gio if str_to_dt(r[setting_log_field.index('time_change')]) <= y]
    list_khung_gio = list_khung_gio[-1]
    work_hour = (int(list_khung_gio[setting_log_field.index('time_finish')][:2]) * 60 + int(list_khung_gio[setting_log_field.index('time_finish')][-2:]) - int(list_khung_gio[setting_log_field.index('time_begin')][:2]) * 60 - int(list_khung_gio[setting_log_field.index('time_begin')][-2:]))/60
    return [list_khung_gio[setting_log_field.index('time_begin')],list_khung_gio[setting_log_field.index('time_finish')],list_khung_gio[setting_log_field.index('min_unit')],work_hour]

def time_dif(x,y,z):
    ## Return time different (second) between start time and end time
    # x : start time (datetime)
    # y : end time (datetime)
    # z : user
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

special_day = dt.datetime(1993,9,19)

start_date_demo = dt.datetime(2017,8,3)

setting_log_field = ['username','time_begin','time_finish','min_unit','time_change']

task_field = ['task_id', 'name', 'type', 'type_strategy', 'content', 'status', 'percentage', 'executer', 'assigner', 'supporter', 'executer_name', 'assigner_name','supporter_name','customer','disable', 'start_time','end_time','last_update','rating','department','type_department']

event_field = ['task_id','event_id', 'name', 'type', 'type_strategy', 'content', 'status', 'percentage', 'executer', 'assigner','supporter', 'executer_name', 'assigner_name','supporter_name','customer','disable','start_time','end_time','complete','department','type_department']

report_field = ['username','so_gio_lam_viec','so_cong_viec','ds_10_ngay_gan_nhat','ds_cong_viec_trong_10_ngay','so_ngay_lam_viec','phan_bo_cv_theo_trung_tam','phan_bo_cv_theo_cong_ty','phan_bo_cv_theo_toan_hang','ds_cv_theo_trung_tam','ds_cv_theo_cong_ty','ds_cv_theo_toan_hang','ty_le_tuan_thu_bao_cao','ty_le_qua_han']

list_ngay_nghi = [dt.date(2017,5,1),dt.date(2017,5,2),dt.date(2017,4,6)]

def calculate(x):
    # x : user hoac trung tam, phong
    #1 So gio lam viec
    event_data = sql("select {} from event where executer = ?".format(','.join(event_field)),[x])
    so_gio_lam_viec_raw = sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),x) for r in event_data])
    so_gio_lam_viec = str(int(round(so_gio_lam_viec_raw/3600,0)))

    #2 So cong viec
    task_data = sql("select {} from task where executer = ? or (supporter = ? or supporter like '%|{}' or supporter like '%|{}|%' or supporter like '{}|%')".format(','.join(task_field),x,x,x),[x,x])
    so_cong_viec = len(task_data)

    #3,4 So cong viec theo 10 ngay gan nhat, 10 ngay gan nhat (dang string)
    ds_10_ngay_gan_nhat = [dt.datetime.now() - dt.timedelta(days=i) for i in range(11,-1,-1)] #?
    ds_10_ngay_gan_nhat = [r for r in ds_10_ngay_gan_nhat if r > start_date_demo and r.weekday() != 6 and r.date() not in list_ngay_nghi]
    ds_cong_viec_trong_10_ngay = [str(len([r for r in task_data if str_to_dt(r[task_field.index('start_time')]).date() == r1.date()])) for r1 in ds_10_ngay_gan_nhat]
    ds_10_ngay_gan_nhat = [str(r.date())[5:] for r in ds_10_ngay_gan_nhat]

    #5 So ngay lam viec
    ds_ngay_lam_viec = [dt.datetime.now() - dt.timedelta(days=r) for r in range(int(str(dt.datetime.now() - start_date_demo).split(" ")[0]))]
    ds_ngay_lam_viec = [r for r in ds_ngay_lam_viec if r.weekday() != 6 and r.date() not in list_ngay_nghi]
    so_ngay_lam_viec = len(ds_ngay_lam_viec)

    #6,7,8,9,10,11 Phan bo cong viec theo trung tam, theo cong ty, theo toan hang, ds cong viec theo trung tam, theo cong ty, theo toan hang
    try:
        department = sql("select phong from profile where username = ?",[x])[0][0]
    except:
        return ['']*10
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

    #13 Ty le qua han
    if so_cong_viec:
        ty_le_qua_han = str(round(len([r for r in task_data if r[task_field.index("status")] != 'Y'])/so_cong_viec*100,2)) + '|' + str(100 - round(len([r for r in task_data if r[task_field.index("status")] != 'Y'])/so_cong_viec*100,2))
    else:
        ty_le_qua_han = ''

    ds_10_ngay_gan_nhat = '|'.join(ds_10_ngay_gan_nhat)
    ds_cong_viec_trong_10_ngay = '|'.join(ds_cong_viec_trong_10_ngay)
    phan_bo_cv_theo_trung_tam = '|'.join(phan_bo_cv_theo_trung_tam)
    phan_bo_cv_theo_cong_ty = '|'.join(phan_bo_cv_theo_cong_ty)
    phan_bo_cv_theo_toan_hang = '|'.join(phan_bo_cv_theo_toan_hang)
    ds_cv_theo_trung_tam = '|'.join(ds_cv_theo_trung_tam)
    ds_cv_theo_cong_ty = '|'.join(ds_cv_theo_cong_ty)
    ds_cv_theo_toan_hang = '|'.join(ds_cv_theo_toan_hang)
    
    return [so_gio_lam_viec,so_cong_viec,ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay,so_ngay_lam_viec,phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam,ds_cv_theo_cong_ty,ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao,ty_le_qua_han]

def calculate_cong_ty():
    #1 So gio lam viec
    event_data = sql("select {} from event".format(','.join(event_field)))
    so_gio_lam_viec_raw = sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in event_data])
    so_gio_lam_viec = str(int(round(so_gio_lam_viec_raw/3600,0)))

    #2 So cong viec
    task_data = sql("select {} from task".format(','.join(task_field)))
    so_cong_viec = len(task_data)

    #3,4 So cong viec theo 10 ngay gan nhat, 10 ngay gan nhat (dang string)
    ds_10_ngay_gan_nhat = [dt.datetime.now() - dt.timedelta(days=i) for i in range(11,-1,-1)] #?
    ds_10_ngay_gan_nhat = [r for r in ds_10_ngay_gan_nhat if r > start_date_demo and r.weekday() != 6 and r.date() not in list_ngay_nghi]
    ds_cong_viec_trong_10_ngay = [str(len([r for r in task_data if str_to_dt(r[task_field.index('start_time')]).date() == r1.date()])) for r1 in ds_10_ngay_gan_nhat]
    ds_10_ngay_gan_nhat = [str(r.date())[5:] for r in ds_10_ngay_gan_nhat]

    #5 So ngay lam viec
    ds_ngay_lam_viec = [dt.datetime.now() - dt.timedelta(days=r) for r in range(int(str(dt.datetime.now() - start_date_demo).split(" ")[0]))]
    ds_ngay_lam_viec = [r for r in ds_ngay_lam_viec if r.weekday() != 6 and r.date() not in list_ngay_nghi]
    so_ngay_lam_viec = len(ds_ngay_lam_viec)

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
    ty_le_tuan_thu_bao_cao = str(round(so_gio_lam_viec_raw/3600/tong_tg_lam_viec_quy_dinh*100,2))

    #13 Ty le qua han
    if so_cong_viec:
        ty_le_qua_han = str(round(len([r for r in task_data if r[task_field.index("status")] != 'Y'])/so_cong_viec*100,2)) + '|' + str(100 - round(len([r for r in task_data if r[task_field.index("status")] != 'Y'])/so_cong_viec*100,2))
    else:
        ty_le_qua_han = ''

    ds_10_ngay_gan_nhat = '|'.join(ds_10_ngay_gan_nhat)
    ds_cong_viec_trong_10_ngay = '|'.join(ds_cong_viec_trong_10_ngay)
    phan_bo_cv_theo_trung_tam = '|'.join(phan_bo_cv_theo_trung_tam)
    phan_bo_cv_theo_cong_ty = '|'.join(phan_bo_cv_theo_cong_ty)
    phan_bo_cv_theo_toan_hang = '|'.join(phan_bo_cv_theo_toan_hang)
    ds_cv_theo_trung_tam = '|'.join(ds_cv_theo_trung_tam)
    ds_cv_theo_cong_ty = '|'.join(ds_cv_theo_cong_ty)
    ds_cv_theo_toan_hang = '|'.join(ds_cv_theo_toan_hang)
    
    return [so_gio_lam_viec,so_cong_viec,ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay,so_ngay_lam_viec,phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam,ds_cv_theo_cong_ty,ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao,ty_le_qua_han]

def calculate_trung_tam(x):
    # x : trung tam
    #1 So gio lam viec
    event_data = sql("select {} from event where department = ?".format(','.join(event_field)),[x])
    so_gio_lam_viec_raw = sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in event_data])
    so_gio_lam_viec = str(int(round(so_gio_lam_viec_raw/3600,0)))

    #2 So cong viec
    task_data = sql("select {} from task where department = ?".format(','.join(task_field)),[x])
    so_cong_viec = len(task_data)

    #3,4 So cong viec theo 10 ngay gan nhat, 10 ngay gan nhat (dang string)
    ds_10_ngay_gan_nhat = [dt.datetime.now() - dt.timedelta(days=i) for i in range(11,-1,-1)] #?
    ds_10_ngay_gan_nhat = [r for r in ds_10_ngay_gan_nhat if r > start_date_demo and r.weekday() != 6 and r.date() not in list_ngay_nghi]
    ds_cong_viec_trong_10_ngay = [str(len([r for r in task_data if str_to_dt(r[task_field.index('start_time')]).date() == r1.date()])) for r1 in ds_10_ngay_gan_nhat]
    ds_10_ngay_gan_nhat = [str(r.date())[5:] for r in ds_10_ngay_gan_nhat]

    #5 So ngay lam viec
    ds_ngay_lam_viec = [dt.datetime.now() - dt.timedelta(days=r) for r in range(int(str(dt.datetime.now() - start_date_demo).split(" ")[0]))]
    ds_ngay_lam_viec = [r for r in ds_ngay_lam_viec if r.weekday() != 6 and r.date() not in list_ngay_nghi]
    so_ngay_lam_viec = len(ds_ngay_lam_viec)

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
    ty_le_tuan_thu_bao_cao = str(round(so_gio_lam_viec_raw/3600/tong_tg_lam_viec_quy_dinh*100,2))

    #13 Ty le qua han
    if so_cong_viec:
        ty_le_qua_han = str(round(len([r for r in task_data if r[task_field.index("status")] != 'Y'])/so_cong_viec*100,2)) + '|' + str(100 - round(len([r for r in task_data if r[task_field.index("status")] != 'Y'])/so_cong_viec*100,2))
    else:
        ty_le_qua_han = ''

    ds_10_ngay_gan_nhat = '|'.join(ds_10_ngay_gan_nhat)
    ds_cong_viec_trong_10_ngay = '|'.join(ds_cong_viec_trong_10_ngay)
    phan_bo_cv_theo_trung_tam = '|'.join(phan_bo_cv_theo_trung_tam)
    phan_bo_cv_theo_cong_ty = '|'.join(phan_bo_cv_theo_cong_ty)
    phan_bo_cv_theo_toan_hang = '|'.join(phan_bo_cv_theo_toan_hang)
    ds_cv_theo_trung_tam = '|'.join(ds_cv_theo_trung_tam)
    ds_cv_theo_cong_ty = '|'.join(ds_cv_theo_cong_ty)
    ds_cv_theo_toan_hang = '|'.join(ds_cv_theo_toan_hang)
    
    return [so_gio_lam_viec,so_cong_viec,ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay,so_ngay_lam_viec,phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam,ds_cv_theo_cong_ty,ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao,ty_le_qua_han]

def calculate_bo_phan(x,y):
    # x : trung tam
    # y : bo phan
    ds_user_trg_bo_phan = [r[0] for r in sql("select username from profile where phong = ? and bophan = ?",[x,y])]
    #1 So gio lam viec
    event_data = sql("select {} from event where executer in ({})".format(','.join(event_field),','.join(["'" + r + "'" for r in ds_user_trg_bo_phan])))
    so_gio_lam_viec_raw = sum([time_dif(str_to_dt(r[event_field.index('start_time')]),str_to_dt(r[event_field.index('end_time')]),r[event_field.index('executer')]) for r in event_data])
    so_gio_lam_viec = str(int(round(so_gio_lam_viec_raw/3600,0)))

    #2 So cong viec
    task_data = sql("select {} from task where executer in ({})".format(','.join(task_field),','.join(["'" + r + "'" for r in ds_user_trg_bo_phan])))
    so_cong_viec = len(task_data)

    #3,4 So cong viec theo 10 ngay gan nhat, 10 ngay gan nhat (dang string)
    ds_10_ngay_gan_nhat = [dt.datetime.now() - dt.timedelta(days=i) for i in range(11,-1,-1)] #?
    ds_10_ngay_gan_nhat = [r for r in ds_10_ngay_gan_nhat if r > start_date_demo and r.weekday() != 6 and r.date() not in list_ngay_nghi]
    ds_cong_viec_trong_10_ngay = [str(len([r for r in task_data if str_to_dt(r[task_field.index('start_time')]).date() == r1.date()])) for r1 in ds_10_ngay_gan_nhat]
    ds_10_ngay_gan_nhat = [str(r.date())[5:] for r in ds_10_ngay_gan_nhat]

    #5 So ngay lam viec
    ds_ngay_lam_viec = [dt.datetime.now() - dt.timedelta(days=r) for r in range(int(str(dt.datetime.now() - start_date_demo).split(" ")[0]))]
    ds_ngay_lam_viec = [r for r in ds_ngay_lam_viec if r.weekday() != 6 and r.date() not in list_ngay_nghi]
    so_ngay_lam_viec = len(ds_ngay_lam_viec)

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
    ty_le_tuan_thu_bao_cao = str(round(so_gio_lam_viec_raw/3600/tong_tg_lam_viec_quy_dinh*100,2))

    #13 Ty le qua han
    if so_cong_viec:
        ty_le_qua_han = str(round(len([r for r in task_data if r[task_field.index("status")] != 'Y'])/so_cong_viec*100,2)) + '|' + str(100 - round(len([r for r in task_data if r[task_field.index("status")] != 'Y'])/so_cong_viec*100,2))
    else:
        ty_le_qua_han = ''

    ds_10_ngay_gan_nhat = '|'.join(ds_10_ngay_gan_nhat)
    ds_cong_viec_trong_10_ngay = '|'.join(ds_cong_viec_trong_10_ngay)
    phan_bo_cv_theo_trung_tam = '|'.join(phan_bo_cv_theo_trung_tam)
    phan_bo_cv_theo_cong_ty = '|'.join(phan_bo_cv_theo_cong_ty)
    phan_bo_cv_theo_toan_hang = '|'.join(phan_bo_cv_theo_toan_hang)
    ds_cv_theo_trung_tam = '|'.join(ds_cv_theo_trung_tam)
    ds_cv_theo_cong_ty = '|'.join(ds_cv_theo_cong_ty)
    ds_cv_theo_toan_hang = '|'.join(ds_cv_theo_toan_hang)
    
    return [so_gio_lam_viec,so_cong_viec,ds_10_ngay_gan_nhat,ds_cong_viec_trong_10_ngay,so_ngay_lam_viec,phan_bo_cv_theo_trung_tam,phan_bo_cv_theo_cong_ty,phan_bo_cv_theo_toan_hang,ds_cv_theo_trung_tam,ds_cv_theo_cong_ty,ds_cv_theo_toan_hang,ty_le_tuan_thu_bao_cao,ty_le_qua_han]
count_update = 0;
print "INSERT REPORT"
while True:
    count_time_start = time.time()

    ds_user_trg_bang = [r[0] for r in sql("select username from report")]
    for username in [r1[0] for r1 in sql("select username from profile")]:
        if username in ds_user_trg_bang:
            data = calculate(username) + [username]
            sql("update report set {} where username = ?".format(','.join([r + ' = ?' for r in report_field[1:]])),data)
        else:
            data = [username] + calculate(username)
            sql("insert into report({}) values({})".format(','.join(report_field),','.join(['?']*len(report_field))),data)

    if 'AMC' in ds_user_trg_bang:
        data = calculate_cong_ty() + ['AMC']
        sql("update report set {} where username = ?".format(','.join([r + ' = ?' for r in report_field[1:]])),data)
    else:
        data = ['AMC'] + calculate_cong_ty()
        sql("insert into report({}) values({})".format(','.join(report_field),','.join(['?']*len(report_field))),data)

    for phong in [r1[0] for r1 in sql("select distinct phong from profile")]:
        if phong in ds_user_trg_bang:
            data = calculate_trung_tam(phong) + [phong]
            sql("update report set {} where username = ?".format(','.join([r + ' = ?' for r in report_field[1:]])),data)
        else:
            data = [phong] + calculate_trung_tam(phong)
            sql("insert into report({}) values({})".format(','.join(report_field),','.join(['?']*len(report_field))),data)

    for phong_bophan in sql("select distinct phong,bophan from profile where bophan != ''"):
        bophan_theo_phong = phong_bophan[0] + '|' + phong_bophan[1]
        if bophan_theo_phong in ds_user_trg_bang:
            data = calculate_bo_phan(phong_bophan[0],phong_bophan[1]) + [bophan_theo_phong]
            sql("update report set {} where username = ?".format(','.join([r + ' = ?' for r in report_field[1:]])),data)
        else:
            data = [bophan_theo_phong] + calculate_bo_phan(phong_bophan[0],phong_bophan[1])
            sql("insert into report({}) values({})".format(','.join(report_field),','.join(['?']*len(report_field))),data)
    count_update += 1
    print u"Update lần thứ {} vào lúc {}".format(str(count_update),dt.datetime.now())
    print "-------------------------------------"
    print u"--- Hết {} giây ---".format(time.time() - count_time_start)
    print "-------------------------------------"
    time.sleep(30)

# x : user hoac trung tam, phong
#1 So gio lam viec

# x = 'admin1'
# y = 'admin1'
# ds_user_trg_bo_phan = [r[0] for r in sql("select username from profile where phong = ? and bophan = ?",[x,y])]
# #1 So gio lam viec
# print ds_user_trg_bo_phan
# print  "select {} from event where executer in ({})".format(','.join(event_field),','.join(ds_user_trg_bo_phan))
# event_data = sql("select {} from event where executer in ({})".format(','.join(event_field),','.join(["'" + r + "'" for r in ds_user_trg_bo_phan])))

# sql("drop table report")
# sql("create table report (username nvarchar(max),so_gio_lam_viec nvarchar(max),so_cong_viec nvarchar(max),ds_10_ngay_gan_nhat nvarchar(max),ds_cong_viec_trong_10_ngay nvarchar(max),so_ngay_lam_viec nvarchar(max),phan_bo_cv_theo_trung_tam nvarchar(max),phan_bo_cv_theo_cong_ty nvarchar(max),phan_bo_cv_theo_toan_hang nvarchar(max),ds_cv_theo_trung_tam nvarchar(max),ds_cv_theo_cong_ty nvarchar(max),ds_cv_theo_toan_hang nvarchar(max),ty_le_tuan_thu_bao_cao nvarchar(max),ty_le_qua_han  nvarchar(max))")
