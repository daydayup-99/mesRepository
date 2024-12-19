import configparser
import logging
import json
import os
import sys
import threading
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw, ImageTk
from flask import Flask, render_template, Response, request, jsonify
from indexsql import selectJob, selectMachine, getRateFilterTotal, ReadJobSql, getJobErrRate, selectPlno, \
    getPlnoErrRate, SelectAiPass, getErrRate, update_db_connection, getLayersql, selectMacRate, \
    exportcsvbyjob, exportallcsv, getAllErrRateSql, getErrJob, getAllMachineNumSql
from datetime import datetime, timedelta, time
import tkinter as tk
from tkinter import messagebox

app = Flask(__name__)

# sys_dir = os.path.dirname(os.path.realpath(__file__))
sys_dir = os.path.dirname(sys.executable)
back_path = os.path.join(sys_dir, 'background.jpg')

window = tk.Tk()
window.title("Mes App")
window.geometry('400x300')
background_image = Image.open(back_path)
background_image = background_image.resize((400, 300), Image.Resampling.LANCZOS)  # 调整图片大小
background_photo = ImageTk.PhotoImage(background_image)
canvas = tk.Canvas(window, width=400, height=300)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=background_photo, anchor="nw")
status_label = tk.Label(window, text="MES 软件正在运行中",
                        font=("Montserrat", 30, "bold"),  # 设置字体
                        fg="black",  # 字体颜色
                        padx=20, pady=20,  # 内边距
                        bg="white" # 背景颜色
                        )
canvas.create_window(200, 150, window=status_label)

# 托盘图标相关函数
def create_image():
    icon_path = os.path.join(sys_dir, 'icon.png')
    if os.path.exists(icon_path):
        image = Image.open(icon_path)
    else:
        width, height = 64, 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill="black")
    return image

def on_show_window(icon, item):
    window.deiconify()  # 显示窗口
    status_label.config(text="MES 软件正在运行中")

def start_flask_app():
    app.run(threaded=True, use_reloader=False)

def hide_window():
    window.withdraw()  # 最小化窗口

def close_application():
    global icon
    if icon:
        icon.stop()  # 停止托盘图标
    sys.exit()  # 退出程序

# 启动 Flask 应用并最小化到系统托盘
def minimize_to_tray():
    icon = Icon("test", create_image(), menu=Menu(MenuItem("Show Window", on_show_window)))
    icon.run()

def on_closing():
    result = messagebox.askquestion("退出确认", "是否最小化到托盘？", icon='warning')
    if result == 'yes':
        hide_window()  # 最小化
    else:
        window.quit()  # 退出

config = configparser.ConfigParser()
# config_dir = os.path.dirname(os.path.realpath(__file__))
config_dir = os.path.dirname(sys.executable)
config_dir = os.path.join(config_dir, 'config.ini')
config.read(config_dir)
@app.route('/static')
def statics():
    export_time = config['log']['autoTime']
    is_export = config.getboolean('log', 'autoStatistic')
    return render_template('static.html', export_time=export_time, is_export=is_export)

@app.route('/mes')
def mes():
    return render_template('mes.html')

@app.route('/index')
def routs():
    reflash_time = config['log']['reflashTime']
    return render_template('index.html', reflash_time=reflash_time)

@app.route('/MacAi', methods=['GET'])
def  selectMacAi():
    json_data = SelectAiPass()
    return  json_data
    # 获取表单数据

@app.route('/MacErrRate')
def  selectMacErr():
    json_data = getErrRate()
    return json_data

@app.route('/MacErrJob')
def  selectMacErrJob():
    json_data = getErrJob()
    return json_data

@app.route('/UpdateDatabase',methods=['POST'])
def updateData():
    process = request.form['process']
    # update_db_connection(process)
    return "Data updated successfully"

@app.route('/selectJob',methods=['POST'])
def getJobName():
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    jobnameData = selectJob(start_time, end_time,start_time_hour,end_time_hour, MacNum)
    response = jsonify(data = jobnameData)
    return  response


@app.route('/selectPlno',methods=['POST'])
def getPlnoName():
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    jobName = request.form['jobNum']
    if jobName != "":
        jobnameData = selectPlno(start_time,end_time,start_time_hour,end_time_hour,MacNum,jobName)
    else:
        jobnameData = []

    response = jsonify(data = jobnameData)
    return response

@app.route('/getdate')
def getdate():
    current_date = datetime.now()
    # 创建当前日期的副本并减去7天
    pre_date = current_date - timedelta(days=7)
    # 格式化日期为 YYYY-MM-DD HH:MM:SS字符串
    pre_datetime = datetime.combine(pre_date, time.min)
    current_datetime = datetime.combine(current_date, time.max)
    formatted_start_date = pre_datetime.strftime('%Y-%m-%d %H:%M')
    formatted_end_date = current_datetime.strftime('%Y-%m-%d %H:%M')
    date_range = [formatted_start_date, formatted_end_date]
    response = jsonify(data=date_range)
    return response

@app.route('/getAllMachineNum')
def getAllMachineNum():
    avi_count = getAllMachineNumSql()  # 从数据库或其他地方获取动态数据
    response = {"avi_count": avi_count}
    return jsonify(response)

# 初始时获取机台号
@app.route('/getMacineData')
def getMacineName():
    MachineData = selectMachine()
    response = jsonify(data=MachineData)
    return response

#获取真点率,和 最大点数
@app.route('/getTrueRate',methods=['POST'])
def getMacTrueRate():
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    # maxnum = request.form['MaxNum']
    # selectMacRate(MacNum,maxnum)
    selectMacRate(MacNum)
    data = {'message': 'True Rate get successfully'}
    return jsonify(data)

@app.route('/staticSubmit', methods=['POST'])
def handle_ajax_request():
    # 获取表单数据
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    # jobName = request.form['jobNum']
    # PLNum = request.form['PLNum']
    # ai_version = request.form['ai_version']
    # josn_string = getRateFilterTotal(ai_version, start_time, end_time, MacNum, jobName, PLNum)
    josn_string = getRateFilterTotal(start_time, end_time,start_time_hour, end_time_hour, MacNum)
    return josn_string

@app.route('/LiaohualvSubmit', methods=['POST'])
def  liaoselectsql():
    # 获取表单数据
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    josn_string = ReadJobSql(start_time, end_time,start_time_hour, end_time_hour, MacNum)
    return josn_string

@app.route('/LiaohuaErrRate', methods=['POST'])
def  liaoselectRatesql():
    # 获取表单数据
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    jobName = request.form['jobNum']
    if jobName !="":
        josn_string = getJobErrRate(start_time, end_time, MacNum, jobName)
    else:
        josn_string ={}
    return josn_string

@app.route('/PlnoErrRate', methods=['POST'])
def  PlnoselectRatesql():
    # 获取表单数据
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    jobName = request.form['jobNum']
    PLNum = request.form['PLNum']
    if jobName !="" and PLNum!="":
        josn_string = getPlnoErrRate(start_time, end_time, MacNum, jobName,PLNum)
    else:
        josn_string ={}
    return josn_string

@app.route('/AllErrRate', methods=['POST'])
def AllselectErrRatesql():
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    josn_string = getAllErrRateSql(start_time, end_time, MacNum)
    return josn_string

@app.route('/ReadLayerSql', methods=['POST'])
def ReadLayersql():
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    jobName = request.form['jobNum']
    josn_string = getLayersql(start_time, end_time, MacNum, jobName)
    return josn_string

@app.route('/ExportSql', methods=['POST'])
def exportcsv():
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    # maxnum =request.form['MaxNum']
    exportallcsv(start_time, end_time, start_time_hour, end_time_hour, MacNum)
    data = {'message': 'Data exported successfully'}
    return jsonify(data)

@app.route('/ExportLiaoSql', methods=['POST'])
def exportliaocsv():
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    # maxnum =request.form['MaxNum']
    exportcsvbyjob(start_time, end_time, start_time_hour, end_time_hour, MacNum)
    dataJob = {'message': 'dataJob exported successfully'}
    return jsonify(dataJob)

def getRequestData (request):
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    start_time_hour = request.form['start_time_hour']
    end_time_hour = request.form['end_time_hour']
    # print(request.form)
    MacNum = request.form.getlist('MacNum[]')
    date_format = '%Y-%m-%d'
    hour_format = '%H:%M'
    start_time = datetime.strptime(start_time, date_format).date()
    end_time = datetime.strptime(end_time, date_format).date()
    start_time_hour = datetime.strptime(start_time_hour, hour_format).time()
    end_time_hour = datetime.strptime(end_time_hour, hour_format).time()
    return start_time,end_time,start_time_hour,end_time_hour,MacNum

@app.errorhandler(Exception)
def handle_error(error):
    logging.error(f"An unexpected error occurred: {str(error)}")
    return jsonify(message="An unexpected error occurred!"), 500

if __name__ == '__main__':
    # 启动 Flask 后台
    threading.Thread(target=start_flask_app, daemon=True).start()

    # 启动托盘图标
    threading.Thread(target=minimize_to_tray, daemon=True).start()

    # 在关闭窗口时调用 on_closing
    window.protocol("WM_DELETE_WINDOW", on_closing)

    # 隐藏 Tkinter 窗口
    hide_window()

    # 启动 Tkinter 窗口的事件循环
    window.mainloop()
    # app.run()
