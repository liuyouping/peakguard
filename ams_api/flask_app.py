# Copyright (C) 2026 PeakGuard Team
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A small Test application to show how to use Flask-MQTT.
"""
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_mqtt import Mqtt
import requests as reqserver
import json, hashlib, time, datetime
from datetime import datetime
import db_comm as dbComm
import math


## ===== 程序启动，参数设置 =====  add by: liuyp@2025-02-15

# flask 服务
app = Flask(__name__)


# 统一返回格式
def make_response(code, msg="", data=None):
    return json.dumps({"code": code, "msg": msg, "data": data}, ensure_ascii=False)


## ===== 原有接口 =====  add by: liuyp@2025-02-15

# APP用户登录
@app.route('/oper/auth', methods=['post'])
def operAuth():
    params = request.get_json()
    operId = params.get("id")
    operPwd = params.get('pwd')

    if not operId or not operPwd:
        return make_response(10001, '参数不能为空！')

    sql = "select operName, email as userId, msg as deviceNo, mobile as cityId from syst_oper where operId = %s and operPwd = %s"
    data = dbComm.getList(sql, (operId, operPwd))
    if not data:
        return make_response(10002, '账号或密码错误')
    return make_response(10000, '登录成功', data)


# 查询城市气温
@app.route('/city/temp', methods=['post'])
def cityTemp():
    params = request.get_json()
    cityId = params.get('cityId')
    measureDate = params.get('measureDate')

    if not cityId or not measureDate:
        return make_response(10001, '参数不能为空！')

    sql = """
        select t.measureDate, t.cityId, c.cityName, t.temp as maxTemp, t.temp as minTemp, t.oxygen, c.altitude
        from ams_city_temp as t
        right join ams_city as c on t.cityId = c.cityId
        where t.cityId = %s and t.measureDate = %s
    """
    data = dbComm.getList(sql, (cityId, measureDate))
    return make_response(10000, '查询成功', data)


# 查询用户体征数据
@app.route('/user/vital', methods=['post'])
def userVital():
    params = request.get_json()
    userId = params.get('userId')
    measureDate = params.get('measureDate')

    if not userId or not measureDate:
        return make_response(10001, '参数不能为空！')

    sql = "select * from ams_vital_data where userId = %s and measureDate = %s"
    data = dbComm.getList(sql, (userId, measureDate))
    return make_response(10000, '查询成功', data)


# 查询用户风险数据
@app.route('/user/risk', methods=['post'])
def userRisk():
    params = request.get_json()
    userId = params.get('userId')
    reportDate = params.get('reportDate')

    if not userId or not reportDate:
        return make_response(10001, '参数不能为空！')

    sql = "select * from ams_user_risk where userId = %s and reportDate = %s"
    data = dbComm.getList(sql, (userId, reportDate))
    return make_response(10000, '查询成功', data)


# 查询设备列表
@app.route('/device/query', methods=['post'])
def deviceList():   
    err = {'code': 9999} 
    params = request.get_json()       # 传入 body 参数

    deviceType = params['deviceType']  

    if deviceType:  
        sql = "select * from  v_device where deviceType = %s "
        return dbComm.getJson(sql, (deviceType))    
    else:
        err = {'code': 10001, 'msg': '参数不能为空！'}
        return json.dumps(err, ensure_ascii=False)


# 查询单个设备
@app.route('/device/one', methods=['post'])
def deviceOne():
    params = request.get_json()
    deviceNo = params.get('deviceNo')
    if not deviceNo:
        return make_response(10001, '参数不能为空！')
    sql = "select * from busi_device where deviceNo = %s"
    data = dbComm.getJson(sql, (deviceNo))
    return make_response(10000, '查询成功', data)


# 查询设备报警记录
@app.route('/alarm/query', methods=['post'])
def alarmList():
    params = request.get_json()
    alarmType = params.get('alarmType')
    if not alarmType:
        return make_response(10001, '参数不能为空！')
    sql = "select * from busi_device_alarm where alarmType = %s order by alarmTime"
    data = dbComm.getJson(sql, (alarmType))
    return make_response(10000, '查询成功', data)


# 新增设备报警记录
@app.route('/alarm/add', methods=['post'])
def alarmAdd():
    params = request.get_json()
    deviceNo = params.get('deviceNo')
    alarmType = params.get('alarmType')
    alarmDesc = params.get('alarmDesc')

    if not deviceNo or not alarmType or not alarmDesc:
        return make_response(10001, '参数不能为空！')

    sql = "insert into busi_device_alarm(deviceNo, alarmType, alarmDesc, alarmTime) values(%s, %s, %s, %s)"
    ret = dbComm.execSql(sql, (deviceNo, alarmType, alarmDesc, datetime.now()))
    if ret == 1:
        # 返回最新设备信息
        data = dbComm.getJson("select * from busi_device where deviceNo = %s", (deviceNo))
        return make_response(10000, '添加成功', data)
    else:
        return make_response(10003, '添加失败')


# 更新报警记录（处理）
@app.route('/alarm/update', methods=['post'])
def alarmUpdate():
    params = request.get_json()
    alarmId = params.get('id')
    if not alarmId:
        return make_response(10001, '参数不能为空！')
    sql = "update busi_device_alarm set processStatus = 1 where id = %s"
    ret = dbComm.execSql(sql, (alarmId))
    if ret == 1:
        return make_response(10000, '修改成功')
    else:
        return make_response(10003, '修改失败')


# 查询预警规则
@app.route('/rule/query', methods=['post'])
def ruleList():
    sql = "select * from busi_alarm_rule order by id"
    data = dbComm.getJson(sql, ())
    return make_response(10000, '查询成功', data)


## ===== 新增接口：覆盖所有主要表的CRUD =====  add by: wjh@2026-03-26

# -------------------- ams_city 城市信息 --------------------
@app.route('/city/list', methods=['post'])
def city_list():
    """城市列表查询"""
    params = request.get_json() or {}
    cityId = params.get('cityId')
    cityName = params.get('cityName')
    sql = "select * from ams_city where 1=1"
    args = []
    if cityId:
        sql += " and cityId = %s"
        args.append(cityId)
    if cityName:
        sql += " and cityName like %s"
        args.append(f"%{cityName}%")
    data = dbComm.getList(sql, tuple(args))
    return make_response(10000, '查询成功', data)


@app.route('/city/add', methods=['post'])
def city_add():
    """新增城市"""
    params = request.get_json()
    cityId = params.get('cityId')
    cityName = params.get('cityName')
    altitude = params.get('altitude')
    if not cityId or not cityName:
        return make_response(10001, 'cityId和cityName不能为空')
    sql = "insert into ams_city(cityId, cityName, altitude) values(%s, %s, %s)"
    ret = dbComm.execSql(sql, (cityId, cityName, altitude))
    if ret:
        return make_response(10000, '添加成功')
    return make_response(10003, '添加失败')


@app.route('/city/update', methods=['post'])
def city_update():
    """修改城市信息"""
    params = request.get_json()
    cityId = params.get('cityId')
    if not cityId:
        return make_response(10001, 'cityId不能为空')
    updates = []
    args = []
    if 'cityName' in params:
        updates.append("cityName=%s")
        args.append(params['cityName'])
    if 'altitude' in params:
        updates.append("altitude=%s")
        args.append(params['altitude'])
    if not updates:
        return make_response(10001, '没有需要更新的字段')
    args.append(cityId)
    sql = f"update ams_city set {','.join(updates)} where cityId=%s"
    ret = dbComm.execSql(sql, tuple(args))
    if ret:
        return make_response(10000, '修改成功')
    return make_response(10003, '修改失败')


@app.route('/city/delete', methods=['post'])
def city_delete():
    """删除城市"""
    params = request.get_json()
    cityId = params.get('cityId')
    if not cityId:
        return make_response(10001, 'cityId不能为空')
    sql = "delete from ams_city where cityId=%s"
    ret = dbComm.execSql(sql, (cityId))
    if ret:
        return make_response(10000, '删除成功')
    return make_response(10003, '删除失败')


# -------------------- ams_city_temp 城市气温氧气 --------------------
@app.route('/citytemp/list', methods=['post'])
def citytemp_list():
    """气温氧气数据列表"""
    params = request.get_json() or {}
    cityId = params.get('cityId')
    startDate = params.get('startDate')
    endDate = params.get('endDate')
    sql = "select * from ams_city_temp where 1=1"
    args = []
    if cityId:
        sql += " and cityId=%s"
        args.append(cityId)
    if startDate:
        sql += " and measureDate>=%s"
        args.append(startDate)
    if endDate:
        sql += " and measureDate<=%s"
        args.append(endDate)
    data = dbComm.getList(sql, tuple(args))
    return make_response(10000, '查询成功', data)


@app.route('/citytemp/add', methods=['post'])
def citytemp_add():
    """新增气温氧气记录"""
    params = request.get_json()
    cityId = params.get('cityId')
    measureDate = params.get('measureDate')
    temp = params.get('temp')
    oxygen = params.get('oxygen')
    if not cityId or not measureDate:
        return make_response(10001, 'cityId和measureDate不能为空')
    sql = "insert into ams_city_temp(cityId, measureDate, temp, oxygen) values(%s, %s, %s, %s)"
    ret = dbComm.execSql(sql, (cityId, measureDate, temp, oxygen))
    if ret:
        return make_response(10000, '添加成功')
    return make_response(10003, '添加失败')


@app.route('/citytemp/update', methods=['post'])
def citytemp_update():
    """修改气温氧气记录"""
    params = request.get_json()
    id_ = params.get('id')
    if not id_:
        return make_response(10001, 'id不能为空')
    updates = []
    args = []
    if 'temp' in params:
        updates.append("temp=%s")
        args.append(params['temp'])
    if 'oxygen' in params:
        updates.append("oxygen=%s")
        args.append(params['oxygen'])
    if not updates:
        return make_response(10001, '没有需要更新的字段')
    args.append(id_)
    sql = f"update ams_city_temp set {','.join(updates)} where id=%s"
    ret = dbComm.execSql(sql, tuple(args))
    if ret:
        return make_response(10000, '修改成功')
    return make_response(10003, '修改失败')


@app.route('/citytemp/delete', methods=['post'])
def citytemp_delete():
    """删除气温氧气记录"""
    params = request.get_json()
    id_ = params.get('id')
    if not id_:
        return make_response(10001, 'id不能为空')
    sql = "delete from ams_city_temp where id=%s"
    ret = dbComm.execSql(sql, (id_))
    if ret:
        return make_response(10000, '删除成功')
    return make_response(10003, '删除失败')


# -------------------- ams_user 用户信息 --------------------
@app.route('/user/list', methods=['post'])
def user_list():
    params = request.get_json() or {}
    userId = params.get('userId')
    userName = params.get('userName')
    sql = "select * from ams_user where 1=1"
    args = []
    if userId:
        sql += " and userId=%s"
        args.append(userId)
    if userName:
        sql += " and userName like %s"
        args.append(f"%{userName}%")
    data = dbComm.getList(sql, tuple(args))
    return make_response(10000, '查询成功', data)


@app.route('/user/add', methods=['post'])
def user_add():
    params = request.get_json()
    userId = params.get('userId')
    userName = params.get('userName')
    age = params.get('age')
    gender = params.get('gender')
    if not userId or not userName:
        return make_response(10001, 'userId和userName不能为空')
    sql = "insert into ams_user(userId, userName, age, gender) values(%s, %s, %s, %s)"
    ret = dbComm.execSql(sql, (userId, userName, age, gender))
    if ret:
        return make_response(10000, '添加成功')
    return make_response(10003, '添加失败')


@app.route('/user/update', methods=['post'])
def user_update():
    params = request.get_json()
    userId = params.get('userId')
    if not userId:
        return make_response(10001, 'userId不能为空')
    updates = []
    args = []
    if 'userName' in params:
        updates.append("userName=%s")
        args.append(params['userName'])
    if 'age' in params:
        updates.append("age=%s")
        args.append(params['age'])
    if 'gender' in params:
        updates.append("gender=%s")
        args.append(params['gender'])
    if not updates:
        return make_response(10001, '没有需要更新的字段')
    args.append(userId)
    sql = f"update ams_user set {','.join(updates)} where userId=%s"
    ret = dbComm.execSql(sql, tuple(args))
    if ret:
        return make_response(10000, '修改成功')
    return make_response(10003, '修改失败')


@app.route('/user/delete', methods=['post'])
def user_delete():
    params = request.get_json()
    userId = params.get('userId')
    if not userId:
        return make_response(10001, 'userId不能为空')
    sql = "delete from ams_user where userId=%s"
    ret = dbComm.execSql(sql, (userId))
    if ret:
        return make_response(10000, '删除成功')
    return make_response(10003, '删除失败')


# -------------------- ams_vital_data 体征数据 --------------------
@app.route('/vital/list', methods=['post'])
def vital_list():
    params = request.get_json() or {}
    userId = params.get('userId')
    startDate = params.get('startDate')
    endDate = params.get('endDate')
    sql = "select * from ams_vital_data where 1=1"
    args = []
    if userId:
        sql += " and userId=%s"
        args.append(userId)
    if startDate:
        sql += " and measureDate>=%s"
        args.append(startDate)
    if endDate:
        sql += " and measureDate<=%s"
        args.append(endDate)
    data = dbComm.getList(sql, tuple(args))
    return make_response(10000, '查询成功', data)


@app.route('/vital/add', methods=['post'])
def vital_add():
    params = request.get_json()
    userId = params.get('userId')
    measureDate = params.get('measureDate')
    if not userId or not measureDate:
        return make_response(10001, 'userId和measureDate不能为空')
    sql = """insert into ams_vital_data(userId, measureDate, SpO2, SBP, DBP, sleep_quality, heart, breath)
             values(%s, %s, %s, %s, %s, %s, %s, %s)"""
    ret = dbComm.execSql(sql, (
        userId, measureDate,
        params.get('SpO2'), params.get('SBP'), params.get('DBP'),
        params.get('sleep_quality'), params.get('heart'), params.get('breath')
    ))
    if ret:
        return make_response(10000, '添加成功')
    return make_response(10003, '添加失败')


@app.route('/vital/update', methods=['post'])
def vital_update():
    params = request.get_json()
    id_ = params.get('id')
    if not id_:
        return make_response(10001, 'id不能为空')
    updates = []
    args = []
    for field in ['SpO2', 'SBP', 'DBP', 'sleep_quality', 'heart', 'breath']:
        if field in params:
            updates.append(f"{field}=%s")
            args.append(params[field])
    if not updates:
        return make_response(10001, '没有需要更新的字段')
    args.append(id_)
    sql = f"update ams_vital_data set {','.join(updates)} where id=%s"
    ret = dbComm.execSql(sql, tuple(args))
    if ret:
        return make_response(10000, '修改成功')
    return make_response(10003, '修改失败')


@app.route('/vital/delete', methods=['post'])
def vital_delete():
    params = request.get_json()
    id_ = params.get('id')
    if not id_:
        return make_response(10001, 'id不能为空')
    sql = "delete from ams_vital_data where id=%s"
    ret = dbComm.execSql(sql, (id_))
    if ret:
        return make_response(10000, '删除成功')
    return make_response(10003, '删除失败')


# -------------------- ams_user_risk 高反风险 --------------------
@app.route('/risk/list', methods=['post'])
def risk_list():
    params = request.get_json() or {}
    userId = params.get('userId')
    startDate = params.get('startDate')
    endDate = params.get('endDate')
    sql = "select * from ams_user_risk where 1=1"
    args = []
    if userId:
        sql += " and userId=%s"
        args.append(userId)
    if startDate:
        sql += " and reportDate>=%s"
        args.append(startDate)
    if endDate:
        sql += " and reportDate<=%s"
        args.append(endDate)
    data = dbComm.getList(sql, tuple(args))
    return make_response(10000, '查询成功', data)


@app.route('/risk/add', methods=['post'])
def risk_add():
    params = request.get_json()
    userId = params.get('userId')
    reportDate = params.get('reportDate')
    if not userId or not reportDate:
        return make_response(10001, 'userId和reportDate不能为空')
    sql = "insert into ams_user_risk(userId, reportDate, riskLevel, riskReport) values(%s, %s, %s, %s)"
    ret = dbComm.execSql(sql, (userId, reportDate, params.get('riskLevel'), params.get('riskReport')))
    if ret:
        return make_response(10000, '添加成功')
    return make_response(10003, '添加失败')


@app.route('/risk/update', methods=['post'])
def risk_update():
    params = request.get_json()
    id_ = params.get('id')
    if not id_:
        return make_response(10001, 'id不能为空')
    updates = []
    args = []
    if 'riskLevel' in params:
        updates.append("riskLevel=%s")
        args.append(params['riskLevel'])
    if 'riskReport' in params:
        updates.append("riskReport=%s")
        args.append(params['riskReport'])
    if not updates:
        return make_response(10001, '没有需要更新的字段')
    args.append(id_)
    sql = f"update ams_user_risk set {','.join(updates)} where id=%s"
    ret = dbComm.execSql(sql, tuple(args))
    if ret:
        return make_response(10000, '修改成功')
    return make_response(10003, '修改失败')


@app.route('/risk/delete', methods=['post'])
def risk_delete():
    params = request.get_json()
    id_ = params.get('id')
    if not id_:
        return make_response(10001, 'id不能为空')
    sql = "delete from ams_user_risk where id=%s"
    ret = dbComm.execSql(sql, (id_))
    if ret:
        return make_response(10000, '删除成功')
    return make_response(10003, '删除失败')


# -------------------- busi_device 设备管理 --------------------
@app.route('/busi/device/list', methods=['post'])
def busi_device_list():
    params = request.get_json() or {}
    deviceNo = params.get('deviceNo')
    productNo = params.get('productNo')
    sql = "select * from busi_device where 1=1"
    args = []
    if deviceNo:
        sql += " and deviceNo=%s"
        args.append(deviceNo)
    if productNo:
        sql += " and productNo=%s"
        args.append(productNo)
    data = dbComm.getList(sql, tuple(args))
    return make_response(10000, '查询成功', data)


@app.route('/busi/device/add', methods=['post'])
def busi_device_add():
    params = request.get_json()
    deviceNo = params.get('deviceNo')
    if not deviceNo:
        return make_response(10001, 'deviceNo不能为空')
    sql = """insert into busi_device(deviceNo, appNo, productNo, netNo, onStatus, appVersion, chipVersion, status, msg, createId, createTime)
             values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    ret = dbComm.execSql(sql, (
        deviceNo, params.get('appNo'), params.get('productNo'), params.get('netNo'),
        params.get('onStatus', 0), params.get('appVersion'), params.get('chipVersion'),
        params.get('status', 1), params.get('msg'), params.get('createId'), datetime.now()
    ))
    if ret:
        return make_response(10000, '添加成功')
    return make_response(10003, '添加失败')


@app.route('/busi/device/update', methods=['post'])
def busi_device_update():
    params = request.get_json()
    deviceNo = params.get('deviceNo')
    if not deviceNo:
        return make_response(10001, 'deviceNo不能为空')
    updates = []
    args = []
    for field in ['appNo', 'productNo', 'netNo', 'onStatus', 'onTime', 'offTime', 'appVersion', 'chipVersion', 'status', 'msg', 'updateId']:
        if field in params:
            updates.append(f"{field}=%s")
            args.append(params[field])
    if not updates:
        return make_response(10001, '没有需要更新的字段')
    updates.append("updateTime=%s")
    args.append(datetime.now())
    args.append(deviceNo)
    sql = f"update busi_device set {','.join(updates)} where deviceNo=%s"
    ret = dbComm.execSql(sql, tuple(args))
    if ret:
        return make_response(10000, '修改成功')
    return make_response(10003, '修改失败')


@app.route('/busi/device/delete', methods=['post'])
def busi_device_delete():
    params = request.get_json()
    deviceNo = params.get('deviceNo')
    if not deviceNo:
        return make_response(10001, 'deviceNo不能为空')
    sql = "delete from busi_device where deviceNo=%s"
    ret = dbComm.execSql(sql, (deviceNo))
    if ret:
        return make_response(10000, '删除成功')
    return make_response(10003, '删除失败')


# -------------------- busi_device_topic 设备主题 --------------------
@app.route('/busi/topic/list', methods=['post'])
def busi_topic_list():
    params = request.get_json() or {}
    deviceNo = params.get('deviceNo')
    productNo = params.get('productNo')
    sql = "select * from busi_device_topic where 1=1"
    args = []
    if deviceNo:
        sql += " and deviceNo=%s"
        args.append(deviceNo)
    if productNo:
        sql += " and productNo=%s"
        args.append(productNo)
    data = dbComm.getList(sql, tuple(args))
    return make_response(10000, '查询成功', data)


@app.route('/busi/topic/add', methods=['post'])
def busi_topic_add():
    params = request.get_json()
    deviceNo = params.get('deviceNo')
    topicNo = params.get('topicNo')
    topicName = params.get('topicName')
    if not deviceNo or not topicNo or not topicName:
        return make_response(10001, 'deviceNo, topicNo, topicName不能为空')
    sql = """insert into busi_device_topic(productNo, deviceNo, topicNo, topicName, topicDesc, payload, status, msg, createId, createTime)
             values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    ret = dbComm.execSql(sql, (
        params.get('productNo'), deviceNo, topicNo, topicName,
        params.get('topicDesc'), params.get('payload'), params.get('status', 1),
        params.get('msg'), params.get('createId'), datetime.now()
    ))
    if ret:
        return make_response(10000, '添加成功')
    return make_response(10003, '添加失败')


@app.route('/busi/topic/update', methods=['post'])
def busi_topic_update():
    params = request.get_json()
    id_ = params.get('id')
    if not id_:
        return make_response(10001, 'id不能为空')
    updates = []
    args = []
    for field in ['topicName', 'topicDesc', 'payload', 'status', 'msg', 'updateId']:
        if field in params:
            updates.append(f"{field}=%s")
            args.append(params[field])
    if not updates:
        return make_response(10001, '没有需要更新的字段')
    updates.append("updateTime=%s")
    args.append(datetime.now())
    args.append(id_)
    sql = f"update busi_device_topic set {','.join(updates)} where id=%s"
    ret = dbComm.execSql(sql, tuple(args))
    if ret:
        return make_response(10000, '修改成功')
    return make_response(10003, '修改失败')


@app.route('/busi/topic/delete', methods=['post'])
def busi_topic_delete():
    params = request.get_json()
    id_ = params.get('id')
    if not id_:
        return make_response(10001, 'id不能为空')
    sql = "delete from busi_device_topic where id=%s"
    ret = dbComm.execSql(sql, (id_))
    if ret:
        return make_response(10000, '删除成功')
    return make_response(10003, '删除失败')


# -------------------- busi_device_subscribe 订阅记录 --------------------
@app.route('/busi/subscribe/list', methods=['post'])
def busi_subscribe_list():
    params = request.get_json() or {}
    deviceNo = params.get('deviceNo')
    clientId = params.get('clientId')
    sql = "select * from busi_device_subscribe where 1=1"
    args = []
    if deviceNo:
        sql += " and deviceNo=%s"
        args.append(deviceNo)
    if clientId:
        sql += " and clientId=%s"
        args.append(clientId)
    data = dbComm.getList(sql, tuple(args))
    return make_response(10000, '查询成功', data)


@app.route('/busi/subscribe/add', methods=['post'])
def busi_subscribe_add():
    params = request.get_json()
    deviceNo = params.get('deviceNo')
    topic = params.get('topic')
    if not deviceNo or not topic:
        return make_response(10001, 'deviceNo和topic不能为空')
    sql = """insert into busi_device_subscribe(deviceNo, clientId, topic, subscribedType, topicTimeStamp, msg, createTime)
             values(%s, %s, %s, %s, %s, %s, %s)"""
    ret = dbComm.execSql(sql, (
        deviceNo, params.get('clientId'), topic, params.get('subscribedType', 1),
        params.get('topicTimeStamp', datetime.now().strftime('%Y%m%d%H%M%S')),
        params.get('msg'), datetime.now()
    ))
    if ret:
        return make_response(10000, '添加成功')
    return make_response(10003, '添加失败')


@app.route('/busi/subscribe/delete', methods=['post'])
def busi_subscribe_delete():
    params = request.get_json()
    id_ = params.get('id')
    if not id_:
        return make_response(10001, 'id不能为空')
    sql = "delete from busi_device_subscribe where id=%s"
    ret = dbComm.execSql(sql, (id_))
    if ret:
        return make_response(10000, '删除成功')
    return make_response(10003, '删除失败')


# -------------------- busi_device_cmd 指令记录 --------------------
@app.route('/busi/cmd/list', methods=['post'])
def busi_cmd_list():
    params = request.get_json() or {}
    deviceNo = params.get('deviceNo')
    clientId = params.get('clientId')
    sql = "select * from busi_device_cmd where 1=1"
    args = []
    if deviceNo:
        sql += " and deviceNo=%s"
        args.append(deviceNo)
    if clientId:
        sql += " and clientId=%s"
        args.append(clientId)
    data = dbComm.getList(sql, tuple(args))
    return make_response(10000, '查询成功', data)


@app.route('/busi/cmd/add', methods=['post'])
def busi_cmd_add():
    params = request.get_json()
    deviceNo = params.get('deviceNo')
    topic = params.get('topic')
    cmdCode = params.get('cmdCode')
    cmdContent = params.get('cmdContent')
    cmdOperator = params.get('cmdOperator')
    if not deviceNo or not topic or not cmdCode or not cmdContent or not cmdOperator:
        return make_response(10001, 'deviceNo, topic, cmdCode, cmdContent, cmdOperator不能为空')
    sql = """insert into busi_device_cmd(deviceNo, clientId, topic, cmdCode, cmdContent, cmdOperator, reqId, reqTime, createTime)
             values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    ret = dbComm.execSql(sql, (
        deviceNo, params.get('clientId'), topic, cmdCode, cmdContent, cmdOperator,
        params.get('reqId'), params.get('reqTime', datetime.now()), datetime.now()
    ))
    if ret:
        return make_response(10000, '添加成功')
    return make_response(10003, '添加失败')


@app.route('/busi/cmd/update', methods=['post'])
def busi_cmd_update():
    params = request.get_json()
    id_ = params.get('id')
    if not id_:
        return make_response(10001, 'id不能为空')
    updates = []
    args = []
    for field in ['reqResult', 'rspTime', 'rspResult']:
        if field in params:
            updates.append(f"{field}=%s")
            args.append(params[field])
    if not updates:
        return make_response(10001, '没有需要更新的字段')
    args.append(id_)
    sql = f"update busi_device_cmd set {','.join(updates)} where id=%s"
    ret = dbComm.execSql(sql, tuple(args))
    if ret:
        return make_response(10000, '修改成功')
    return make_response(10003, '修改失败')


@app.route('/busi/cmd/delete', methods=['post'])
def busi_cmd_delete():
    params = request.get_json()
    id_ = params.get('id')
    if not id_:
        return make_response(10001, 'id不能为空')
    sql = "delete from busi_device_cmd where id=%s"
    ret = dbComm.execSql(sql, (id_))
    if ret:
        return make_response(10000, '删除成功')
    return make_response(10003, '删除失败')


# -------------------- busi_device_report 报文记录 --------------------
@app.route('/busi/report/list', methods=['post'])
def busi_report_list():
    params = request.get_json() or {}
    deviceNo = params.get('deviceNo')
    clientId = params.get('clientId')
    sql = "select * from busi_device_report where 1=1"
    args = []
    if deviceNo:
        sql += " and deviceNo=%s"
        args.append(deviceNo)
    if clientId:
        sql += " and clientId=%s"
        args.append(clientId)
    data = dbComm.getList(sql, tuple(args))
    return make_response(10000, '查询成功', data)


@app.route('/busi/report/add', methods=['post'])
def busi_report_add():
    params = request.get_json()
    deviceNo = params.get('deviceNo')
    topic = params.get('topic')
    reportText = params.get('reportText')
    if not deviceNo or not topic or not reportText:
        return make_response(10001, 'deviceNo, topic, reportText不能为空')
    sql = "insert into busi_device_report(deviceNo, clientId, topic, reportText, msg, createTime) values(%s, %s, %s, %s, %s, %s)"
    ret = dbComm.execSql(sql, (
        deviceNo, params.get('clientId'), topic, reportText,
        params.get('msg'), datetime.now()
    ))
    if ret:
        return make_response(10000, '添加成功')
    return make_response(10003, '添加失败')


@app.route('/busi/report/delete', methods=['post'])
def busi_report_delete():
    params = request.get_json()
    id_ = params.get('id')
    if not id_:
        return make_response(10001, 'id不能为空')
    sql = "delete from busi_device_report where id=%s"
    ret = dbComm.execSql(sql, (id_))
    if ret:
        return make_response(10000, '删除成功')
    return make_response(10003, '删除失败')


# -------------------- busi_device_data 报文数据 --------------------
@app.route('/busi/data/list', methods=['post'])
def busi_data_list():
    params = request.get_json() or {}
    deviceNo = params.get('deviceNo')
    propertyCmd = params.get('propertyCmd')
    sql = "select * from busi_device_data where 1=1"
    args = []
    if deviceNo:
        sql += " and deviceNo=%s"
        args.append(deviceNo)
    if propertyCmd:
        sql += " and propertyCmd=%s"
        args.append(propertyCmd)
    data = dbComm.getList(sql, tuple(args))
    return make_response(10000, '查询成功', data)


@app.route('/busi/data/add', methods=['post'])
def busi_data_add():
    params = request.get_json()
    deviceNo = params.get('deviceNo')
    if not deviceNo:
        return make_response(10001, 'deviceNo不能为空')
    sql = """insert into busi_device_data(deviceNo, serviceId, propertyCmd, propertyValue, propertyResult, propertyAction, eventTime, createTime)
             values(%s, %s, %s, %s, %s, %s, %s, %s)"""
    ret = dbComm.execSql(sql, (
        deviceNo, params.get('serviceId'), params.get('propertyCmd'), params.get('propertyValue'),
        params.get('propertyResult'), params.get('propertyAction'), params.get('eventTime'), datetime.now()
    ))
    if ret:
        return make_response(10000, '添加成功')
    return make_response(10003, '添加失败')


@app.route('/busi/data/delete', methods=['post'])
def busi_data_delete():
    params = request.get_json()
    id_ = params.get('id')
    if not id_:
        return make_response(10001, 'id不能为空')
    sql = "delete from busi_device_data where id=%s"
    ret = dbComm.execSql(sql, (id_))
    if ret:
        return make_response(10000, '删除成功')
    return make_response(10003, '删除失败')


## ===== 项目启动 =====  add by: liuyp@2026-2-15

if __name__ == '__main__': 
    ##app.run(host='127.0.0.1', port=5060, debug=True)
    app.run(host='0.0.0.0', port=5060, debug=True)