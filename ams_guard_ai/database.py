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

import sqlite3
import pandas as pd
import pymysql

class DatabaseManager:
    def __init__(self, db_path='snow_guard_ams.db'):
        self.db_path = db_path
        self.conn = None
    
    # 修改database.py中的connect方法
    def connect(self):
        """连接MySQL数据库"""
        self.conn = pymysql.connect(
            host='IP',
            port=3306,
            user='test',
            password='123456',
            db='superdemo',  # 数据库名称
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"✅ 已连接到MySQL数据库: ")
        return self.conn
    
    
    def get_table_info(self):
        """获取表信息"""
        cursor = self.conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        
        print("\n📊 数据库表信息:")
        for table in tables:
            # 使用字典键获取表名，键名格式为 Tables_in_数据库名
            table_name = list(table.values())[0]
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            print(f"  {table_name}: {count} 条记录")
    
    def get_sample_data(self, table_name, limit=5):
        """获取样本数据"""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        df = pd.read_sql_query(query, self.conn)
        return df
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("🔒 数据库连接已关闭")