# Copyright (C) 2026 PeakGuard Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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