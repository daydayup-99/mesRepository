import configparser
import json
import os
import sys

from flask import Flask, render_template, Response, request, jsonify
from indexsql import selectJob, selectMachine, getRateFilterTotal, ReadJobSql, getJobErrRate, selectPlno, \
    getPlnoErrRate, SelectAiPass, getErrRate, update_db_connection, getLayersql, selectMacRate, \
    exportcsvbyjob, exportallcsv, getAllErrRateSql, getErrJob
from datetime import datetime, timedelta, time

app = Flask(__name__)


@app.route('/static')
def statics():
    config = configparser.ConfigParser()
    config_dir = os.path.dirname(os.path.realpath(__file__))
    # config_dir = os.path.dirname(sys.executable)
    config_dir = os.path.join(config_dir, 'config.ini')
    config.read(config_dir)
    export_time = config['log']['autoTime']
    is_export = config.getboolean('log', 'autoStatistic')
    return render_template('static.html', export_time=export_time, is_export=is_export)

@app.route('/mes')
def mes():
    return render_template('mes.html')

@app.route('/index')
def routs():
    return render_template('index.html')


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
    return  response




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

if __name__ == '__main__':
    app.run()
