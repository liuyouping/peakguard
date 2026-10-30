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

# 直连数据库的通用操作

import pymysql, json
from datetime import datetime  

user = 'test'
pwd = '123456'
host = '127.0.0.1'
dbname = 'demo'
#connstr = 'mysql+pymysql://{0}:{1}@{2}:3306/{3}?charset=utf8'.format(user, pwd, host, dbname)


# ===== 辅助函数 =====
# cursor 转 json
def cursor2json(cur):
    row_headers=[x[0] for x in cur.description] #this will extract row headers
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    return json.dumps(json_data, cls=DateEncoder, ensure_ascii=False)  

# cursor 转 list
def cursor2list(cur):
    row_headers=[x[0] for x in cur.description] #this will extract row headers
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    return json_data

# 日期格式化类   
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)
# ===== end.

# ===== 减少 mysql 连接 ===== 

# 连接和游标变量
cursor = None
conn = None  

# 创建连接
def getConn():
    return pymysql.connect(host = host,user = user, password = pwd, db = dbname, charset = "utf8") 

# 关闭连接和游标
def close():
    if cursor:
        cursor.close()
    if conn:
        conn.close()

#
def getData(sql, params):
    conn = getConn()    
    cursor = conn.cursor()
    cursor.execute(sql, params)
    return cursor                                   # 尚未关闭 cursor

#
def getJson(sql, params):
    conn = getConn()                                # 创建连接 conn
    cursor = conn.cursor()                          # 创建游标 cursor
    cursor.execute(sql, params)                     # 执行 sql 语句
    ret = cursor2json(cursor)                       # 转成 json(字符) 格式
    close()                                         # 及时关闭 conn 及 cursor
    return ret      


#
def getList(sql, params):
    conn = getConn()                                # 创建连接 conn
    cursor = conn.cursor()                          # 创建游标 cursor
    cursor.execute(sql, params)                     # 执行 sql 语句
    ret = cursor2list(cursor)                       # 转成 json(对象) 格式
    close()                                         # 及时关闭 conn 及 cursor
    return ret  

# 
def execSql(sql, params):
    conn = getConn()                                # 创建连接 conn
    cursor = conn.cursor()                          # 创建游标 cursor
    try:
        ret = cursor.execute(sql, params)           # 执行 sql 语句
        conn.commit()
        close()                                     # 及时关闭 conn 及 cursor
        return ret
    except Exception as e:
        conn.rollback()
        close()
        return 0


