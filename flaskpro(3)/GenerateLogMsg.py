# -*- coding: utf-8 -*-
# @Time : 2021/8/17 11:00
# @Author : Maoger

import os
import time
# from PyQt5.QtCore import QTime, QDateTime, QDate, Qt, QCalendar
from PyQt5.QtCore import QTime, QDateTime, QDate, Qt
import random

print(QTime.currentTime().toString("hh:mm:ss"))
print(QDate.currentDate().toString("yyyy_M_dd"))
logTxt = QDate.currentDate().toString("yyyy_M_d") + '.txt'


msg_noise = False
frequency = 5
noise_pn = "TC49863-6B01H"
noise_pn1 = "TC49863-6B01R--25"
noise_pn2 = "TC49863-6B01H--25"
noise_pn3 = "TC49863-6B01T--25"

rootPath = r'F:\0808深圳景旺6#验孔误报资料'

only_FM = False  # 只生成有峰明的资料

for dir in os.listdir(rootPath):
    if dir.split("\\")[-1] == "car":
    # if dir.split("\\")[-1] == "car":
        carPath = os.path.join(rootPath, dir)
        # carPath = r"E:\20211020标准板测试资料\car-跳镀"
    elif dir.split("\\")[-1] == "avilog":
        aviLog = os.path.join(rootPath, dir)
# car 路径  D:\ShareDir\zw\0826bm\car
# carPath = r"E:\20211022星联\car"
# aviLog = r"E:\20211022星联\avilog"
aviLog = os.path.join(rootPath, "avilog")
if not os.path.exists(aviLog):
    os.mkdir(aviLog)
logTxtPath = os.path.join(aviLog, logTxt)

pn_select = ""
pl_select = ""
pcb_select = []

n = 0
Start_log_time = QTime.currentTime()
with open(logTxtPath, "w+", encoding="gbk") as obj_writer:
    for Pn in os.listdir(carPath):

        # filter
        if Pn != pn_select and pn_select != "":
            continue

        if only_FM:
            jobPath = os.path.join(rootPath, "job", Pn)
            if not os.path.exists(jobPath) or not os.path.isdir(jobPath):
                continue
        print(Pn)
        PnPath = os.path.join(carPath, Pn)
        if not os.path.isdir(PnPath):
            continue

        Pn_list = os.listdir(PnPath)
        # Pn_list.sort(key=lambda x: int(os.path.basename(x).split('.')[0][1:]))  # 路径排序
        for pl in Pn_list:
            # if pl[-2:] != "_1":
            if pl != pl_select and pl_select != "":
                 continue
            print(pl)
            _b_tPath = os.path.join(PnPath, pl)
            if not (os.path.isdir(_b_tPath)):
                continue

            res_list = []
            for _b_t in sorted(os.listdir(_b_tPath)):
                if not _b_t.split("_")[0].isdigit():
                    continue
                res_list.append(int(_b_t.split("_")[0]))
            pcb_num_list = sorted(set(res_list))

            # for _b_t in sorted(os.listdir(_b_tPath)):
            for pcb_num in pcb_num_list:

                # if pcb_num != pcb_select and pcb_select > 0:
                if pcb_num not in pcb_select and len(pcb_select) != 0:
                    continue
                # _b_t_list01 = os.listdir(_b_tPath)
                # if _b_t.split('_')[-1] == "ai" or _b_t.split("_")[-1].lower() not in ["b", "t"]:
                #     continue
                # int(_b_t.split("_")[0])
                Start_log_time = Start_log_time.addSecs(1)
                avi_time = Start_log_time.toString("hh:mm:ss")
                # idx = _b_t.split("_")[0]
                # side = _b_t.split("_")[-1].upper()
                t_size = "T"
                b_size = "B"
                # n += 1
                # obj_writer.write(f"{time_current} {Pn} admin {pl}:{pcb_num}:{side} 1\n")
                obj_writer.write(f"{avi_time} {Pn} admin {pl}:{pcb_num}:{t_size} 1\n")

                obj_writer.write(f"{avi_time} {Pn} admin {pl}:{pcb_num}:{b_size} 1\n")
                # if(pl.__contains__('_1')):
                #     obj_writer.write(f"{time_current} {Pn} admin {pl.replace('_1','_2')}:{idx}:{side} 1\n")
                # if msg_noise and n % frequency == 0:
                #     obj_writer.write(f"{time_current} {noise_pn} admin {pl}:{random.randint(1,10)}:{side} 1\n")
                #     obj_writer.write(f"{time_current} {noise_pn1} admin {pl}:{random.randint(1,10)}:{side} 1\n")
                #     obj_writer.write(f"{time_current} {noise_pn2} admin {pl}:{random.randint(1,10)}:{side} 1\n")
                #     obj_writer.write(f"{time_current} {noise_pn3} admin {pl}:{random.randint(1,10)}:{side} 1\n")
