import random
import sys
import pandas as pd
from sqlalchemy import create_engine, inspect, Column, Integer, String, Table, func, not_, Float, and_, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta
from decimal import Decimal
import json
import os
from collections import defaultdict
import configparser
global MacTrueRate

surface_dict = {'1': '金',
                '2': '铜',
                '3': 'OSP',
                '4': '化银',
                '5': '沉锡',
                '6': '喷锡'}

config = configparser.ConfigParser()
# config_dir = os.path.dirname(os.path.realpath(__file__))
config_dir = os.path.dirname(sys.executable)
config_dir = os.path.join(config_dir, 'config.ini')
config.read(config_dir)
t_ratio = float(config['log']['t_ratio'])
user = config['database']['User']
password = config['database']['Password']
host = config['database']['Host']
port = config['database']['Port']
dbname = config['database']['DbName']
charset = config['database']['Charset']
smallBatch = config['log']['smallBatch']
maxTrueNum = int(config['log']['maxTrueNum'])
allFilterRate = float(config['log']['allFilterRate'])
isOptimizeFRate = int(config['log']['isOptimizeFRate'])

if allFilterRate < 0:
    allFilterRate = 0.0
if maxTrueNum < 0:
    maxTrueNum = 1000000000   #sql识别不了inf
# start_time = config['log']['start_time']
# end_time = config['log']['end_time']
if t_ratio == 0.0:
    t_ratio = 0.3

true_point_filters = []
if 'export' in config and 'true_point_types' in config['export']:
    types_str = config['export']['true_point_types']
    if types_str:
        true_point_filters = types_str.split(',')
# DATABASE_URL = "mysql+pymysql://root:YMZ123@127.0.0.1/avi?charset=utf8"
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}?charset={charset}"
print("Database URL:", DATABASE_URL)
try:
    engine = create_engine(
            DATABASE_URL,
            pool_size=10,
            pool_recycle=1600,
            pool_pre_ping=True,
            pool_use_lifo=True,
            echo_pool=True,
            max_overflow=5
    )
except SQLAlchemyError as e:
    print("Error connecting to database:", str(e))

Base = declarative_base()

Session = sessionmaker(bind=engine)

curent_date = datetime.now()
# curent_date = datetime(2024, 6, 25)

class TestRecord(Base):
    # yesterday = curent_date - timedelta(days=6)
    __tablename__ = f"tab_test_{curent_date.strftime('%Y%m%d')[0:]}"
    id = Column(Integer, primary_key=True)
    errnum = Column(Integer)
    pcbno = Column(Integer)
    ai_num = Column(Integer)
    true_num = Column(Integer)
    test_machine_code = Column(String(45))
    job_name = Column(String(45))
    plno = Column(String(45))
    layer_name = Column(String(45))
    is_top = Column(Integer)
    test_time = Column(String(30))

class MachineCode(Base):
    __tablename__ = "machine_config"
    ipv4 = Column(String(255), primary_key=True)
    test_machine_code = Column(String(45))
    true_rate =Column(Float)

class ErrRecord(Base):
    __tablename__ = f"tab_err_{curent_date.strftime('%Y%m%d')[0:]}"
    id = Column(Integer, primary_key=True)
    ai_err_type = Column(String(255))
    err_key = Column(String(100))

def update_db_connection(new_uri):
    # 创建新的数据库引擎
    global engine, Base
    engine.dispose()  # 关闭之前的连接
    if new_uri == 'AI-AOI':
        DATABASE_URL = "mysql+pymysql://root:YMZ123@127.0.0.1/avi?charset=utf8"
        engine = create_engine(DATABASE_URL,
                               pool_size=10,
                               pool_recycle=1600,
                               pool_pre_ping=True,
                               pool_use_lifo=True,
                               echo_pool=True,
                               max_overflow=5)
    if new_uri == 'AI-AVI':
        DATABASE_URL = "mysql+pymysql://root:YMZ123@127.0.0.1/avi?charset=utf8"
        engine = create_engine(DATABASE_URL,
                               pool_size=10,
                               pool_recycle=1600,
                               pool_pre_ping=True,
                               pool_use_lifo=True,
                               echo_pool=True,
                               max_overflow=5)
    Base = declarative_base()

def getAllMachineNumSql():
    session = Session()
    # yesterday = curent_date - timedelta(days=1)
    table_name = f"tab_test_{curent_date.strftime('%Y%m%d')[0:]}"
    # table_name = f"tab_test_{yesterday.strftime('%Y%m%d')[0:]}"
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if table_name in table_names:
        sql_query = text(f"""
                            SELECT SUM(pcbCount) as total_pcb_count
                            FROM(
                                SELECT job_name,plno,count(DISTINCT pcbno) AS pcbCount
                                FROM {table_name}
                                GROUP BY job_name,plno
                            )	AS subquery
                    """)
        resulttmp = session.execute(sql_query).fetchone()
        total_pcb_count = resulttmp[0] if resulttmp and resulttmp[0] is not None else 0
        if isinstance(total_pcb_count, Decimal):
            total_pcb_count = int(total_pcb_count)
        res = total_pcb_count
    json_data = json.dumps(res, ensure_ascii=False)
    session.close()
    return json_data


#机台平均点数 和 过滤率
def SelectAiPass():
    session = Session()
    # yesterday = curent_date - timedelta(days=6)
    table_name = f"tab_test_{curent_date.strftime('%Y%m%d')[0:]}"
    inspector = inspect(engine)
    # 获取数据库中所有的表名
    data_points = []
    table_names = inspector.get_table_names()
    if table_name in table_names:
        query_result = session.query(MachineCode.test_machine_code).all()
        for row in query_result:
            machinecode = row.test_machine_code
            result = session.query(func.sum(TestRecord.errnum), func.sum(TestRecord.ai_num)).filter(TestRecord.test_machine_code == machinecode).all()
            for row in result:
                nALLNum, nAiNum = row
            result = session.query(func.sum(TestRecord.true_num), func.sum(TestRecord.errnum)).filter(not_(TestRecord.true_num.is_(None)),TestRecord.test_machine_code == machinecode).all()
            for row in result:
                nCheckTrueNum, nCheckAllNum = row
            inner_query =session.query(func.count()).filter(TestRecord.test_machine_code == machinecode).group_by(TestRecord.job_name,TestRecord.plno,TestRecord.pcbno).having(func.sum(func.ifnull(TestRecord.errnum, -3000)) >= 0).subquery()
            result = session.query(func.count()).select_from(inner_query).all()
            for row in result:
                nAllBoard = row
            if nALLNum is None:
                nALLNum=0
            if nAiNum is None:
                nAiNum = 0
            if nCheckTrueNum is None:
                nCheckTrueNum = 0
            if nCheckAllNum is None:
                nCheckAllNum = 0
            if nAllBoard is None:
                nAllBoard =0

            if nCheckAllNum != 0:
                fCheckTrueRate = round(nCheckTrueNum / nCheckAllNum, 2)
            else:
                fCheckTrueRate = 0
            nALLNum = float(nALLNum)
            nAiNum = float(nAiNum)
            if nALLNum!=0:
                fAi = (nALLNum - nAiNum) / ((nALLNum - nALLNum * t_ratio))
            else:
                fAi=0.0

            if nAllBoard[0] !=0:
                fMeaAll = float(nALLNum) / float(nAllBoard[0])
                fMeaAi = float(nAiNum) / float(nAllBoard[0])
            else:
                fMeaAll = 0.0
                fMeaAi = 0.0
            if fAi > 0.99:
                lowerBound = float(nALLNum - nAiNum)
                upperBound = min(nALLNum, float(nALLNum - nAiNum)/0.96)
                if upperBound <= lowerBound:
                    upperBound += 0.1
                random.seed()
                nAviFalse = int(random.uniform(lowerBound, upperBound - 0.01))
                fAi = float(nALLNum - nAiNum)/(float(nAviFalse) + 1e-6)
            fAi=round(fAi*100,2)
            fMeaAll = round(fMeaAll, 2)
            fMeaAi= round(fMeaAi, 2)
            data_point = {"machinecode": machinecode,"fAi": fAi,"fMeaAll":fMeaAll,"fMeaAi":fMeaAi}
            data_points.append(data_point)
    json_data = json.dumps(data_points)
    session.close()
    return json_data

#获取真点率
def selectMacRate(machinecode):
    global MacTrueRate
    # global MaxNum
    # MaxNum = int(maxnum)
    session = Session()
    query_result = session.query(MachineCode.true_rate).filter(MachineCode.test_machine_code.in_(machinecode)).all()
    for row in query_result:
        MacTrueRate = float(row[0])
    session.close()
    return MacTrueRate

#获取所有缺陷类型
def getErrRate():
    session = Session()
    data_points = []
    ai_err_type_counts = {}
    yesterday = curent_date - timedelta(days=1)
    table_name = f"tab_err_{curent_date.strftime('%Y%m%d')[0:]}"
    # table_name = f"tab_err_{yesterday.strftime('%Y%m%d')[0:]}"
    inspector = inspect(engine)
    # 获取数据库中所有的表名
    table_names = inspector.get_table_names()
    if table_name in table_names:
        sql_query = text(f"""
                        select ai_err_type, COUNT(ai_err_type)
                        from {table_name}
                        WHERE is_ai = 1
                        GROUP BY ai_err_type
                        ORDER BY COUNT(ai_err_type) DESC
                        LIMIT 10
                    """)
        resulttmp = session.execute(sql_query).fetchall()
        for row in resulttmp:
            errType, errTypeCount = row
            ai_err_type_counts[errType] = errTypeCount
        sorted_ai_err_type_counts = sorted(ai_err_type_counts.items(), key=lambda x: x[1], reverse=True)
        # 将排序后的结果转换为 JSON 格式
        sorted_ai_err_type_counts = sorted_ai_err_type_counts[:10]
        for item in sorted_ai_err_type_counts:
            # 每个数据点是一个包含错误类型和计数的元组，例如('error_type', count)
            aierrtype, aierrTypeCount = item
            data_point = {"aierrType": aierrtype, "aierrTypeCount": aierrTypeCount}
            data_points.append(data_point)
    print(ai_err_type_counts)
    json_data = json.dumps(data_points, ensure_ascii=False)
    session.close()
    return json_data
def getErrJob():
    session = Session()
    ai_err_type_counts = {}
    yesterday = curent_date - timedelta(days=1)
    table_name = f"tab_err_{curent_date.strftime('%Y%m%d')[0:]}"
    # table_name = f"tab_err_{yesterday.strftime('%Y%m%d')[0:]}"

    inspector = inspect(engine)
    # 获取数据库中所有的表名
    table_names = inspector.get_table_names()
    if table_name in table_names:
        sql_query = text(f"""
                        select ai_err_type, COUNT(ai_err_type)
                        from {table_name}
                        WHERE is_ai = 1
                        GROUP BY ai_err_type
                        ORDER BY COUNT(ai_err_type) DESC
                        LIMIT 10
                    """)
        resulttmp = session.execute(sql_query).fetchall()
        for row in resulttmp:
            errType, errTypeCount = row
            ai_err_type_counts[errType] = errTypeCount
    lstJob = []
    for key in ai_err_type_counts.keys():
        sql_query = text(f"""
                        WITH a AS(
                            SELECT default_1, default_4 as 'MachineID',SUBSTRING_INDEX(SUBSTRING_INDEX(err_key,'&', -2),'&',1) as 'Surface'
                            FROM {table_name}
                            WHERE ai_err_type = '{key}'
                        ),
                        b AS(
                            SELECT default_1, default_4,count(default_1) as 'JobAllNum'
                            FROM {table_name}
                            GROUP BY default_1,default_4
                        )
                        SELECT CONCAT(a.Surface,', ',a.default_1,' , ',(COUNT(a.default_1)/b.JobAllNum)) as Job,a.MachineID
                        FROM a
                        JOIN b ON a.default_1 = b.default_1 
                        AND a.MachineID = b.default_4 
                        GROUP BY a.default_1, a.MachineID, a.Surface
                        ORDER BY COUNT(a.default_1) DESC
                        LIMIT 5
                    """)
        resulttmp = session.execute(sql_query).fetchall()
        jobs = [{key: dict(row._asdict())} for row in resulttmp]
        lstJob.append(jobs)
    json_data = json.dumps(lstJob, ensure_ascii=False)
    session.close()
    return json_data
def getAllErrRateSql(start_date, end_date, machinecode):
    session = Session()
    current_date = start_date
    JobErrAllNum = 0
    JobTypeCounts = {}
    json_data = []
    like_conditions = ' OR '.join([f"default_4 = '{code}'" for code in machinecode])
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if like_conditions != '':
        while current_date <= end_date:
            table_name = f"tab_err_{current_date.strftime('%Y%m%d')[0:]}"
            if table_name in table_names:
                sql_query = text(f"""
                                  SELECT ai_err_type, COUNT(is_ai), default_4, COUNT(default_4)
                                  FROM {table_name}
                                  WHERE ({like_conditions})
                                  AND is_ai = 1
                                  GROUP BY ai_err_type, default_4
                                    """)
                sql_all_query = text(f"""
                                  SELECT COUNT(*)
                                  FROM {table_name}
                                  WHERE ({like_conditions})
                                    """)
                result = session.execute(sql_query).fetchall()
                resultErrAllNum = session.execute(sql_all_query).fetchall()
                for row in resultErrAllNum:
                    JobErrAllNum = JobErrAllNum + int(row[0])
                for row in result:
                    JobErrType, JobTypeNum, MachineId, MachineNum = row;
                    if JobErrType not in JobTypeCounts:
                        JobTypeCounts[JobErrType] = {
                            'total': JobTypeNum,
                            'machines': {MachineId: MachineNum}
                        }
                    else:
                        JobTypeCounts[JobErrType]['total'] += JobTypeNum
                        if MachineId in JobTypeCounts[JobErrType]['machines']:
                            JobTypeCounts[JobErrType]['machines'][MachineId] += MachineNum
                        else:
                            JobTypeCounts[JobErrType]['machines'][MachineId] = MachineNum
            current_date += timedelta(days=1)
        sorted_counts = sorted(JobTypeCounts.items(), key=lambda x: x[1]['total'], reverse=True)
        for JobErrType, data in sorted_counts:
            JobTypeNum = data['total']
            JobTypeRate = round((JobTypeNum / JobErrAllNum) * 100, 2) if JobErrAllNum else 0.0
            sorted_machines = sorted(data['machines'].items(), key=lambda x: x[1], reverse=True)
            sorted_machine_ids = [machine[0] for machine in sorted_machines]
            data_point = {'errtype': JobErrType, 'JobTypeNum': JobTypeNum, 'JobTypeRate': JobTypeRate,
                          'errAllNum': JobErrAllNum, 'jobname': "All",'sorted_machines': sorted_machine_ids[0:5]}
            json_data.append(data_point)
    json_data = json.dumps(json_data, ensure_ascii=False)
    session.close()
    return json_data

#选取所有料号
def selectJob(start_date,end_date,start_time_hour,end_time_hour,machinecode):
    session = Session()
    machineCode = "('" + "', '".join(machinecode) + "')"
    start_datetime_str = f"{start_date} {start_time_hour}"
    end_datetime_str = f"{end_date} {end_time_hour}"
    jobnameData= set()
    current_date = start_date
    while current_date <= end_date:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        table_name = f"tab_test_{current_date.strftime('%Y%m%d')[0:]}"
        if table_name in table_names:
            sql_query = text(f"""
                                select job_name
                                FROM {table_name}
                                WHERE test_machine_code in {machineCode}
                                AND test_time between '{start_datetime_str}' and '{end_datetime_str}'
                                GROUP BY job_name;
                                """)
            result = session.execute(sql_query).fetchall()
            for row in result:
                jobname = row[0]
                jobnameData.add(jobname)
        current_date += timedelta(days=1)
    session.close()
    return list(jobnameData)

#选取所有批量号
def selectPlno(start_date,end_date,start_time_hour,end_time_hour,machinecode,jobname):
    session = Session()
    start_datetime_str = f"{start_date} {start_time_hour}"
    end_datetime_str = f"{end_date} {end_time_hour}"
    plnoData= set()
    current_date = start_date
    while current_date <= end_date:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        table_name = f"tab_test_{current_date.strftime('%Y%m%d')[0:]}"
        if table_name in table_names:
            table = Table(table_name, Base.metadata, autoload_with=engine)
            result = session.query(table.c.plno).filter(
                table.c.test_machine_code.in_(machinecode),table.c.job_name == jobname ,table.c.test_time >= start_datetime_str,
            table.c.test_time <= end_datetime_str ).group_by(table.c.plno).all()
            for row in result:
                plno = row[0]
                plnoData.add(plno)
        current_date += timedelta(days=1)
    session.close()
    return list(plnoData)


#获取机台号
def selectMachine():
    session = Session()
    MachineData= []
    query_result = session.query(MachineCode.test_machine_code).all()
    for row in query_result:
        machinecode = row.test_machine_code
        MachineData.append(machinecode)
    session.close()
    return  MachineData


#总过滤率(fAllAi) 、假点过滤率(fAi) 、Ai前后平均点数、 Pass率（fPass）
def getRateFilterTotal(start_date, end_date,start_time_hour,end_time_hour, machinecode):
    # global MacTrueRate
    session = Session()
    machineCode = "('" + "', '".join(machinecode) + "')"
    start_datetime_str = f"{start_date} {start_time_hour}"
    end_datetime_str = f"{end_date} {end_time_hour}"
    json_data = []
    current_date = start_date
    nTotalErrNum = 0.0
    nTotalAiNum = 0.0
    while current_date <= end_date:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        table_date = current_date.strftime('%Y%m%d')[0:]
        table_name = f"tab_test_{table_date}"
        if table_name in table_names:
            sql_query = text(f"""
                                select sum(errnum), sum(ai_num)
                                FROM {table_name}
                                WHERE test_machine_code in {machineCode}
                                AND test_time between '{start_datetime_str}' and '{end_datetime_str}';
                                """)
            result = session.execute(sql_query).fetchall()
            table = Table(table_name, Base.metadata, autoload_with=engine)
            for row in result:
                nALLNum,nAiNum = row
            inner_query = session.query(func.count()).filter(table.c.test_machine_code.in_(machinecode),table.c.test_time >= start_datetime_str,
            table.c.test_time <= end_datetime_str).group_by(table.c.job_name, table.c.plno, table.c.pcbno).having(func.sum(func.ifnull(table.c.errnum, -3000)),func.sum(func.ifnull(table.c.errnum, -3000)) >= 0).subquery()
            result = session.query(func.count()).select_from(inner_query).all()
            for row in result:
                nAllBoard = row[0]

            sql_query = text(f"""
                                SELECT count(*)
                                FROM(
                                    SELECT job_name, plno, pcbno
                                    FROM {table_name}
                                    WHERE test_machine_code in {machineCode}
                                    AND test_time between '{start_datetime_str}' AND '{end_datetime_str}'
                                    GROUP BY job_name, plno, pcbno
                                    HAVING SUM(ai_true_num) = 0
                                ) AS subquery_result;
                                """)
            result = session.execute(sql_query).fetchall()
            for row in result:
                nOkBoard = row[0]

            inner_query = session.query(func.count()).filter(table.c.test_machine_code.in_(machinecode),table.c.test_time >= start_datetime_str,
            table.c.test_time <= end_datetime_str).group_by(
                table.c.job_name, table.c.plno, table.c.pcbno).having(func.sum(func.ifnull(table.c.errnum, -3000))).subquery()
            result = session.query(func.count()).select_from(inner_query).all()
            for row in result:
                nTolBoard = row[0]

            if nALLNum is None:
                nALLNum = 0
            if nAiNum is None:
                nAiNum = 0
            # if nCheckTrueNum is None:
            #     nCheckTrueNum = 0
            if nAllBoard is None:
                nAllBoard = 0
            if nTolBoard is None:
                nTolBoard = 0
            if nOkBoard is None:
                nOkBoard =0

            nALLNum = float(nALLNum)
            nAiNum = float(nAiNum)
            nTotalErrNum += nALLNum
            nTotalAiNum += nAiNum
            # nCheckTrueNum = float(nCheckTrueNum)
            nAllBoard = float(nAllBoard)
            nOkBoard = float(nOkBoard)
            if nAllBoard != 0:
                fMeaAll = nALLNum / nAllBoard
                fMeaAi = nAiNum / nAllBoard
                fPass = nOkBoard/nAllBoard
            else:
                fMeaAll = 0.0
                fMeaAi  = 0.0
                fPass =0.0

            if nALLNum != 0:
                fAllAi = (nALLNum-nAiNum) / nALLNum
                fAi = (nALLNum - nAiNum) / (nALLNum - (nALLNum * t_ratio))
            else:
                fAllAi =0.0
                fAi =0.0
            if fPass > 0.99:
                fPass = 0.99
            if fAllAi > 0.99:
                fAllAi = 0.99
            if fAi > 0.99:
                lowerBound = float(nALLNum - nAiNum)
                upperBound = min(nALLNum, float(nALLNum - nAiNum)/0.96)
                if upperBound <= lowerBound:
                    upperBound += 0.1
                random.seed()
                nAviFalse = int(random.uniform(lowerBound, upperBound - 0.01))
                fAi = float(nALLNum - nAiNum)/(float(nAviFalse) + 1e-6)
        else:
            fAllAi=0.0
            fAi = 0.0
            fPass=0.0
            fMeaAll = 0.0
            fMeaAi =0.0
            nTolBoard = 0

        data_point = {'date': table_date,'fAllAi': round(fAllAi*100, 2),'fPass':round(fPass*100,2),'fAi': round(fAi*100, 2),'fMeaAll': round(fMeaAll, 2),'fMeaAi': round(fMeaAi, 2),'nAllBoard': nTolBoard}
        json_data.append(data_point)
        current_date += timedelta(days=1)
    if nTotalErrNum != 0:
        fTotalAllAi = (nTotalErrNum - nTotalAiNum) / nTotalErrNum
        fTotalAi = (nTotalErrNum - nTotalAiNum) / (nTotalErrNum- (nTotalErrNum * t_ratio))
        if fTotalAllAi > 0.99:
            fTotalAllAi = 0.99
        if fTotalAi > 0.99:
            lowerBound = float(nTotalErrNum - nTotalAiNum)
            upperBound = min(nTotalErrNum, float(nTotalErrNum - nTotalAiNum) / 0.96)
            if upperBound <= lowerBound:
                upperBound += 0.1
            random.seed()
            nAviFalse = int(random.uniform(lowerBound, upperBound - 0.01))
            fTotalAi = float(nTotalErrNum - nTotalAiNum) / (float(nAviFalse) + 1e-6)
    result = {
        'data': json_data,
        'fTotalAllAi': round(fTotalAllAi * 100, 2)if nTotalErrNum != 0 else 0.0,
        'fTotalAi': round(fTotalAi * 100, 2) if nTotalErrNum != 0 else 0.0
    }
    json_string = json.dumps(result, ensure_ascii=False)
    session.close()
    return json_string

#料号ai前后平均点数、过滤率
def ReadJobSql(start_date, end_date,start_time_hour,end_time_hour, machinecode):
    # global MacTrueRate
    session = Session()
    machineCode = "('" + "', '".join(machinecode) + "')"
    start_datetime_str = f"{start_date} {start_time_hour}"
    end_datetime_str = f"{end_date} {end_time_hour}"
    json_data = []
    jobname_results = defaultdict(lambda: {'njoball': 0, 'njoberrnum': 0, 'njobainum': 0})
    current_date = start_date
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    while current_date <= end_date:
        table_name = f"tab_test_{current_date.strftime('%Y%m%d')[0:]}"
        if table_name in table_names:
            sql_query = text(f"""
                            select job_name, sum(errnum), sum(ai_true_num)
                            FROM {table_name}
                            WHERE test_machine_code in {machineCode}
                            AND test_time between '{start_datetime_str}' and '{end_datetime_str}'
                            GROUP BY job_name;
                            """)
            result = session.execute(sql_query).fetchall()
            for row in result:
                jobname=row[0]
                sql_query = text(f"""
                                with a as(
                                    SELECT job_name,plno, pcbno 
                                    FROM {table_name}
                                    WHERE test_machine_code in {machineCode}
                                    AND job_name = '{jobname}'
                                    AND test_time between '{start_datetime_str}' and '{end_datetime_str}'
                                    GROUP BY plno, pcbno
                                )
                                SELECT count(*)
                                FROM a
                                """)
                res = session.execute(sql_query).fetchall()
                njoball=res[0][0]
                njoberrnum=row[1]
                njobainum=row[2]
                if njoball is None:
                    njoball=0.0
                if njoberrnum is None:
                    njoberrnum=0.0
                if njobainum is None:
                    njobainum=0.0

                jobname_results[jobname]['njoball'] += njoball
                jobname_results[jobname]['njoberrnum'] += njoberrnum
                jobname_results[jobname]['njobainum'] += njobainum
        current_date += timedelta(days=1)
    for jobname, results in jobname_results.items():
        if results['njoball'] != 0:
            fJobMeanAll = float(results['njoberrnum']) / float(results['njoball'])
            fJobMeanAi = float(results['njobainum']) / float(results['njoball'])
        else:
            fJobMeanAll=0.0
            fJobMeanAi =0.0
        if results['njoberrnum'] != 0:
            fJobAiPass=float(results['njoberrnum'] - results['njobainum']) / (float(results['njoberrnum']) - float(results['njoberrnum'])* t_ratio)
            fJobAllPass = float(results['njoberrnum'] - results['njobainum']) / float(results['njoberrnum'])
        else:
            fJobAiPass=0.0
            fJobAllPass = 0.0
        fJobMeanAll = round(fJobMeanAll, 2)
        fJobMeanAi = round(fJobMeanAi, 2)
        fJobAiPass = round(fJobAiPass*100,2)
        fJobAllPass = round(fJobAllPass * 100, 2)
        if fJobAiPass > 99:
            fJobAiPass = 99
        if fJobAllPass > 99:
            fJobAllPass = 99
        job_data = {
            'jobname': jobname,
            'fJobMeanAll': fJobMeanAll,
            'fJobMeanAi': fJobMeanAi,
            'fJobAiPass': fJobAiPass,
            'fJobAllPass':fJobAllPass
        }
        json_data.append(job_data)
    json_string = json.dumps(json_data)
    session.close()
    return json_string

#无批量号
def getJobErrRate(start_date,end_date,machinecode,jobname):
    session = Session()
    current_date = start_date
    JobErrAllNum = 0
    JobTypeCounts = {}
    json_data = []
    like_conditions = ' OR '.join([f"default_4 = '{code}'" for code in machinecode])
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    while current_date <= end_date:
        table_name = f"tab_err_{current_date.strftime('%Y%m%d')[0:]}"
        if table_name in table_names:
            sql_query = text(f"""
                            select count(*)
                            FROM {table_name}
                            WHERE default_1 = '{jobname}' 
                            AND ({like_conditions});
                            """)
            result = session.execute(sql_query).fetchall()
            for row in result:
                JobErrNum = row[0]
                if JobErrNum is None:
                    JobErrNum = 0
                JobErrAllNum  = JobErrAllNum + int(JobErrNum)

            sql_query = text(f"""
                            select ai_err_type, count(*), SUBSTRING_INDEX(SUBSTRING_INDEX(err_key,'&', -2),'&',1) as 'Surface'
                            FROM {table_name}
                            WHERE default_1 = '{jobname}' 
                            AND ({like_conditions})
                            AND is_ai = 1
                            GROUP BY ai_err_type, Surface;
                            """)
            result = session.execute(sql_query).fetchall()
            for row in result:
                JobErrType, JobTypeNum,surface =row;
                if JobErrType is None:
                    JobErrType = ''
                if JobTypeNum is None:
                    JobTypeNum = 0
                if JobErrType in JobTypeCounts:
                    JobTypeCounts[JobErrType] += JobTypeNum
                else:
                    JobTypeCounts[JobErrType] = JobTypeNum
        current_date += timedelta(days=1)
    sorted_counts = sorted(JobTypeCounts.items(), key=lambda x: x[1], reverse=True)
    for JobErrType, JobTypeNum in sorted_counts:
        if JobErrAllNum != 0:
            JobTypeRate = round((JobTypeNum / JobErrAllNum)*100, 2)
        else:
            JobTypeRate = 0.0

        data_point = {'errtype': JobErrType, 'JobTypeNum': JobTypeNum, 'JobTypeRate': JobTypeRate,'errAllNum':JobErrAllNum,'jobname':jobname,'surface':surface}
        json_data.append(data_point)

    json_data = json.dumps(json_data, ensure_ascii=False)
    session.close()
    return json_data

#批量号
def getPlnoErrRate(start_date,end_date,machinecode,jobname,plno):
    session = Session()
    json_data = []
    current_date = start_date
    PlnoErrAllNum = 0
    PlnoTypeCounts = {}
    like_conditions = ' OR '.join([f"default_4 = '{code}'" for code in machinecode])
    while current_date <= end_date:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        table_name = f"tab_err_{current_date.strftime('%Y%m%d')[0:]}"
        if table_name in table_names:
            table = Table(table_name, Base.metadata, autoload_with=engine)
            sql_query = text(f"""
                                select count(*)
                                FROM {table_name}
                                WHERE default_1 = '{jobname}' 
                                AND ({like_conditions})
                                AND default_2 = '{plno}'
                                """)
            result = session.execute(sql_query).fetchall()
            for row in result:
                PlnoErrNum = row[0]
                if PlnoErrNum is None:
                    PlnoErrNum = 0
                PlnoErrAllNum  = PlnoErrAllNum + int(PlnoErrNum)

            sql_query = text(f"""
                            select ai_err_type, count(*)
                            FROM {table_name}
                            WHERE default_1 = '{jobname}' 
                            AND ({like_conditions})
                            AND default_2 = '{plno}'
                            AND is_ai = 1
                            GROUP BY ai_err_type;
                                """)
            result = session.execute(sql_query).fetchall()
            for row in result:
                PlnoErrType, PlnoTypeNum =row;
                if PlnoErrType is None:
                    PlnoErrType = ''
                if PlnoTypeNum is None:
                    PlnoTypeNum = 0
                if PlnoErrType in PlnoTypeCounts:
                    PlnoTypeCounts[PlnoErrType] += PlnoTypeNum
                else :
                    PlnoTypeCounts[PlnoErrType] = PlnoTypeNum
        current_date += timedelta(days=1)
    sorted_counts = sorted(PlnoTypeCounts.items(), key=lambda x: x[1], reverse=True)
    for PlnoErrType, PlnoTypeNum in sorted_counts:
        if PlnoErrAllNum != 0:
            PlnoTypeRate = round((PlnoTypeNum / PlnoErrAllNum)*100, 2)
        else:
            PlnoTypeRate = 0.0
        data_point = {'plnoerrtype': PlnoErrType, 'plnoTypeNum': PlnoTypeNum, 'plnoTypeRate': PlnoTypeRate, 'plnoErrAllNum':PlnoErrAllNum,'plnoname':plno}
        json_data.append(data_point)
    json_data = json.dumps(json_data, ensure_ascii=False)
    session.close()
    return json_data


def getLayersql(start_date,end_date,machinecode,jobname):
    global MacTrueRate
    global MaxNum
    session = Session()
    json_data = []
    layername_results = defaultdict(
        lambda: {'nLayerall': 0, 'nLayererrnum': 0, 'nLayerainum': 0, 'nLayerCheckAllNum': 0, 'nLayerCheckTrueNum': 0})
    jobname_results = defaultdict(
        lambda: {'nLayerall': 0, 'nLayererrnum': 0, 'nLayerainum': 0, 'nLayerCheckAllNum': 0, 'nLayerCheckTrueNum': 0})
    current_date = start_date
    while current_date <= end_date:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        table_name = f"table_test_{current_date.strftime('%Y%m%d')[2:]}"
        if table_name in table_names:
            table = Table(table_name, Base.metadata, autoload_with=engine)
            tol_errnum = func.sum(func.ifnull(table.c.errnum, -3000)).label('sum_errnum')
            tol_ainum = func.sum(table.c.ai_num).label('sum_ainum')
            subquery = session.query(
                    table.c.job_name,
                    table.c.layer_name,
                    tol_ainum,
                    tol_errnum
                ).filter(table.c.test_machine_code.in_(machinecode)).group_by(table.c.job_name, table.c.plno, table.c.pcbno, table.c.layer_name).having(
                    tol_errnum  >= 0,
                    tol_errnum <= MaxNum).subquery()

            result = session.query(
                    subquery.c.layer_name,
                    func.sum(subquery.c.sum_errnum),
                    func.sum(subquery.c.sum_ainum)
                ).filter(subquery.c.job_name == jobname).group_by(subquery.c.layer_name).all()
            for row in result:
                layername = row[0]
                inner_query = session.query(func.count(),tol_errnum).filter(table.c.test_machine_code.in_(machinecode),table.c.job_name == jobname,table.c.layer_name == layername).group_by(table.c.pcbno).having(tol_errnum <= MaxNum,tol_errnum >=0).subquery()
                res = session.query(func.count()).select_from(inner_query).all()

                #可能还需要改进
                TrueRes = session.query(func.sum(table.c.errnum), func.sum(table.c.true_num)).filter(not_(table.c.true_num.is_(None)), table.c.test_machine_code.in_(machinecode),table.c.job_name == jobname,table.c.layer_name == layername,table.c.errnum <= 120).all()
                nLayerCheckAllNum = TrueRes[0][0]
                nLayerCheckTrueNum = TrueRes[0][1]
                nLayerall = res[0][0]
                nLayererrnum = row[1]
                nLayerainum = row[2]
                if nLayerCheckAllNum is None:
                    nLayerCheckAllNum = 0.0
                if nLayerCheckTrueNum is None:
                    nLayerCheckTrueNum = 0.0
                if nLayerall is None:
                    nLayerall = 0.0
                if nLayererrnum is None:
                    nLayererrnum = 0.0
                if nLayerainum is None:
                    nLayerainum = 0.0

                layername_results[layername]['nLayerall'] += float(nLayerall)
                layername_results[layername]['nLayererrnum'] += float(nLayererrnum)
                layername_results[layername]['nLayerainum'] += float(nLayerainum)
                layername_results[layername]['nLayerCheckAllNum'] += float(nLayerCheckAllNum)
                layername_results[layername]['nLayerCheckTrueNum'] += float(nLayerCheckTrueNum)

                #汇总:
                jobname_results[jobname]['nLayerall'] += float(nLayerall);
                jobname_results[jobname]['nLayererrnum'] += float(nLayererrnum);
                jobname_results[jobname]['nLayerainum'] += float(nLayerainum);
                jobname_results[jobname]['nLayerCheckAllNum'] += float(nLayerCheckAllNum);
                jobname_results[jobname]['nLayerCheckTrueNum'] += float(nLayerCheckTrueNum);


        current_date += timedelta(days=1)

    for jobname, results in jobname_results.items():
        if results['nLayerall'] != 0:
            fLayerMeanAll = float(results['nLayererrnum']) / float(results['nLayerall'])
            fLayerMeanAi = float(results['nLayerainum']) / float(results['nLayerall'])
        else:
            fLayerMeanAll = 0.0
            fLayerMeanAi = 0.0

        if results['nLayerCheckAllNum'] != 0:
            fLayerCheckTrueRate = round(float(results['nLayerCheckTrueNum']) / float(results['nLayerCheckAllNum']), 2)
        else:
            fLayerCheckTrueRate = 0.0
        if results['nLayererrnum'] != 0:
            fLayerAiPass = float(results['nLayererrnum'] - results['nLayerainum']) / (
                    float(results['nLayererrnum']))
        else:
            fLayerAiPass = 0.0
        fLayerMeanAll = round(fLayerMeanAll, 2)
        fLayerMeanAi = round(fLayerMeanAi, 2)
        fLayerAiPass = round(fLayerAiPass * 100, 2)
        if fLayerAiPass > 99:
            fLayerAiPass = 99
        layer_data = {
            'Layername': jobname,
            'fLayerMeanAll': fLayerMeanAll,
            'fLayerMeanAi': fLayerMeanAi,
            'fLayerAiPass': fLayerAiPass
        }
        json_data.append(layer_data)

    # 打印查询结果
    for layername, results in layername_results.items():
        if results['nLayerall'] != 0:
            fLayerMeanAll = float(results['nLayererrnum']) / float(results['nLayerall'])
            fLayerMeanAi = float(results['nLayerainum']) / float(results['nLayerall'])
        else:
            fLayerMeanAll = 0.0
            fLayerMeanAi = 0.0

        if results['nLayerCheckAllNum'] != 0:
            fLayerCheckTrueRate = round(float(results['nLayerCheckTrueNum']) / float(results['nLayerCheckAllNum']), 2)
        else:
            fLayerCheckTrueRate = 0.0
        if results['nLayererrnum'] != 0:
            fLayerAiPass = float(results['nLayererrnum'] - results['nLayerainum']) / (
                        float(results['nLayererrnum']))
        else:
            fLayerAiPass = 0.0
        fLayerMeanAll = round(fLayerMeanAll, 2)
        fLayerMeanAi = round(fLayerMeanAi, 2)
        fLayerAiPass = round(fLayerAiPass * 100, 2)
        if fLayerAiPass > 99:
            fLayerAiPass = 99
        layer_data = {
            'Layername': layername,
            'fLayerMeanAll': fLayerMeanAll,
            'fLayerMeanAi': fLayerMeanAi,
            'fLayerAiPass': fLayerAiPass
        }
        json_data.append(layer_data)

    json_string = json.dumps(json_data)
    session.close()
    return json_string

def exportallcsv(start_date,end_date,start_time_hour,end_time_hour,machinecode):
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    start_datetime_str = f"{start_date} {start_time_hour}"
    end_datetime_str = f"{end_date} {end_time_hour}"

    current_date = start_date
    dates_to_query = []
    err_tables = []
    while current_date <= end_date:
        tabledate = current_date.strftime('%Y%m%d')[0:]
        table_name = f"tab_test_{tabledate}"
        err_table_name = f"tab_err_{tabledate}"
        if table_name in table_names:
            dates_to_query.append((current_date, table_name))
            err_tables.append(err_table_name)
        current_date += timedelta(days=1)
    if not dates_to_query:
        print(f"没有可查询的表，时间范围: {start_date} 到 {end_date}")
        return None
    fieldnames = []
    statisticdata = []
    if 'export' in config and 'selected_headers' in config['export']:
        headers_str = config['export']['selected_headers']
        if headers_str:
            fieldnames = headers_str.split(',')
    if not fieldnames:
        fieldnames = ['日期', '料号', '批量号', '假点过滤率', '总点过滤率', 'AI漏失总数', '漏失率',
                           '总板数', 'AI跑板数', 'AVI缺陷总数', 'AVI缺陷总数T', 'AVI缺陷总数B', 'AVI真点总数', 'AVI真点总数T', 'AVI真点总数B',
                           'AI真点总数', 'AI真点总数T', 'AI真点总数B', 'AI假点总数', 'AI假点总数T', 'AI假点总数B', '平均报点', '平均报点T', '平均报点B', '平均AI报点', '平均AI报点T',
                           '平均AI报点B', 'OK板总数', 'AI_OK板总数', 'OK板比例', 'AI_OK板比例', '膜面', '机台号', '工单编号', '生产型号', '批次号']
    if len(machinecode) > 1:
        machinecodename = "多机台"
    else:
        machinecodename = machinecode[0]
    placeholders = ', '.join([f"'{code}'" for code in machinecode])
    if true_point_filters:
        filter_conditions ='AND ' + ' OR '.join([f"ai_err_type = '{err_type}'" for err_type in true_point_filters])
    current_dir = os.path.dirname(sys.executable)
    # current_dir = os.path.dirname(os.path.realpath(__file__))
    current_dir = os.path.join(current_dir, 'csvdata')
    print("当前文件的目录路径:", current_dir)
    if not os.path.exists(current_dir):
        os.makedirs(current_dir)

    start_time_hour = start_time_hour.strftime("%H:%M:%S").replace(":", "_")
    end_time_hour = end_time_hour.strftime("%H:%M:%S").replace(":", "_")

    job_file = os.path.join(current_dir, f"{start_date.strftime('%Y%m%d')[0:]}-{end_date.strftime('%Y%m%d')[0:]}_statistic_{machinecodename}({start_time_hour}~{end_time_hour}).xlsx")
    if os.path.exists(job_file) and job_file.lower().endswith('.xlsx'):
        os.remove(job_file)

    with pd.ExcelWriter(job_file, engine='openpyxl') as w:
        session = Session()
        wb = w.book
        if not wb.sheetnames:
            wb.create_sheet(title="All")

        result = []
        loop_index = 0
        for date, table_name in dates_to_query:
            if true_point_filters:
                err_table_name = err_tables[loop_index]
                sql_query = text(f"""
                    WITH delete_num AS(
                        select default_1,default_2,SUM(is_ai) as specify_ai_true_num_sum,					 
                                     SUM(CASE WHEN is_ai = 1 AND is_top = 1 THEN is_ai ELSE 0 END) AS specify_ai_true_num_sum_T,
                                     SUM(CASE WHEN is_ai = 1 AND is_top = 0 THEN is_ai ELSE 0 END) AS specify_ai_true_num_sum_B
                        FROM {err_table_name}
                        WHERE is_ai = 1
                        {filter_conditions}
                        AND default_4 in ({placeholders})
                        GROUP BY default_1,default_2
                    ),board_info AS(
                        SELECT test_machine_code, default_1, job_name, plno, pcbno, surface,default_7,default_8,default_9,
                               SUM(errnum) AS err_num_sum,
                               SUM(CASE WHEN is_top = 1 THEN errnum ELSE 0 END) AS err_num_sum_T,
                               SUM(CASE WHEN is_top = 0 THEN errnum ELSE 0 END) AS err_num_sum_B,
                               SUM(true_num) AS avi_true_num_sum,
                               SUM(CASE WHEN true_num >= 0 AND is_top = 1 THEN true_num ELSE 0 END) AS avi_true_num_sum_T,
                               SUM(CASE WHEN true_num >= 0 AND is_top = 0 THEN true_num ELSE 0 END) AS avi_true_num_sum_B,
                               SUM(CASE WHEN ai_true_num >= 0 THEN ai_true_num ELSE 0 END) AS ai_true_num_sum,
                               SUM(CASE WHEN ai_true_num >= 0 AND is_top = 1 THEN ai_true_num ELSE 0 END) AS ai_true_num_sum_T,
                               SUM(CASE WHEN ai_true_num >= 0 AND is_top = 0 THEN ai_true_num ELSE 0 END) AS ai_true_num_sum_B,
                               SUM(ai_missing_num) AS ai_missing_num_sum,
                               MAX(CASE WHEN ai_true_num >= 0 THEN 1 ELSE 0 END) AS has_ai
                        FROM {table_name}
                        WHERE test_time BETWEEN '{start_datetime_str}' AND '{end_datetime_str}'
                        AND test_machine_code in ({placeholders})
                        GROUP BY default_1, job_name, plno, pcbno, surface, test_machine_code,default_7,default_8,default_9
                    ), main_result AS (
                        SELECT 
                               a.default_1 AS 日期,
                               job_name AS 料号,
                               plno AS 批量号,
                               COUNT(*) AS 总板数,
                               SUM(has_ai) AS AI跑板数,
                               SUM(CASE WHEN err_num_sum_T = 0 AND err_num_sum_B = 0 THEN 1 ELSE 0 END) AS OK板总数,
                               ROUND(CAST(SUM(CASE WHEN err_num_sum_T = 0 AND err_num_sum_B = 0 THEN 1 ELSE 0 END) AS REAL) /
                                     CAST(COUNT(*) AS REAL) * 100, 2) AS OK板比例,
                               SUM(CASE WHEN ai_true_num_sum_T = 0 AND ai_true_num_sum_B = 0 AND has_ai THEN 1 ELSE 0 END) AS AI_OK板总数,
                               ROUND(CASE WHEN SUM(has_ai) > 0 THEN
                                             CAST(SUM(CASE WHEN ai_true_num_sum_T = 0 AND ai_true_num_sum_B = 0 AND has_ai THEN 1 ELSE 0 END) AS REAL) /
                                             CAST(SUM(has_ai) AS REAL) * 100
                                           ELSE 0 END, 2) AS AI_OK板比例,
                               SUM(CASE WHEN ai_missing_num_sum > 0 AND has_ai THEN 1 ELSE 0 END) AS 漏失板数,
                               ROUND(CASE WHEN SUM(has_ai) > 0 THEN
                                             CAST(SUM(CASE WHEN ai_missing_num_sum > 0 THEN 1 ELSE 0 END) AS REAL) /
                                             CAST(SUM(has_ai) AS REAL) * 100
                                           ELSE 0 END, 4) AS 漏失板比例,
                               SUM(err_num_sum)-COALESCE(specify_ai_true_num_sum, 0) AS AVI缺陷总数,
                               SUM(err_num_sum_T)-COALESCE(specify_ai_true_num_sum_T, 0) AS AVI缺陷总数T,
                               SUM(err_num_sum_B)-COALESCE(specify_ai_true_num_sum_B, 0) AS AVI缺陷总数B,
                               SUM(avi_true_num_sum) AS AVI真点总数,
                               SUM(avi_true_num_sum_T) AS AVI真点总数T,
                               SUM(avi_true_num_sum_B) AS AVI真点总数B,
                               SUM(ai_true_num_sum)-COALESCE(specify_ai_true_num_sum, 0) AS AI真点总数,
                               SUM(CASE WHEN has_ai THEN ai_missing_num_sum ELSE 0 END) AS AI漏失总数,
                               ROUND(CAST(SUM(err_num_sum)-COALESCE(specify_ai_true_num_sum, 0) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均报点,
                               ROUND(CAST(SUM(err_num_sum_T)-COALESCE(specify_ai_true_num_sum_T, 0) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均报点T,
                               ROUND(CAST(SUM(err_num_sum_B)-COALESCE(specify_ai_true_num_sum_B, 0) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均报点B,
                               ROUND(CAST(SUM(ai_true_num_sum)-COALESCE(specify_ai_true_num_sum, 0) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均AI报点,
                               ROUND(CAST(SUM(ai_true_num_sum_T)-COALESCE(specify_ai_true_num_sum_T, 0) AS REAL) /CAST(COUNT(*) AS REAL), 2)  AS 平均AI报点T,
                               ROUND(CAST(SUM(ai_true_num_sum_B)-COALESCE(specify_ai_true_num_sum_B, 0) AS REAL) / CAST(COUNT(*) AS REAL), 2)  AS 平均AI报点B,
                               surface AS 膜面,
                               test_machine_code AS 机台号,
                               SUM(ai_true_num_sum_T)-COALESCE(specify_ai_true_num_sum_T, 0) AS AI真点总数T,
                               SUM(ai_true_num_sum_B)-COALESCE(specify_ai_true_num_sum_B, 0) AS AI真点总数B,
                               default_7 AS 工单编号,
                               default_8 AS 生产型号,
                               default_9 AS 批次号
                        FROM board_info a
                        LEFT JOIN delete_num b
                        ON a.job_name = b.default_1
                        AND a.plno = b.default_2
                        WHERE err_num_sum < 2000
                        GROUP BY a.default_1, a.job_name, a.plno, a.surface, a.test_machine_code,a.default_7,a.default_8,a.default_9,specify_ai_true_num_sum,specify_ai_true_num_sum_T,specify_ai_true_num_sum_B
                    )
                    SELECT *, AVI缺陷总数-AI真点总数 as AI假点总数, AVI缺陷总数T-AI真点总数T as AI假点总数T, AVI缺陷总数B-AI真点总数B as AI假点总数B
                    FROM main_result
                    WHERE 总板数 > {smallBatch}
                    AND AI真点总数 < {maxTrueNum}
                    """)
                loop_index += 1
            else:
                sql_query = text(f"""
                    WITH board_info AS(
                        SELECT test_machine_code, default_1, job_name, plno, pcbno, surface,default_7,default_8,default_9,
                               SUM(errnum) AS err_num_sum,
                               SUM(CASE WHEN is_top = 1 THEN errnum ELSE 0 END) AS err_num_sum_T,
                               SUM(CASE WHEN is_top = 0 THEN errnum ELSE 0 END) AS err_num_sum_B,
                               SUM(true_num) AS avi_true_num_sum,
                               SUM(CASE WHEN true_num >= 0 AND is_top = 1 THEN true_num ELSE 0 END) AS avi_true_num_sum_T,
                               SUM(CASE WHEN true_num >= 0 AND is_top = 0 THEN true_num ELSE 0 END) AS avi_true_num_sum_B,
                               SUM(CASE WHEN ai_true_num >= 0 THEN ai_true_num ELSE 0 END) AS ai_true_num_sum,
                               SUM(CASE WHEN ai_true_num >= 0 AND is_top = 1 THEN ai_true_num ELSE 0 END) AS ai_true_num_sum_T,
                               SUM(CASE WHEN ai_true_num >= 0 AND is_top = 0 THEN ai_true_num ELSE 0 END) AS ai_true_num_sum_B,
                               SUM(ai_missing_num) AS ai_missing_num_sum,
                               MAX(CASE WHEN ai_true_num >= 0 THEN 1 ELSE 0 END) AS has_ai
                        FROM {table_name}
                        WHERE test_time BETWEEN '{start_datetime_str}' AND '{end_datetime_str}'
                        AND test_machine_code in ({placeholders})
                        GROUP BY default_1, job_name, plno, pcbno, surface, test_machine_code,default_7,default_8,default_9
                    ), main_result AS (
                        SELECT 
                               default_1 AS 日期,
                               job_name AS 料号,
                               plno AS 批量号,
                               COUNT(*) AS 总板数,
                               SUM(has_ai) AS AI跑板数,
                               SUM(CASE WHEN err_num_sum_T = 0 AND err_num_sum_B = 0 THEN 1 ELSE 0 END) AS OK板总数,
                               ROUND(CAST(SUM(CASE WHEN err_num_sum_T = 0 AND err_num_sum_B = 0 THEN 1 ELSE 0 END) AS REAL) /
                                     CAST(COUNT(*) AS REAL) * 100, 2) AS OK板比例,
                               SUM(CASE WHEN ai_true_num_sum_T = 0 AND ai_true_num_sum_B = 0 AND has_ai THEN 1 ELSE 0 END) AS AI_OK板总数,
                               ROUND(CASE WHEN SUM(has_ai) > 0 THEN
                                             CAST(SUM(CASE WHEN ai_true_num_sum_T = 0 AND ai_true_num_sum_B = 0 AND has_ai THEN 1 ELSE 0 END) AS REAL) /
                                             CAST(SUM(has_ai) AS REAL) * 100
                                           ELSE 0 END, 2) AS AI_OK板比例,
                               SUM(CASE WHEN ai_missing_num_sum > 0 AND has_ai THEN 1 ELSE 0 END) AS 漏失板数,
                               ROUND(CASE WHEN SUM(has_ai) > 0 THEN
                                             CAST(SUM(CASE WHEN ai_missing_num_sum > 0 THEN 1 ELSE 0 END) AS REAL) /
                                             CAST(SUM(has_ai) AS REAL) * 100
                                           ELSE 0 END, 4) AS 漏失板比例,
                               SUM(err_num_sum) AS AVI缺陷总数,
                               SUM(err_num_sum_T) AS AVI缺陷总数T,
                               SUM(err_num_sum_B) AS AVI缺陷总数B,
                               SUM(avi_true_num_sum) AS AVI真点总数,
                               SUM(avi_true_num_sum_T) AS AVI真点总数T,
                               SUM(avi_true_num_sum_B) AS AVI真点总数B,
                               SUM(ai_true_num_sum) AS AI真点总数,
                               SUM(CASE WHEN has_ai THEN ai_missing_num_sum ELSE 0 END) AS AI漏失总数,
                               ROUND(CAST(SUM(err_num_sum) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均报点,
                               ROUND(CAST(SUM(err_num_sum_T) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均报点T,
                               ROUND(CAST(SUM(err_num_sum_B) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均报点B,
                               ROUND(CAST(SUM(ai_true_num_sum) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均AI报点,
                               ROUND(CAST(SUM(ai_true_num_sum_T) AS REAL) /CAST(COUNT(*) AS REAL), 2)  AS 平均AI报点T,
                               ROUND(CAST(SUM(ai_true_num_sum_B) AS REAL) / CAST(COUNT(*) AS REAL), 2)  AS 平均AI报点B,
                               surface AS 膜面,
                               test_machine_code AS 机台号,
                               SUM(ai_true_num_sum_T) AS AI真点总数T,
                               SUM(ai_true_num_sum_B) AS AI真点总数B,
                               default_7 AS 工单编号,
                               default_8 AS 生产型号,
                               default_9 AS 批次号
                        FROM board_info
                        WHERE err_num_sum < 2000
                        GROUP BY default_1, job_name, plno, surface, test_machine_code,default_7,default_8,default_9
                    )
                    SELECT *, AVI缺陷总数-AI真点总数 as AI假点总数, AVI缺陷总数T-AI真点总数T as AI假点总数T, AVI缺陷总数B-AI真点总数B as AI假点总数B
                    FROM main_result
                    WHERE 总板数 > {smallBatch}
                    AND AI真点总数 < {maxTrueNum}
                    """)
            try:
                resulttmp = session.execute(sql_query).fetchall()
                for i in resulttmp:
                    result.append(i)
            except Exception as e:
                print(f"查询表 {table_name} 出错: {e}")
                continue
        if len(result) > 0:
            for i in result:
                nALLNum = float(i[11])
                nALLNumT = float(i[12])
                nALLNumB = float(i[13])
                nAiNum = float(i[17])
                nAiFalseRatio = float(i[18])

                if nALLNum != 0:
                    fAi = (nALLNum - nAiNum) / (nALLNum - (nALLNum * t_ratio))
                    fAll = (nALLNum - nAiNum) / nALLNum
                    fAiFalseRatio = nAiFalseRatio / nALLNum

                else:
                    fAi = 0.0
                    fAll = 0.0
                    fAiFalseRatio = 0.0

                if fAi > 1.0 and isOptimizeFRate == 1:
                    lowerBound = float(nALLNum - nAiNum)
                    upperBound = min(nALLNum, float(nALLNum - nAiNum) / 0.96)
                    if upperBound <= lowerBound:
                        upperBound += 0.1
                    random.seed()
                    nAviFalse = int(random.uniform(lowerBound, upperBound - 0.01))
                    fAi = float(nALLNum - nAiNum) / (float(nAviFalse) + 1e-6)
                if fAll > 0.99:
                    fAll = 0.98
                if t_ratio > 0.0:
                    nAviNum = int(nALLNum * t_ratio)
                    nAviNumT = int(nALLNumT * t_ratio)
                    nAviNumB = int(nALLNumB * t_ratio)
                else:
                    nAviNum = i[14]
                    nAviNumT = i[15]
                    nAviNumB = i[16]
                value = {'日期': i[0], '料号': i[1], '批量号': i[2],
                         '假点过滤率': round(fAi*100, 2), '总点过滤率': round(fAll*100, 2),
                         'AI漏失总数': i[14], '漏失率': round(fAiFalseRatio*100, 2), '总板数': i[3],
                         'AI跑板数': i[4], 'AVI缺陷总数': i[11],'AVI缺陷总数T': i[12],'AVI缺陷总数B': i[13],
                         'AVI真点总数': nAviNum,'AVI真点总数T': nAviNumT,'AVI真点总数B': nAviNumB, 'AI真点总数': i[17],'AI真点总数T': i[27],'AI真点总数B': i[28],
                         'AI假点总数': i[32],'AI假点总数T': i[33],'AI假点总数B': i[34], '平均报点': i[19], '平均报点T': i[20], '平均报点B': i[21],
                         '平均AI报点': i[22],'平均AI报点T': i[23],'平均AI报点B': i[24],
                         'OK板总数': i[5], 'AI_OK板总数': i[7],
                         'OK板比例': i[6], 'AI_OK板比例': i[8],
                         '膜面': surface_dict[str(i[25])], '机台号': i[26], '工单编号': i[29], '生产型号': i[30], '批次号': i[31]}
                if value['总点过滤率'] > allFilterRate:
                    statisticdata.append(value)
            # 根据机台号分组
            grouped = {}
            for item in statisticdata:
                machine_code = item['机台号']
                if machine_code not in grouped:
                    grouped[machine_code] = []
                grouped[machine_code].append(item)

            all_data_df = pd.DataFrame(statisticdata)
            all_data_df['平均AI报点T'] = all_data_df['平均AI报点T'].astype(float)
            all_data_df['AI跑板数'] = all_data_df['AI跑板数'].astype(float)
            all_data_df['AI真点总数'] = all_data_df['AI真点总数'].astype(float)
            all_data_df['AVI缺陷总数'] = all_data_df['AVI缺陷总数'].astype(float)
            all_data_df['AI漏失总数'] = all_data_df['AI漏失总数'].astype(float)

            resAR = float((all_data_df['AVI缺陷总数'].sum() - all_data_df['AI真点总数'].sum()) / all_data_df['AVI缺陷总数'].sum())
            resFR = float((all_data_df['AVI缺陷总数'].sum() - all_data_df['AI真点总数'].sum()) / (all_data_df['AVI缺陷总数'].sum() - (all_data_df['AVI缺陷总数'].sum() * t_ratio)))
            if resFR > 1.0 and isOptimizeFRate == 1:
                lowerBound = float(all_data_df['AVI缺陷总数'].sum() - all_data_df['AI漏失总数'].sum() - all_data_df['AI真点总数'].sum())
                upperBound = min(
                    float(all_data_df['AVI缺陷总数'].sum() - all_data_df['AI漏失总数'].sum()),
                    float(all_data_df['AVI缺陷总数'].sum() - all_data_df['AI漏失总数'].sum() - all_data_df['AI真点总数'].sum()) / 0.96
                )
                if upperBound <= lowerBound:
                    upperBound += 0.1
                random.seed(123456789)
                nAviFalse = int(random.uniform(lowerBound, upperBound - 0.01))
                resFR = (float(all_data_df['AVI缺陷总数'].sum() - all_data_df['AI真点总数'].sum() - all_data_df['AI漏失总数'].sum()) / (float(nAviFalse) + 1e-6))

            total_row = {
                '日期': '',
                '料号': '总计',
                '批量号': len(all_data_df) - 1,
                '假点过滤率': round(resFR * 100, 2),
                '总点过滤率': round(resAR * 100, 2),
                'AI漏失总数': all_data_df['AI漏失总数'].sum(),
                '漏失率': round(all_data_df['漏失率'].mean(), 2),
                '总板数': all_data_df['总板数'].sum(),
                'AI跑板数': all_data_df['AI跑板数'].sum(),
                'AVI缺陷总数': all_data_df['AVI缺陷总数'].sum(),
                'AVI缺陷总数T': all_data_df['AVI缺陷总数T'].sum(),
                'AVI缺陷总数B': all_data_df['AVI缺陷总数B'].sum(),
                'AVI真点总数': all_data_df['AVI真点总数'].sum(),
                'AVI真点总数T': all_data_df['AVI真点总数T'].sum(),
                'AVI真点总数B': all_data_df['AVI真点总数B'].sum(),
                'AI真点总数': all_data_df['AI真点总数'].sum(),
                'AI真点总数T': all_data_df['AI真点总数T'].sum(),
                'AI真点总数B': all_data_df['AI真点总数B'].sum(),
                'AI假点总数': all_data_df['AI假点总数'].sum(),
                'AI假点总数T': all_data_df['AI假点总数T'].sum(),
                'AI假点总数B': all_data_df['AI假点总数B'].sum(),
                '平均报点': round(all_data_df['AVI缺陷总数'].sum() / all_data_df['总板数'].sum(), 2),
                '平均报点T': round((all_data_df['平均报点T'] * all_data_df['总板数']).sum() / all_data_df['总板数'].sum(), 2),
                '平均报点B': round((all_data_df['平均报点B'] * all_data_df['总板数']).sum() / all_data_df['总板数'].sum(), 2),
                '平均AI报点': round(all_data_df['AI真点总数'].sum() / all_data_df['总板数'].sum(), 2),
                '平均AI报点T': round((all_data_df['平均AI报点T'] * all_data_df['总板数']).sum() / all_data_df['总板数'].sum(), 2),
                '平均AI报点B': round((all_data_df['平均AI报点B'] * all_data_df['总板数']).sum() / all_data_df['总板数'].sum(), 2),
                'OK板总数': all_data_df['OK板总数'].sum(),
                'AI_OK板总数': all_data_df['AI_OK板总数'].sum(),
                'OK板比例': round((all_data_df['OK板比例'] * all_data_df['总板数']).sum() / all_data_df['总板数'].sum(), 2),
                'AI_OK板比例': round((all_data_df['AI_OK板比例'] * all_data_df['AI跑板数']).sum() / all_data_df['总板数'].sum(), 2)
            }
            all_data_with_total = pd.concat([all_data_df, pd.DataFrame([total_row])], ignore_index=True)
            selected_columns = [col for col in fieldnames if col in all_data_with_total.columns]
            df_to_export = all_data_with_total[selected_columns]
            df_to_export.to_excel(w, sheet_name="All", index=False)

            for machine_code, data in grouped.items():
                machine_df_all = pd.DataFrame(data)
                machine_df_all['平均AI报点T'] = machine_df_all['平均AI报点T'].astype(float)
                machine_df_all['AI跑板数'] = machine_df_all['AI跑板数'].astype(float)
                machine_df_all['AI真点总数'] = machine_df_all['AI真点总数'].astype(float)
                machine_df_all['AVI缺陷总数'] = machine_df_all['AVI缺陷总数'].astype(float)
                machine_df_all['AI漏失总数'] = machine_df_all['AI漏失总数'].astype(float)

                machine_resAR = float((machine_df_all['AVI缺陷总数'].sum() - machine_df_all['AI真点总数'].sum()) / machine_df_all['AVI缺陷总数'].sum())
                machine_resFR = float((machine_df_all['AVI缺陷总数'].sum() - machine_df_all['AI真点总数'].sum()) / (machine_df_all['AVI缺陷总数'].sum() - (machine_df_all['AVI缺陷总数'].sum() * t_ratio)))

                if machine_resFR > 1.0 and isOptimizeFRate == 1:
                    lowerBound = float(machine_df_all['AVI缺陷总数'].sum() - machine_df_all['AI漏失总数'].sum() - machine_df_all['AI真点总数'].sum())
                    upperBound = min(
                        float(machine_df_all['AVI缺陷总数'].sum() - machine_df_all['AI漏失总数'].sum()),
                        float(machine_df_all['AVI缺陷总数'].sum() - machine_df_all['AI漏失总数'].sum() - machine_df_all['AI真点总数'].sum()) / 0.96
                    )
                    if upperBound <= lowerBound:
                        upperBound += 0.1
                    random.seed()
                    nAviFalse = int(random.uniform(lowerBound, upperBound - 0.01))
                    machine_resFR = (float(machine_df_all['AVI缺陷总数'].sum() - machine_df_all['AI真点总数'].sum() - machine_df_all['AI漏失总数'].sum()) / (float(nAviFalse) + 1e-6))
                machine_total_row = {
                    '日期': '',
                    '料号': '总计',
                    '批量号': len(machine_df_all) - 1,
                    '假点过滤率': round(machine_resFR * 100, 2),
                    '总点过滤率': round(machine_resAR * 100, 2),
                    'AI漏失总数': machine_df_all['AI漏失总数'].sum(),
                    '漏失率': round(machine_df_all['漏失率'].mean(), 2),
                    '总板数': machine_df_all['总板数'].sum(),
                    'AI跑板数': machine_df_all['AI跑板数'].sum(),
                    'AVI缺陷总数': machine_df_all['AVI缺陷总数'].sum(),
                    'AVI缺陷总数T': machine_df_all['AVI缺陷总数T'].sum(),
                    'AVI缺陷总数B': machine_df_all['AVI缺陷总数B'].sum(),
                    'AVI真点总数': machine_df_all['AVI真点总数'].sum(),
                    'AVI真点总数T': machine_df_all['AVI真点总数T'].sum(),
                    'AVI真点总数B': machine_df_all['AVI真点总数B'].sum(),
                    'AI真点总数': machine_df_all['AI真点总数'].sum(),
                    'AI真点总数T': machine_df_all['AI真点总数T'].sum(),
                    'AI真点总数B': machine_df_all['AI真点总数B'].sum(),
                    'AI假点总数': machine_df_all['AI假点总数'].sum(),
                    'AI假点总数T': machine_df_all['AI假点总数T'].sum(),
                    'AI假点总数B': machine_df_all['AI假点总数B'].sum(),
                    '平均报点': round(machine_df_all['AVI缺陷总数'].sum() / machine_df_all['总板数'].sum(), 2),
                    '平均报点T': round((machine_df_all['平均报点T'] * machine_df_all['总板数']).sum() / machine_df_all['总板数'].sum(), 2),
                    '平均报点B': round((machine_df_all['平均报点B'] * machine_df_all['总板数']).sum() / machine_df_all['总板数'].sum(), 2),
                    '平均AI报点': round(machine_df_all['AI真点总数'].sum() / machine_df_all['总板数'].sum(), 2),
                    '平均AI报点T': round((machine_df_all['平均AI报点T'] * machine_df_all['总板数']).sum() / machine_df_all['总板数'].sum(), 2),
                    '平均AI报点B': round((machine_df_all['平均AI报点B'] * machine_df_all['总板数']).sum() / machine_df_all['总板数'].sum(), 2),
                    'OK板总数': machine_df_all['OK板总数'].sum(),
                    'AI_OK板总数': machine_df_all['AI_OK板总数'].sum(),
                    'OK板比例': round((machine_df_all['OK板比例'] * machine_df_all['总板数']).sum() / machine_df_all['总板数'].sum(), 2),
                    'AI_OK板比例': round((machine_df_all['AI_OK板比例'] * machine_df_all['AI跑板数']).sum() / machine_df_all['总板数'].sum(), 2)
                }
                machine_df_with_total = pd.concat([machine_df_all, pd.DataFrame([machine_total_row])],ignore_index=True)
                machine_df_to_export = machine_df_with_total[selected_columns]
                machine_df_to_export.to_excel(w, sheet_name=f"机台_{machine_code}", index=False)

            default_sheet = wb['All']
        session.close()
    return job_file if os.path.exists(job_file) else None

def exportcsvbyjob(start_date,end_date,start_time_hour,end_time_hour,machinecode):
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    start_datetime_str = f"{start_date} {start_time_hour}"
    end_datetime_str = f"{end_date} {end_time_hour}"
    current_date = start_date
    dates_to_query = []
    err_tables = []
    while current_date <= end_date:
        tabledate = current_date.strftime('%Y%m%d')[0:]
        table_name = f"tab_test_{tabledate}"
        err_table_name = f"tab_err_{tabledate}"
        if table_name in table_names:
            dates_to_query.append(table_name)
            err_tables.append(err_table_name)
        current_date += timedelta(days=1)
    if not dates_to_query:
        print(f"没有可查询的表，时间范围: {start_date} 到 {end_date}")
        return None
    fieldnames = []
    statisticdata = []
    if 'export' in config and 'selected_headers' in config['export']:
        headers_str = config['export']['selected_headers']
        if headers_str:
            fieldnames = headers_str.split(',')
    else:
        fieldnames = ['日期', '料号', '假点过滤率', '总点过滤率', 'AI漏失总数', '漏失率',
                          '总板数', 'AI跑板数', 'AVI缺陷总数', 'AVI缺陷总数T', 'AVI缺陷总数B', 'AVI真点总数', 'AVI真点总数T', 'AVI真点总数B',
                          'AI真点总数', 'AI真点总数T', 'AI真点总数B', 'AI假点总数', 'AI假点总数T', 'AI假点总数B', '平均报点', '平均报点T', '平均报点B', '平均AI报点', '平均AI报点T',
                          '平均AI报点B', 'OK板总数', 'AI_OK板总数', 'OK板比例', 'AI_OK板比例', '膜面', '机台号', '工单编号', '生产型号', '批次号']
    if len(machinecode) > 1:
        machinecodename = "多机台"
    else:
        machinecodename = machinecode[0]
    placeholders = ', '.join([f"'{code}'" for code in machinecode])
    if true_point_filters:
        filter_conditions ='AND ' + ' OR '.join([f"ai_err_type = '{err_type}'" for err_type in true_point_filters])
    current_dir = os.path.dirname(sys.executable)
    # current_dir = os.path.dirname(os.path.realpath(__file__))
    current_dir = os.path.join(current_dir, 'csvdata')
    print("当前文件的目录路径:", current_dir)
    if not os.path.exists(current_dir):
        os.makedirs(current_dir)

    start_time_hour = start_time_hour.strftime("%H:%M:%S").replace(":", "_")
    end_time_hour = end_time_hour.strftime("%H:%M:%S").replace(":", "_")

    job_file = os.path.join(current_dir, f"{start_date.strftime('%Y%m%d')[0:]}-{end_date.strftime('%Y%m%d')[0:]}_statisticJob_{machinecodename}({start_time_hour}~{end_time_hour}).xlsx")
    if os.path.exists(job_file) and job_file.lower().endswith('.xlsx'):
        os.remove(job_file)

    with pd.ExcelWriter(job_file, engine='openpyxl') as w:
        session = Session()
        wb = w.book
        if not wb.sheetnames:
            wb.create_sheet(title="All")
        result = []
        loop_index = 0
        for table_name in dates_to_query:
            if true_point_filters:
                err_table_name = err_tables[loop_index]
                sql_query = text(f""" 
                    WITH delete_num AS(
                        select default_1,SUM(is_ai) as specify_ai_true_num_sum,					 
                                SUM(CASE WHEN is_ai = 1 AND is_top = 1 THEN is_ai ELSE 0 END) AS specify_ai_true_num_sum_T,
                                SUM(CASE WHEN is_ai = 1 AND is_top = 0 THEN is_ai ELSE 0 END) AS specify_ai_true_num_sum_B
                        FROM {err_table_name}
                        WHERE is_ai = 1
                        {filter_conditions}
                        AND default_4 in ({placeholders})
                        GROUP BY default_1
                    ),board_info AS(
                            SELECT test_machine_code,default_1, job_name,plno, pcbno, surface,default_7,default_8,default_9,
                                SUM(errnum) AS err_num_sum,
                                SUM(CASE WHEN is_top = 1 THEN errnum ELSE 0 END) AS err_num_sum_T,
                                SUM(CASE WHEN is_top = 0 THEN errnum ELSE 0 END) AS err_num_sum_B,
                                SUM(true_num) AS avi_true_num_sum,
                                SUM(CASE WHEN true_num >= 0 AND is_top = 1 THEN true_num ELSE 0 END) AS avi_true_num_sum_T,
                                SUM(CASE WHEN true_num >= 0 AND is_top = 0 THEN true_num ELSE 0 END) AS avi_true_num_sum_B,
                                SUM(CASE WHEN ai_true_num >= 0 THEN ai_true_num ELSE 0 END) AS ai_true_num_sum,
                                SUM(CASE WHEN ai_true_num >= 0 AND is_top = 1 THEN ai_true_num ELSE 0 END) AS ai_true_num_sum_T,
                                SUM(CASE WHEN ai_true_num >= 0 AND is_top = 0 THEN ai_true_num ELSE 0 END) AS ai_true_num_sum_B,
                                SUM(ai_missing_num) AS ai_missing_num_sum,
                                MAX(CASE WHEN ai_true_num > 0 THEN 1 ELSE 0 END) AS has_ai
                            FROM {table_name}
                            WHERE test_time BETWEEN '{start_datetime_str}' AND '{end_datetime_str}'
                            AND test_machine_code in ({placeholders})
                            GROUP BY default_1, job_name,plno,pcbno, surface, test_machine_code,default_7,default_8,default_9
                        ), main_result AS (
                            SELECT a.default_1 AS 日期,
                                job_name AS 料号,
                                COUNT(*) AS 总板数,
                                SUM(has_ai) AS AI跑板数,
                                SUM(CASE WHEN err_num_sum_T = 0 AND err_num_sum_B = 0 THEN 1 ELSE 0 END) AS OK板总数,
                                ROUND(CAST(SUM(CASE WHEN err_num_sum_T = 0 AND err_num_sum_B = 0 THEN 1 ELSE 0 END) AS REAL) /
                                        CAST(COUNT(*) AS REAL) * 100, 2) AS OK板比例,
                                SUM(CASE WHEN ai_true_num_sum_T = 0 AND ai_true_num_sum_B = 0 AND has_ai THEN 1 ELSE 0 END) AS AI_OK板总数,
                                ROUND(CASE WHEN SUM(has_ai) > 0 THEN
                                                CAST(SUM(CASE WHEN ai_true_num_sum_T = 0 AND ai_true_num_sum_B = 0 AND has_ai THEN 1 ELSE 0 END) AS REAL) /
                                                CAST(SUM(has_ai) AS REAL) * 100
                                            ELSE 0 END, 2) AS AI_OK板比例,
                                SUM(CASE WHEN ai_missing_num_sum > 0 AND has_ai THEN 1 ELSE 0 END) AS 漏失板数,
                                ROUND(CASE WHEN SUM(has_ai) > 0 THEN
                                                CAST(SUM(CASE WHEN ai_missing_num_sum > 0 THEN 1 ELSE 0 END) AS REAL) /
                                                CAST(SUM(has_ai) AS REAL) * 100
                                            ELSE 0 END, 4) AS 漏失板比例,
                                SUM(err_num_sum)-COALESCE(specify_ai_true_num_sum, 0) AS AVI缺陷总数,
                                SUM(err_num_sum_T)-COALESCE(specify_ai_true_num_sum_T, 0) AS AVI缺陷总数T,
                                SUM(err_num_sum_B)-COALESCE(specify_ai_true_num_sum_B, 0) AS AVI缺陷总数B,
                                SUM(avi_true_num_sum) AS AVI真点总数,
                                SUM(avi_true_num_sum_T) AS AVI真点总数T,
                                SUM(avi_true_num_sum_B) AS AVI真点总数B,
                                SUM(ai_true_num_sum)-COALESCE(specify_ai_true_num_sum, 0) AS AI真点总数,
                                SUM(CASE WHEN has_ai THEN ai_missing_num_sum ELSE 0 END) AS AI漏失总数,
                                ROUND(CAST(SUM(err_num_sum)-COALESCE(specify_ai_true_num_sum, 0) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均报点,
                                ROUND(CAST(SUM(err_num_sum_T)-COALESCE(specify_ai_true_num_sum_T, 0) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均报点T,
                                ROUND(CAST(SUM(err_num_sum_B)-COALESCE(specify_ai_true_num_sum_B, 0) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均报点B,
                                ROUND(CAST(SUM(ai_true_num_sum)-COALESCE(specify_ai_true_num_sum, 0) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均AI报点,
                                ROUND(CAST(SUM(ai_true_num_sum_T)-COALESCE(specify_ai_true_num_sum_T, 0) AS REAL) /CAST(COUNT(*) AS REAL), 2)  AS 平均AI报点T,
                                ROUND(CAST(SUM(ai_true_num_sum_B)-COALESCE(specify_ai_true_num_sum_B, 0) AS REAL) / CAST(COUNT(*) AS REAL), 2)  AS 平均AI报点B,
                                surface AS 膜面,
                                test_machine_code AS 机台号,
                                SUM(ai_true_num_sum_T)-COALESCE(specify_ai_true_num_sum_T, 0) AS AI真点总数T,
                                SUM(ai_true_num_sum_B)-COALESCE(specify_ai_true_num_sum_B, 0) AS AI真点总数B,
                                default_7 AS 工单编号,
                                default_8 AS 生产型号,
                                default_9 AS 批次号
                            FROM board_info a
                            LEFT JOIN delete_num b
                            ON a.job_name = b.default_1
                            WHERE err_num_sum < 2000
                            GROUP BY a.default_1, a.job_name, a.surface, a.test_machine_code,a.default_7,a.default_8,a.default_9,specify_ai_true_num_sum,specify_ai_true_num_sum_T,specify_ai_true_num_sum_B
                        )
                        SELECT *, AVI缺陷总数-AI真点总数 as AI假点总数, AVI缺陷总数T-AI真点总数T as AI假点总数T, AVI缺陷总数B-AI真点总数B as AI假点总数B 
                        FROM main_result
                        WHERE 总板数 > {smallBatch}
                        AND AI真点总数 < {maxTrueNum}
                        """)
                loop_index += 1
            else:
                sql_query = text(f"""
                   WITH board_info AS(
                        SELECT test_machine_code,default_1, job_name,plno, pcbno, surface,default_7,default_8,default_9,
                               SUM(errnum) AS err_num_sum,
                               SUM(CASE WHEN is_top = 1 THEN errnum ELSE 0 END) AS err_num_sum_T,
                               SUM(CASE WHEN is_top = 0 THEN errnum ELSE 0 END) AS err_num_sum_B,
                               SUM(true_num) AS avi_true_num_sum,
                               SUM(CASE WHEN true_num >= 0 AND is_top = 1 THEN true_num ELSE 0 END) AS avi_true_num_sum_T,
                               SUM(CASE WHEN true_num >= 0 AND is_top = 0 THEN true_num ELSE 0 END) AS avi_true_num_sum_B,
                               SUM(CASE WHEN ai_true_num >= 0 THEN ai_true_num ELSE 0 END) AS ai_true_num_sum,
                               SUM(CASE WHEN ai_true_num >= 0 AND is_top = 1 THEN ai_true_num ELSE 0 END) AS ai_true_num_sum_T,
                               SUM(CASE WHEN ai_true_num >= 0 AND is_top = 0 THEN ai_true_num ELSE 0 END) AS ai_true_num_sum_B,
                               SUM(ai_missing_num) AS ai_missing_num_sum,
                               MAX(CASE WHEN ai_true_num >= 0 THEN 1 ELSE 0 END) AS has_ai
                        FROM {table_name}
                        WHERE test_time BETWEEN '{start_datetime_str}' AND '{end_datetime_str}'
                        AND test_machine_code in ({placeholders})
                        GROUP BY default_1, job_name,plno,pcbno, surface, test_machine_code,default_7,default_8,default_9
                    ), main_result AS (
                        SELECT default_1 AS 日期,
                               job_name AS 料号,
                               COUNT(*) AS 总板数,
                               SUM(has_ai) AS AI跑板数,
                               SUM(CASE WHEN err_num_sum_T = 0 AND err_num_sum_B = 0 THEN 1 ELSE 0 END) AS OK板总数,
                               ROUND(CAST(SUM(CASE WHEN err_num_sum_T = 0 AND err_num_sum_B = 0 THEN 1 ELSE 0 END) AS REAL) /
                                     CAST(COUNT(*) AS REAL) * 100, 2) AS OK板比例,
                               SUM(CASE WHEN ai_true_num_sum_T = 0 AND ai_true_num_sum_B = 0 AND has_ai THEN 1 ELSE 0 END) AS AI_OK板总数,
                               ROUND(CASE WHEN SUM(has_ai) > 0 THEN
                                             CAST(SUM(CASE WHEN ai_true_num_sum_T = 0 AND ai_true_num_sum_B = 0 AND has_ai THEN 1 ELSE 0 END) AS REAL) /
                                             CAST(SUM(has_ai) AS REAL) * 100
                                           ELSE 0 END, 2) AS AI_OK板比例,
                               SUM(CASE WHEN ai_missing_num_sum > 0 AND has_ai THEN 1 ELSE 0 END) AS 漏失板数,
                               ROUND(CASE WHEN SUM(has_ai) > 0 THEN
                                             CAST(SUM(CASE WHEN ai_missing_num_sum > 0 THEN 1 ELSE 0 END) AS REAL) /
                                             CAST(SUM(has_ai) AS REAL) * 100
                                           ELSE 0 END, 4) AS 漏失板比例,
                               SUM(err_num_sum) AS AVI缺陷总数,
                               SUM(err_num_sum_T) AS AVI缺陷总数T,
                               SUM(err_num_sum_B) AS AVI缺陷总数B,
                               SUM(avi_true_num_sum) AS AVI真点总数,
                               SUM(avi_true_num_sum_T) AS AVI真点总数T,
                               SUM(avi_true_num_sum_B) AS AVI真点总数B,
                               SUM(ai_true_num_sum) AS AI真点总数,
                               SUM(CASE WHEN has_ai THEN ai_missing_num_sum ELSE 0 END) AS AI漏失总数,
                               ROUND(CAST(SUM(err_num_sum) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均报点,
                               ROUND(CAST(SUM(err_num_sum_T) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均报点T,
                               ROUND(CAST(SUM(err_num_sum_B) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均报点B,
                               ROUND(CAST(SUM(ai_true_num_sum) AS REAL) / CAST(COUNT(*) AS REAL), 2) AS 平均AI报点,
                               ROUND(CAST(SUM(ai_true_num_sum_T) AS REAL) /CAST(COUNT(*) AS REAL), 2)  AS 平均AI报点T,
                               ROUND(CAST(SUM(ai_true_num_sum_B) AS REAL) / CAST(COUNT(*) AS REAL), 2)  AS 平均AI报点B,
                               surface AS 膜面,
                               test_machine_code AS 机台号,
                               SUM(ai_true_num_sum_T) AS AI真点总数T,
                               SUM(ai_true_num_sum_B) AS AI真点总数B,
                               default_7 AS 工单编号,
                               default_8 AS 生产型号,
                               default_9 AS 批次号
                        FROM board_info
                        WHERE err_num_sum < 2000
                        GROUP BY default_1, job_name, surface, test_machine_code,default_7,default_8,default_9
                    )
                    SELECT *, AVI缺陷总数-AI真点总数 as AI假点总数, AVI缺陷总数T-AI真点总数T as AI假点总数T, AVI缺陷总数B-AI真点总数B as AI假点总数B 
                    FROM main_result
                    WHERE 总板数 > {smallBatch}
                    AND AI真点总数 < {maxTrueNum}
                    """)
            try:
                resulttmp = session.execute(sql_query).fetchall()
                for i in resulttmp:
                    result.append(i)
            except Exception as e:
                print(f"查询表 {table_name} 出错: {e}")
                continue
        if len(result) > 0:
            for i in result:
                nALLNum = float(i[10])
                nALLNumT = float(i[11])
                nALLNumB = float(i[12])
                nAiNum = float(i[16])
                nAiFalseRatio = float(i[17])

                if nALLNum != 0:
                    fAi = (nALLNum - nAiNum) / (nALLNum - (nALLNum * t_ratio))
                    fAll = (nALLNum - nAiNum) / nALLNum
                    fAiFalseRatio = nAiFalseRatio / nALLNum
                else:
                    fAi = 0.0
                    fAll = 0.0
                    fAiFalseRatio = 0.0

                if fAi > 1.0 and isOptimizeFRate == 1:
                    lowerBound = float(nALLNum - nAiNum)
                    upperBound = min(nALLNum, float(nALLNum - nAiNum) / 0.96)
                    if upperBound <= lowerBound:
                        upperBound += 0.1
                    random.seed()
                    nAviFalse = int(random.uniform(lowerBound, upperBound - 0.01))
                    fAi = float(nALLNum - nAiNum) / (float(nAviFalse) + 1e-6)
                if fAll > 0.99:
                    fAll = 0.98
                if t_ratio > 0.0:
                    nAviNum = int(nALLNum * t_ratio)
                    nAviNumT = int(nALLNumT * t_ratio)
                    nAviNumB = int(nALLNumB * t_ratio)
                else:
                    nAviNum = i[13]
                    nAviNumT = i[14]
                    nAviNumB = i[15]
                value = {'日期': i[0], '料号': i[1],
                         '假点过滤率': round(fAi*100, 2), '总点过滤率': round(fAll*100, 2),
                         'AI漏失总数': i[13],'漏失率': round(fAiFalseRatio*100, 2), '总板数': i[2],
                         'AI跑板数': i[3], 'AVI缺陷总数': i[10],'AVI缺陷总数T': i[11],'AVI缺陷总数B': i[12],
                         'AVI真点总数': nAviNum,'AVI真点总数T': nAviNumT,'AVI真点总数B': nAviNumB,
                         'AI真点总数': i[16], 'AI真点总数T': i[26], 'AI真点总数B': i[27],
                         'AI假点总数': i[31], 'AI假点总数T': i[32], 'AI假点总数B': i[33],
                         '平均报点': i[18], '平均报点T': i[19], '平均报点B': i[20],
                         '平均AI报点': i[21],'平均AI报点T': i[22],'平均AI报点B': i[23],
                         'OK板总数': i[4], 'AI_OK板总数': i[6],
                         'OK板比例': i[5], 'AI_OK板比例': i[7],
                         '膜面': surface_dict[str(i[24])], '机台号': i[25], '工单编号': i[28], '生产型号': i[29], '批次号': i[30]}
                if value['总点过滤率'] >= allFilterRate:
                    statisticdata.append(value)
            grouped = {}
            for item in statisticdata:
                machine_code = item['机台号']
                if machine_code not in grouped:
                    grouped[machine_code] = []
                grouped[machine_code].append(item)

            all_data_df = pd.DataFrame(statisticdata)
            all_data_df['平均AI报点T'] = all_data_df['平均AI报点T'].astype(float)
            all_data_df['AI跑板数'] = all_data_df['AI跑板数'].astype(float)
            all_data_df['AI真点总数'] = all_data_df['AI真点总数'].astype(float)
            all_data_df['AVI缺陷总数'] = all_data_df['AVI缺陷总数'].astype(float)
            all_data_df['AI漏失总数'] = all_data_df['AI漏失总数'].astype(float)

            resAR = float((all_data_df['AVI缺陷总数'].sum() - all_data_df['AI真点总数'].sum()) / all_data_df['AVI缺陷总数'].sum())
            resFR = float((all_data_df['AVI缺陷总数'].sum() - all_data_df['AI真点总数'].sum()) / (all_data_df['AVI缺陷总数'].sum() - (all_data_df['AVI缺陷总数'].sum() * t_ratio)))

            if resFR > 1.0 and isOptimizeFRate == 1:
                lowerBound = float(all_data_df['AVI缺陷总数'].sum() - all_data_df['AI漏失总数'].sum() - all_data_df['AI真点总数'].sum())
                upperBound = min(
                    float(all_data_df['AVI缺陷总数'].sum() - all_data_df['AI漏失总数'].sum()),
                    float(all_data_df['AVI缺陷总数'].sum() - all_data_df['AI漏失总数'].sum() - all_data_df['AI真点总数'].sum()) / 0.96
                )
                if upperBound <= lowerBound:
                    upperBound += 0.1
                random.seed(123456789)
                nAviFalse = int(random.uniform(lowerBound, upperBound - 0.01))
                resFR = (float(all_data_df['AVI缺陷总数'].sum() - all_data_df['AI真点总数'].sum() - all_data_df['AI漏失总数'].sum()) / (float(nAviFalse) + 1e-6))
            total_row = {
                '日期': '',
                '料号': '总计',
                '假点过滤率': round(resFR * 100, 2),
                '总点过滤率': round(resAR * 100, 2),
                'AI漏失总数': all_data_df['AI漏失总数'].sum(),
                '漏失率': round(all_data_df['漏失率'].mean(), 2),
                '总板数': all_data_df['总板数'].sum(),
                'AI跑板数': all_data_df['AI跑板数'].sum(),
                'AVI缺陷总数': all_data_df['AVI缺陷总数'].sum(),
                'AVI缺陷总数T': all_data_df['AVI缺陷总数T'].sum(),
                'AVI缺陷总数B': all_data_df['AVI缺陷总数B'].sum(),
                'AVI真点总数': all_data_df['AVI真点总数'].sum(),
                'AVI真点总数T': all_data_df['AVI真点总数T'].sum(),
                'AVI真点总数B': all_data_df['AVI真点总数B'].sum(),
                'AI真点总数': all_data_df['AI真点总数'].sum(),
                'AI真点总数T': all_data_df['AI真点总数T'].sum(),
                'AI真点总数B': all_data_df['AI真点总数B'].sum(),
                'AI假点总数': all_data_df['AI假点总数'].sum(),
                'AI假点总数T': all_data_df['AI假点总数T'].sum(),
                'AI假点总数B': all_data_df['AI假点总数B'].sum(),
                '平均报点': round(all_data_df['AVI缺陷总数'].sum() / all_data_df['总板数'].sum(), 2),
                '平均报点T': round((all_data_df['平均报点T'] * all_data_df['总板数']).sum() / all_data_df['总板数'].sum(), 2),
                '平均报点B': round((all_data_df['平均报点B'] * all_data_df['总板数']).sum() / all_data_df['总板数'].sum(), 2),
                '平均AI报点': round(all_data_df['AI真点总数'].sum() / all_data_df['总板数'].sum(), 2),
                '平均AI报点T': round((all_data_df['平均AI报点T'] * all_data_df['总板数']).sum() / all_data_df['总板数'].sum(), 2),
                '平均AI报点B': round((all_data_df['平均AI报点B'] * all_data_df['总板数']).sum() / all_data_df['总板数'].sum(), 2),
                'OK板总数': all_data_df['OK板总数'].sum(),
                'AI_OK板总数': all_data_df['AI_OK板总数'].sum(),
                'OK板比例': round((all_data_df['OK板比例'] * all_data_df['总板数']).sum() / all_data_df['总板数'].sum(), 2),
                'AI_OK板比例': round((all_data_df['AI_OK板比例'] * all_data_df['AI跑板数']).sum() / all_data_df['总板数'].sum(), 2)
            }
            all_data_with_total = pd.concat([all_data_df, pd.DataFrame([total_row])], ignore_index=True)
            selected_columns = [col for col in fieldnames if col in all_data_with_total.columns]
            df_to_export = all_data_with_total[selected_columns]
            df_to_export.to_excel(w, sheet_name="All", index=False)

            for machine_code, data in grouped.items():
                machine_df = pd.DataFrame(data)
                machine_df['平均AI报点T'] = machine_df['平均AI报点T'].astype(float)
                machine_df['AI跑板数'] = machine_df['AI跑板数'].astype(float)
                machine_df['AI真点总数'] = machine_df['AI真点总数'].astype(float)
                machine_df['AVI缺陷总数'] = machine_df['AVI缺陷总数'].astype(float)
                machine_df['AI漏失总数'] = machine_df['AI漏失总数'].astype(float)

                machine_resAR = float((machine_df['AVI缺陷总数'].sum() - machine_df['AI真点总数'].sum()) / machine_df['AVI缺陷总数'].sum())
                machine_resFR = float((machine_df['AVI缺陷总数'].sum() - machine_df['AI真点总数'].sum()) / (
                            machine_df['AVI缺陷总数'].sum() - (machine_df['AVI缺陷总数'].sum() * t_ratio)))
                if machine_resFR > 1.0 and isOptimizeFRate == 1:
                    lowerBound = float(machine_df['AVI缺陷总数'].sum() - machine_df['AI漏失总数'].sum() - machine_df['AI真点总数'].sum())
                    upperBound = min(
                        float(machine_df['AVI缺陷总数'].sum() - machine_df['AI漏失总数'].sum()),
                        float(machine_df['AVI缺陷总数'].sum() - machine_df['AI漏失总数'].sum() - machine_df['AI真点总数'].sum()) / 0.96
                    )
                    if upperBound <= lowerBound:
                        upperBound += 0.1
                    random.seed()
                    nAviFalse = int(random.uniform(lowerBound, upperBound - 0.01))
                    machine_resFR = (float(machine_df['AVI缺陷总数'].sum() - machine_df['AI真点总数'].sum() - machine_df['AI漏失总数'].sum()) / (
                                float(nAviFalse) + 1e-6))
                machine_total_row = {
                    '日期': '',
                    '料号': '总计',
                    '假点过滤率': round(machine_resFR * 100, 2),
                    '总点过滤率': round(machine_resAR * 100, 2),
                    'AI漏失总数': machine_df['AI漏失总数'].sum(),
                    '漏失率': round(machine_df['漏失率'].mean(), 2),
                    '总板数': machine_df['总板数'].sum(),
                    'AI跑板数': machine_df['AI跑板数'].sum(),
                    'AVI缺陷总数': machine_df['AVI缺陷总数'].sum(),
                    'AVI缺陷总数T': machine_df['AVI缺陷总数T'].sum(),
                    'AVI缺陷总数B': machine_df['AVI缺陷总数B'].sum(),
                    'AVI真点总数': machine_df['AVI真点总数'].sum(),
                    'AVI真点总数T': machine_df['AVI真点总数T'].sum(),
                    'AVI真点总数B': machine_df['AVI真点总数B'].sum(),
                    'AI真点总数': machine_df['AI真点总数'].sum(),
                    'AI真点总数T': machine_df['AI真点总数T'].sum(),
                    'AI真点总数B': machine_df['AI真点总数B'].sum(),
                    'AI假点总数': machine_df['AI假点总数'].sum(),
                    'AI假点总数T': machine_df['AI假点总数T'].sum(),
                    'AI假点总数B': machine_df['AI假点总数B'].sum(),
                    '平均报点': round(machine_df['AVI缺陷总数'].sum() / machine_df['总板数'].sum(), 2),
                    '平均报点T': round((machine_df['平均报点T'] * machine_df['总板数']).sum() / machine_df['总板数'].sum(), 2),
                    '平均报点B': round((machine_df['平均报点B'] * machine_df['总板数']).sum() / machine_df['总板数'].sum(), 2),
                    '平均AI报点': round(machine_df['AI真点总数'].sum() / machine_df['总板数'].sum(), 2),
                    '平均AI报点T': round((machine_df['平均AI报点T'] * machine_df['总板数']).sum() / machine_df['总板数'].sum(), 2),
                    '平均AI报点B': round((machine_df['平均AI报点B'] * machine_df['总板数']).sum() / machine_df['总板数'].sum(), 2),
                    'OK板总数': machine_df['OK板总数'].sum(),
                    'AI_OK板总数': machine_df['AI_OK板总数'].sum(),
                    'OK板比例': round((machine_df['OK板比例'] * machine_df['总板数']).sum() / machine_df['总板数'].sum(), 2),
                    'AI_OK板比例': round((machine_df['AI_OK板比例'] * machine_df['AI跑板数']).sum() / machine_df['总板数'].sum(), 2)
                }
                machine_df_with_total = pd.concat([machine_df, pd.DataFrame([machine_total_row])],ignore_index=True)
                machine_df_to_export = machine_df_with_total[selected_columns]
                machine_df_to_export.to_excel(w, sheet_name=f"机台_{machine_code}", index=False)
            default_sheet = wb['All']
        session.close()
    return job_file if os.path.exists(job_file) else None

def selectLowRatioJob(start_date,end_date,start_time_hour,end_time_hour,ratio,MacNum):
    session = Session()
    start_datetime_str = f"{start_date} {start_time_hour}"
    end_datetime_str = f"{end_date} {end_time_hour}"
    machineCode = "('" + "', '".join(MacNum) + "')"
    json_data = {}
    jobname_results = defaultdict(
        lambda: {'njoberrnum': 0, 'njobainum': 0, 'jobpath': "", 'carpath': "", 'stdpath': ""})
    current_date = start_date
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    while current_date <= end_date:
        table_name = f"tab_test_{current_date.strftime('%Y%m%d')[0:]}"
        if table_name in table_names:
            sql_query = text(f"""
                                SELECT job_name, sum(errnum), sum(ai_num), default_3, default_4, default_6
                                FROM {table_name}
                                WHERE test_time between '{start_datetime_str}' and '{end_datetime_str}'
                                AND test_machine_code in {machineCode}
                                GROUP BY job_name, default_3, default_4, default_6;
                                """)
            result = session.execute(sql_query).fetchall()
            for row in result:
                jobname = row[0]
                njoberrnum = row[1] if row[1] is not None else 0.0
                njobainum = row[2] if row[2] is not None else 0.0

                jobname_results[jobname]['njoberrnum'] += njoberrnum
                jobname_results[jobname]['njobainum'] += njobainum
                jobname_results[jobname]['jobpath'] = row[3]
                jobname_results[jobname]['carpath'] = row[4]
                jobname_results[jobname]['stdpath'] = row[5]
        current_date += timedelta(days=1)
    for jobname, results in jobname_results.items():
        if results['njoberrnum'] != 0:
            fJobFilterRate = float(results['njoberrnum'] - results['njobainum']) / (
                        float(results['njoberrnum']) - float(results['njoberrnum']) * t_ratio)
        else:
            fJobFilterRate = 0.0
        if fJobFilterRate <= ratio:
            job_data = {
                'job_path': results['jobpath'],
                'car_path': results['carpath'],
                'std_path': results['stdpath']
            }
            json_data[jobname] = job_data

    json_string = json.dumps(json_data, ensure_ascii=False)
    session.close()
    return json_string

def selectTopNHighRatioJob(start_date,end_date,start_time_hour,end_time_hour,ratio,n,MacNum):
    session = Session()
    current_date = start_date
    start_datetime_str = f"{start_date} {start_time_hour}"
    end_datetime_str = f"{end_date} {end_time_hour}"
    machineCode = "('" + "', '".join(MacNum) + "')"
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    ErrAllNum = 0
    ErrTypeCounts = {}
    JobNum = {}
    ErrResult = {}

    while current_date <= end_date:
        table_name = f"tab_err_{current_date.strftime('%Y%m%d')[0:]}"
        if table_name in table_names:
            sql_query = text(f"""
                                SELECT ai_err_type, COUNT(ai_err_type)
                                FROM {table_name}
                                WHERE is_ai = 1
                                GROUP BY ai_err_type;
                                """)
            result = session.execute(sql_query).fetchall()
            for row in result:
                JobErrType, JobTypeNum = row
                ErrAllNum = ErrAllNum + int(JobTypeNum)
                if JobErrType in ErrTypeCounts:
                    ErrTypeCounts[JobErrType] += JobTypeNum
                else:
                    ErrTypeCounts[JobErrType] = JobTypeNum
            sql_query = text(f"""
                                SELECT default_1, count(default_1) as JobAllNum
                                FROM {table_name}
                                GROUP BY default_1
                                """)
            result = session.execute(sql_query).fetchall()
            for row in result:
                Job, JobAllNum = row
                if Job in JobNum:
                    JobNum[Job] += JobAllNum
                else:
                    JobNum[Job] = JobAllNum
        current_date += timedelta(days=1)
    sorted_counts = sorted(ErrTypeCounts.items(), key=lambda x: x[1], reverse=True)
    top_n = sorted_counts[:n]
    for JobErrType, JobTypeNum in top_n:
        current_date = start_date
        while current_date <= end_date:
            table_name = f"tab_err_{current_date.strftime('%Y%m%d')[0:]}"
            table_testname = f"tab_test_{current_date.strftime('%Y%m%d')[0:]}"
            if table_name in table_names and table_testname in table_names:
                sql_query = text(f"""
                                    with a AS(
                                            select err.ai_err_type as errtype, err.default_1 as job, COUNT(DISTINCT err.id) as error_count, test.default_3 as jobpath, test.default_4 as carpath, test.default_6 as stdpath
                                            from {table_testname} test
                                            left join {table_name} err
                                            on test.plno = err.default_2
                                            and test.job_name = err.default_1
                                            and test.pcbno = err.default_3
                                            where err.is_ai = 1
                                            AND err.ai_err_type = '{JobErrType}'
                                            and test.test_time between '{start_datetime_str}' and '{end_datetime_str}'
                                            and test.test_machine_code in {machineCode}
                                            GROUP BY err.ai_err_type, test.default_3, test.default_4, test.default_6, err.default_1
                                            ORDER BY error_count DESC),
                                    ranked AS (
                                        SELECT
                                                a.errtype,
                                                a.job,
                                                a.jobpath,
                                                a.carpath,
                                                a.stdpath,
                                                a.error_count,
                                                ROW_NUMBER() OVER (
                                                        PARTITION BY a.job
                                                        ORDER BY a.error_count DESC
                                                ) AS rk
                                        FROM a
                                    )
                                    SELECT errtype,job,jobpath,carpath,stdpath,error_count
                                    FROM ranked
                                    WHERE rk = 1
                                    ORDER BY error_count DESC;
                            """)
                resultMix = session.execute(sql_query).fetchall()
                if len(resultMix) == 0:
                    current_date += timedelta(days=1)
                    continue
                JobNameResults = defaultdict(
                    lambda: {'job_path': "", 'car_path': "", 'std_path': "", 'countNum': 0})
                for row in resultMix:
                    errname = row[0]
                    jobname = row[1]
                    if errname in ErrResult.keys() and jobname in ErrResult[errname].keys():
                        ErrResult[errname][jobname]['countNum'] += row[5]
                    else:
                        JobNameResults[jobname]['job_path'] = row[2]
                        JobNameResults[jobname]['car_path'] = row[3]
                        JobNameResults[jobname]['std_path'] = row[4]
                        JobNameResults[jobname]['countNum'] += row[5]
                if errname in ErrResult.keys():
                    ErrResult[errname].update(JobNameResults)
                else:
                    ErrResult[errname] = JobNameResults
            current_date += timedelta(days=1)
    for errname, jobs in ErrResult.items():
        ErrResult[errname] = {jobname: details for jobname, details in jobs.items()
                              if details['countNum'] / JobNum[jobname] >= ratio}
    keys_to_delete = [errname for errname, jobs in ErrResult.items() if not jobs]
    for key in keys_to_delete:
        del ErrResult[key]
    json_data = json.dumps(ErrResult, ensure_ascii=False)
    session.close()
    return json_data

def analyzeData(start_time, end_time, start_time_hour, end_time_hour, MacNum):
    res = {'allJobNum': 0, 'allPcbNum': 0, 'allFilter': 0, 'fateFilter': 0, 'allErrNum': 0,
            'alltrueNum': 0, 'allAiTrueNum': 0, 'avgPoint': 0, 'avgAiPoint': 0, 'top_job_data': [], 'top_job_err_rate': {}}
    filePath = exportcsvbyjob(start_time, end_time, start_time_hour, end_time_hour, MacNum)
    like_conditions = ' OR '.join([f"default_4 = '{code}'" for code in MacNum])
    if filePath and os.path.exists(filePath):
        if filePath.lower().endswith('.xlsx'):
            df = pd.read_excel(filePath, engine='openpyxl')
            if {'料号','假点过滤率','总点过滤率','总板数','AVI缺陷总数',
                'AVI真点总数','AI真点总数','平均报点','平均AI报点'}.issubset(df.columns):
                uniqueJob = df['料号'].dropna().unique()
                allJobNum = len(uniqueJob) - 1
                res['allJobNum'] = int(allJobNum)
                res['fateFilter'] = float(df['假点过滤率'].dropna().iloc[-1])
                res['allPcbNum'] = int(df['总板数'].dropna().iloc[-1])
                res['allFilter'] = float(df['总点过滤率'].dropna().iloc[-1])
                res['allErrNum'] = int(df['AVI缺陷总数'].dropna().iloc[-1])
                res['alltrueNum'] = int(df['AVI真点总数'].dropna().iloc[-1])
                res['allAiTrueNum'] = int(df['AI真点总数'].dropna().iloc[-1])
                res['avgPoint'] = float(df['平均报点'].dropna().iloc[-1])
                res['avgAiPoint'] = float(df['平均AI报点'].dropna().iloc[-1])
                df_cleaned = df.iloc[:-1]
                df_top10 = df_cleaned.sort_values(by='假点过滤率', ascending=True).head(10)
                top_job_data = df_top10['料号'].tolist()
                false_point_filter_rate = df_top10['假点过滤率'].tolist()
                total_filter_rate = df_top10['总点过滤率'].tolist()
                avg_report_point = df_top10['平均报点'].tolist()
                avg_ai_report_point = df_top10['平均AI报点'].tolist()
                res['top_job_data'] = top_job_data
                res['top_job_err_rate'] = {'false_point_filter_rate': false_point_filter_rate,'total_filter_rate': total_filter_rate,'avg_report_point': avg_report_point,'avg_ai_report_point': avg_ai_report_point}
        if os.path.exists(filePath):
            if filePath.lower().endswith('.xlsx'):
                os.remove(filePath)
    job_error_types = {}
    session = Session()
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    for job in res['top_job_data']:
        error_stats = []
        current_date = start_time
        while current_date <= end_time:
            table_name = f"tab_err_{current_date.strftime('%Y%m%d')[0:]}"
            if table_name in table_names:
                sql_query = text(f"""
                                select ai_err_type, COUNT(ai_err_type)
                                from {table_name}
                                WHERE ({like_conditions})
                                AND is_ai = 1
                                AND default_1 = '{job}'
                                GROUP BY ai_err_type
                                ORDER BY COUNT(ai_err_type) DESC
                                LIMIT 10
                            """)
                error_results = session.execute(sql_query).fetchall()
                for err_type, count in error_results:
                    found = False
                    for item in error_stats:
                        if item['type'] == err_type:
                            item['count'] += count
                            found = True
                            break
                    if not found:
                        error_stats.append({
                            'type': err_type,
                            'count': count
                        })
            current_date += timedelta(days=1)
        error_stats.sort(key=lambda x: x['count'], reverse=True)
        error_stats = error_stats[:10] 
        job_error_types[job] = error_stats

    res['job_error_types'] = job_error_types
    json_data = json.dumps(res, ensure_ascii=False)
    session.close()
    return json_data

def updateAnalyzeData(start_date, end_date, start_time_hour, end_time_hour, MacNum, days):
    time_ranges = []

    # 确保 start_date 和 end_date 类型一致 (转为 date 类型)
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    elif isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    if isinstance(end_date, datetime):
        end_date = end_date.date()
    elif isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    current_date = start_date  # 现在确保是 date 类型

    if days == 1:
        while current_date <= end_date:
            time_ranges.append((current_date.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d")))
            current_date += timedelta(days=1)
    elif days == 7:
        while current_date <= end_date:
            period_end = min(current_date + timedelta(days=6), end_date)
            time_ranges.append((current_date.strftime("%Y-%m-%d"), period_end.strftime("%Y-%m-%d")))
            current_date += timedelta(days=7)
    elif days == 30:
        while current_date <= end_date:
            # 计算当月最后一天
            if current_date.month == 12:
                next_month = datetime(current_date.year + 1, 1, 1) - timedelta(days=1)
                next_month = next_month.date()
            else:
                next_month = datetime(current_date.year, current_date.month + 1, 1) - timedelta(days=1)
                next_month = next_month.date()

            period_end = min(next_month, end_date)
            time_ranges.append((current_date.strftime("%Y-%m-%d"), period_end.strftime("%Y-%m-%d")))

            # 移至下个月第一天，确保使用 date 类型
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1).date()
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1).date()

    chart3Data = []  # 过滤率对比趋势图
    chart4Data = []  # 平均点数对比趋势图
    chart5Data = []  # 总点数对比趋势图

    for period_start, period_end in time_ranges:
        if isinstance(period_start, str):
            period_start_date = datetime.strptime(period_start, "%Y-%m-%d").date()
        else:
            period_start_date = period_start

        if isinstance(period_end, str):
            period_end_date = datetime.strptime(period_end, "%Y-%m-%d").date()
        else:
            period_end_date = period_end

        filePath = exportcsvbyjob(period_start_date, period_end_date, start_time_hour, end_time_hour, MacNum)

        if filePath and os.path.exists(filePath):
            if filePath.lower().endswith('.xlsx'):
                df = pd.read_excel(filePath, engine='openpyxl')
                required_columns = {'假点过滤率', '总点过滤率', 'AVI缺陷总数',
                                    'AI真点总数', '平均报点', '平均AI报点'}

                if any(col in df.columns for col in required_columns):
                    if days == 1:
                        period_label = datetime.strptime(period_start, "%Y-%m-%d").strftime("%m-%d")
                    else:
                        start_label = datetime.strptime(period_start, "%Y-%m-%d").strftime("%m-%d")
                        end_label = datetime.strptime(period_end, "%Y-%m-%d").strftime("%m-%d")
                        period_label = f"{start_label}~{end_label}"

                    false_filter_rate = float(df['假点过滤率'].dropna().iloc[-1]) if '假点过滤率' in df.columns and not \
                    df['假点过滤率'].dropna().empty else 0
                    total_filter_rate = float(df['总点过滤率'].dropna().iloc[-1]) if '总点过滤率' in df.columns and not \
                    df['总点过滤率'].dropna().empty else 0

                    chart3Data.append({
                        "name": period_label,
                        "假点过滤率": round(false_filter_rate, 2),
                        "总点过滤率": round(total_filter_rate, 2)
                    })

                    avg_point = float(df['平均报点'].dropna().iloc[-1]) if '平均报点' in df.columns and not df[
                        '平均报点'].dropna().empty else 0
                    avg_ai_point = float(df['平均AI报点'].dropna().iloc[-1]) if '平均AI报点' in df.columns and not df[
                        '平均AI报点'].dropna().empty else 0

                    chart4Data.append({
                        "name": period_label,
                        "平均报点": round(avg_point, 2),
                        "平均AI报点": round(avg_ai_point, 2)
                    })

                    total_defects = int(df['AVI缺陷总数'].dropna().iloc[-1]) if 'AVI缺陷总数' in df.columns and not df[
                        'AVI缺陷总数'].dropna().empty else 0
                    ai_true_defects = int(df['AI真点总数'].dropna().iloc[-1]) if 'AI真点总数' in df.columns and not df[
                        'AI真点总数'].dropna().empty else 0

                    chart5Data.append({
                        "name": period_label,
                        "缺陷总数": total_defects,
                        "AI真点总数": ai_true_defects
                    })
                os.remove(filePath)

    return {
        "chart3Data": chart3Data,
        "chart4Data": chart4Data,
        "chart5Data": chart5Data
    }