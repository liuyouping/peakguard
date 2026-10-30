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

import pandas as pd
import numpy as np

class DataGenerator:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.feature_names = ['SpO2', 'HR', 'RR', 'SBP', 'DBP', 'altitude', 'temperature', 'sleep_quality']
    
    def generate_users_data(self, n_users=50):
        """生成用户数据"""
        print("🔄 正在生成用户数据...")
        
        # 生成中文姓名
        first_names = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴']
        second_names = ['明', '红', '军', '芳', '伟', '丽', '娜', '涛', '强', '静']
        
        cursor = self.db_manager.conn.cursor()
        
        # 先删除子表中的数据，避免外键约束错误
        cursor.execute("DELETE FROM physiological_data")
        cursor.execute("DELETE FROM warnings")
        cursor.execute("DELETE FROM emergency_contacts")
        cursor.execute("DELETE FROM team_members")
        cursor.execute("DELETE FROM teams")
        cursor.execute("DELETE FROM scenario_records")
        cursor.execute("DELETE FROM alert_history")
        cursor.execute("DELETE FROM rescue_requests")
        cursor.execute("DELETE FROM health_reports")
        
        # 清空现有用户数据
        cursor.execute("DELETE FROM users")
        
        users_data = []
        for i in range(n_users):
            # 生成随机姓名
            name = np.random.choice(first_names) + np.random.choice(second_names)
            
            # 生成随机电话号码
            phone = f"13{np.random.randint(0, 10)}{np.random.randint(0, 10)}{np.random.randint(0, 10)}{np.random.randint(0, 10)}{np.random.randint(0, 10)}{np.random.randint(0, 10)}{np.random.randint(0, 10)}{np.random.randint(0, 10)}"
            
            age = np.random.randint(20, 65)
            gender = np.random.choice(['M', 'F'])
            
            # 插入数据
            cursor.execute("""
                INSERT INTO users (name, phone, age, gender, altitude, heart_rate, blood_oxygen, respiratory_rate, risk_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, phone, age, gender, 0, 0, 0, 0, 0))
            
            users_data.append({
                'name': name,
                'age': age,
                'gender': gender,
                'phone': phone
            })
        
        self.db_manager.conn.commit()
        users_df = pd.DataFrame(users_data)
        print(f"✅ 已生成 {n_users} 条用户数据")
        return users_df
    
    def generate_physiological_data(self, n_samples=1000):
        """生成生理数据"""
        print("🔄 正在生成生理数据...")
        
        np.random.seed(42)
        physiological_data = []
        
        cursor = self.db_manager.conn.cursor()
        
        # 清空现有数据
        cursor.execute("DELETE FROM physiological_data")
        
        # 获取实际的用户ID列表
        cursor.execute("SELECT user_id FROM users")
        user_ids = [row['user_id'] for row in cursor.fetchall()]
        
        if not user_ids:
            print("❌ 没有找到用户数据，无法生成生理数据")
            return pd.DataFrame()
        
        for i in range(n_samples):
            user_id = np.random.choice(user_ids)  # 从实际用户ID中随机选择
            altitude = np.random.uniform(2000, 5500)
            
            # 基础生理参数
            base_SpO2 = np.random.normal(98, 1)
            base_HR = np.random.normal(75, 8)
            base_RR = np.random.normal(16, 2)
            base_SBP = np.random.normal(120, 10)
            base_DBP = np.random.normal(80, 8)
            
            # 海拔影响
            altitude_effect = (altitude - 2000) / 3500
            
            # 高原环境下的生理变化
            SpO2 = base_SpO2 - altitude_effect * np.random.uniform(5, 15)
            HR = base_HR + altitude_effect * np.random.uniform(5, 25)
            RR = base_RR + altitude_effect * np.random.uniform(2, 10)
            SBP = base_SBP + altitude_effect * np.random.uniform(0, 20)
            DBP = base_DBP + altitude_effect * np.random.uniform(0, 15)
            
            # 环境参数
            temperature = 20 - altitude_effect * 15 + np.random.normal(0, 3)
            sleep_quality = 8 - altitude_effect * 4 + np.random.normal(0, 1.5)
            sleep_quality = max(0, min(10, sleep_quality))
            
            # 计算风险等级
            AMS_risk = self._calculate_risk_level(SpO2, HR, RR, SBP, DBP, sleep_quality)
            
            # 插入数据
            cursor.execute("""
                INSERT INTO physiological_data (user_id, SpO2, HR, RR, SBP, DBP, altitude, temperature, sleep_quality, AMS_risk)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, max(70, SpO2), max(40, min(180, HR)), max(8, min(40, RR)), max(80, min(200, SBP)), max(50, min(130, DBP)), altitude, temperature, sleep_quality, AMS_risk))
            
            physiological_data.append({
                'user_id': user_id,
                'SpO2': max(70, SpO2),
                'HR': max(40, min(180, HR)),
                'RR': max(8, min(40, RR)),
                'SBP': max(80, min(200, SBP)),
                'DBP': max(50, min(130, DBP)),
                'altitude': altitude,
                'temperature': temperature,
                'sleep_quality': sleep_quality,
                'AMS_risk': AMS_risk
            })
        
        self.db_manager.conn.commit()
        physiological_df = pd.DataFrame(physiological_data)
        print(f"✅ 已生成 {n_samples} 条生理数据")
        return physiological_df
    
    def _calculate_risk_level(self, SpO2, HR, RR, SBP, DBP, sleep_quality):
        """计算高原反应风险等级"""
        risk_score = 0
        if SpO2 < 90: risk_score += 2
        if SpO2 < 85: risk_score += 1
        if HR > 100: risk_score += 1
        if HR > 120: risk_score += 1
        if RR > 24: risk_score += 1
        if SBP > 140 or DBP > 90: risk_score += 1
        if sleep_quality < 5: risk_score += 1
        
        return min(3, risk_score)
    
    def get_data_statistics(self):
        """获取数据统计信息"""
        cursor = self.db_manager.conn.cursor()
        
        # 总数据量
        cursor.execute("SELECT COUNT(*) as total FROM physiological_data")
        total_records = cursor.fetchone()['total']
        
        # 风险等级统计
        cursor.execute("SELECT AMS_risk, COUNT(*) as count FROM physiological_data GROUP BY AMS_risk")
        risk_stats = cursor.fetchall()
        
        # 平均生理参数
        cursor.execute("SELECT AVG(SpO2) as avg_SpO2, AVG(HR) as avg_HR, AVG(RR) as avg_RR, AVG(altitude) as avg_altitude FROM physiological_data")
        avg_stats = cursor.fetchone()
        
        print("\n📈 数据统计信息:")
        print(f"总数据量: {total_records} 条")
        print("风险等级分布:")
        risk_names = ['无风险', '轻度', '中度', '重度']
        for item in risk_stats:
            risk = item['AMS_risk']
            count = item['count']
            print(f"  {risk_names[risk]}: {count} 条 ({count/total_records*100:.1f}%)")
        
        print(f"平均生理参数:")
        print(f"  血氧饱和度: {avg_stats['avg_SpO2']:.1f}%")
        print(f"  心率: {avg_stats['avg_HR']:.1f} 次/分")
        print(f"  呼吸频率: {avg_stats['avg_RR']:.1f} 次/分")
        print(f"  海拔: {avg_stats['avg_altitude']:.0f} 米")