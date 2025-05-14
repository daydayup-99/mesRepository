import configparser
import os
import sys
import threading
from flask import Flask, render_template, request, jsonify
from indexsql import selectJob, selectMachine, getRateFilterTotal, ReadJobSql, getJobErrRate, selectPlno, \
    getPlnoErrRate, SelectAiPass, getErrRate, getLayersql, selectMacRate, \
    exportcsvbyjob, exportallcsv, getAllErrRateSql, getErrJob, getAllMachineNumSql, selectTopNHighRatioJob, \
    selectLowRatioJob, analyzeData, updateAnalyzeData
from datetime import datetime, timedelta, time
import win32file
import win32con
import mainwindow

# sys_dir = os.path.dirname(os.path.realpath(__file__))
sys_dir = os.path.dirname(sys.executable)
lock_file_path = os.path.join(sys_dir, 'my_app.lock')
def check_if_running():
    global lock_file_handle
    # 尝试打开锁文件
    try:
        lock_file_handle = win32file.CreateFile(
            lock_file_path,
            win32con.GENERIC_READ | win32con.GENERIC_WRITE,
            0,  # 不共享
            None,
            win32con.CREATE_ALWAYS,  # 如果文件不存在则创建
            win32con.FILE_ATTRIBUTE_NORMAL,
            None
        )
        # 尝试对文件加锁
        win32file.LockFile(lock_file_handle, 0, 0, win32con.MAXDWORD, win32con.MAXDWORD)
    except Exception as e:
        print("程序已经在运行。", e)
        sys.exit(1)
def release_lock():
    if lock_file_handle:
        win32file.UnlockFile(lock_file_handle, 0, 0, win32con.MAXDWORD, win32con.MAXDWORD)
        win32file.CloseHandle(lock_file_handle)

app = Flask(__name__)

def start_flask_app():
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)

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

@app.route('/report_html')
def report_html():
    return render_template('report.html')

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

@app.route('/DataReport', methods=['POST'])
def AnalyzeDataReport():
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    josn_string = analyzeData(start_time, end_time, start_time_hour, end_time_hour, MacNum)
    return josn_string

@app.route('/UpdateReportEcharts', methods=['POST'])
def AnalyzeUpdateReportEcharts():
    start_time, end_time, start_time_hour, end_time_hour, MacNum, days = getUpdateReportRequestData(request)
    josn_string = updateAnalyzeData(start_time, end_time, start_time_hour, end_time_hour, MacNum, days)
    return josn_string

@app.route('/ExportSql', methods=['POST'])
def exportcsv():
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    result = exportallcsv(start_time, end_time, start_time_hour, end_time_hour, MacNum)
    if result is None:
        data = {'message': '没有可查询的表，请检查时间范围或数据库连接'}
        return jsonify(data), 404
    data = {'message': '数据导出成功'}
    return jsonify(data)

@app.route('/ExportLiaoSql', methods=['POST'])
def exportliaocsv():
    start_time, end_time, start_time_hour, end_time_hour, MacNum = getRequestData(request)
    result = exportcsvbyjob(start_time, end_time, start_time_hour, end_time_hour, MacNum)
    if result is None:
        data = {'message': '没有可查询的表，请检查时间范围或数据库连接'}
        return jsonify(data), 404
    data = {'message': '数据导出成功'}
    return jsonify(data)

@app.route('/GetTopNHighRatioJob',methods=['POST'])
def getTopNHighRatioJob():
    start_time,end_time,start_time_hour,end_time_hour,ratio,n,MacNum = getTopNHighRatioJobRequestData(request)
    jobnameData = selectTopNHighRatioJob(start_time,end_time,start_time_hour,end_time_hour,ratio,n, MacNum)
    response = jsonify(data=jobnameData)
    return response

@app.route('/GetLowRatioJob',methods=['POST'])
def getLowRatioJob():
    start_time,end_time,start_time_hour,end_time_hour,ratio,MacNum = getLowRatioJobRequestData(request)
    jobnameData = selectLowRatioJob(start_time,end_time,start_time_hour,end_time_hour,ratio, MacNum)
    response = jsonify(data=jobnameData)
    return response

def getLowRatioJobRequestData(request):
    start_time_str = request.json['start_time']
    end_time_str = request.json['end_time']
    ratio = request.json['ratio']
    MacNum = request.json['machine_id']
    datetime_format = '%Y-%m-%d %H:%M:%S'
    start_time = datetime.strptime(start_time_str, datetime_format).date()
    end_time = datetime.strptime(end_time_str, datetime_format).date()
    start_time_hour = datetime.strptime(start_time_str, datetime_format).time()
    end_time_hour = datetime.strptime(end_time_str, datetime_format).time()
    return start_time,end_time,start_time_hour,end_time_hour,ratio, MacNum

def getTopNHighRatioJobRequestData(request):
    start_time_str = request.json['start_time']
    end_time_str = request.json['end_time']
    n = request.json['n']
    ratio = request.json['ratio']
    MacNum = request.json['machine_id']
    datetime_format = '%Y-%m-%d %H:%M:%S'
    start_time = datetime.strptime(start_time_str, datetime_format).date()
    end_time = datetime.strptime(end_time_str, datetime_format).date()
    start_time_hour = datetime.strptime(start_time_str, datetime_format).time()
    end_time_hour = datetime.strptime(end_time_str, datetime_format).time()
    return start_time,end_time,start_time_hour,end_time_hour,ratio,n, MacNum

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

def getUpdateReportRequestData (request):
    start_time = request.form['start_time']
    timePeriod = request.form['timePeriod']
    if timePeriod == 'month':
        days = 30
    elif timePeriod == 'day':
        days = 1
    elif timePeriod == 'week':
        days = 7
    end_time = request.form['end_time']
    start_time_hour = request.form['start_time_hour']
    end_time_hour = request.form['end_time_hour']
    MacNum_str = request.form.get('report_macnum')
    if MacNum_str.startswith("'") and MacNum_str.endswith("'"):
        MacNum_str = MacNum_str[1:-1]
    items = MacNum_str.split(',')
    cleaned_items = [item.strip() for item in items]
    MacNum = [item for item in cleaned_items if item]
    date_format = '%Y-%m-%d'
    hour_format = '%H:%M'
    start_time = datetime.strptime(start_time, date_format).date()
    end_time = datetime.strptime(end_time, date_format).date()
    start_time_hour = datetime.strptime(start_time_hour, hour_format).time()
    end_time_hour = datetime.strptime(end_time_hour, hour_format).time()
    return start_time,end_time,start_time_hour,end_time_hour,MacNum, days

if __name__ == '__main__':
    check_if_running()
    try:
        # 启动 Flask 后台
        threading.Thread(target=start_flask_app, daemon=True).start()

        # 启动托盘图标
        threading.Thread(target=mainwindow.minimize_to_tray, daemon=True).start()

        # 在关闭窗口时调用 on_closing
        mainwindow.window.protocol("WM_DELETE_WINDOW", mainwindow.on_closing)

        # 隐藏 Tkinter 窗口
        mainwindow.hide_window()

        # 启动 Tkinter 窗口的事件循�?
        mainwindow.window.mainloop()
    finally:
        release_lock()