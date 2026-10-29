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

import pandas as pd
import joblib

class AMSPredictor:
    def __init__(self, db_manager, model_path='snow_guard_model.pkl'):
        self.db_manager = db_manager
        self.model_path = model_path
        self.model_data = None
        self.model = None
        self.scaler = None
        self.feature_names = None
    
    def load_model(self):
        """加载训练好的模型"""
        try:
            self.model_data = joblib.load(self.model_path)
            self.model = self.model_data['model']
            self.scaler = self.model_data['scaler']
            self.feature_names = self.model_data['feature_names']
            print("✅ 模型加载成功！")
            return True
        except FileNotFoundError:
            print("❌ 模型文件不存在，请先训练模型")
            return False
    
    def predict_risk(self, physiological_data):
        """预测高原反应风险"""
        if self.model is None:
            if not self.load_model():
                return None
        
        # 确保输入数据格式正确
        input_df = pd.DataFrame([physiological_data], columns=self.feature_names)
        input_scaled = self.scaler.transform(input_df)
        
        prediction = self.model.predict(input_scaled)[0]
        probabilities = self.model.predict_proba(input_scaled)[0]
        
        risk_levels = ['无风险', '轻度风险', '中度风险', '重度风险']
        
        result = {
            'risk_level': prediction,
            'risk_description': risk_levels[prediction],
            'probabilities': {
                level: f"{prob:.4f}" for level, prob in zip(risk_levels, probabilities)
            }
        }
        
        return result
    
    def add_warning_record(self, user_id, risk_level, message):
        """添加预警记录到数据库"""
        cursor = self.db_manager.conn.cursor()
        cursor.execute('''
            INSERT INTO warnings (user_id, risk_level, warning_message)
            VALUES (?, ?, ?)
        ''', (user_id, risk_level, message))
        self.db_manager.conn.commit()
        print(f"⚠️  已为用户 {user_id} 添加风险预警: {message}")
    
    def run_test_cases(self):
        """运行测试案例"""
        test_cases = [
            # 正常情况 - 低海拔
            {'SpO2': 95, 'HR': 78, 'RR': 16, 'SBP': 120, 'DBP': 80, 'altitude': 2500, 'temperature': 15, 'sleep_quality': 8},
            # 轻度风险 - 中海拔
            {'SpO2': 88, 'HR': 95, 'RR': 22, 'SBP': 135, 'DBP': 85, 'altitude': 3500, 'temperature': 8, 'sleep_quality': 6},
            # 中度风险 - 高海拔
            {'SpO2': 82, 'HR': 110, 'RR': 26, 'SBP': 150, 'DBP': 95, 'altitude': 4500, 'temperature': 2, 'sleep_quality': 4},
            # 重度风险 - 极高海拔
            {'SpO2': 75, 'HR': 130, 'RR': 32, 'SBP': 170, 'DBP': 105, 'altitude': 5000, 'temperature': -5, 'sleep_quality': 2}
        ]
        
        case_descriptions = [
            "正常情况 - 低海拔游客",
            "轻度风险 - 中海拔适应期",
            "中度风险 - 高海拔警戒",
            "重度风险 - 极高海拔紧急"
        ]
        
        print("\n" + "=" * 50)
        print("🔮 风险预测测试")
        print("=" * 50)
        
        for i, (test_data, desc) in enumerate(zip(test_cases, case_descriptions), 1):
            print(f"\n {i}: {desc} ---")
            print(f"📊 输入数据:")
            for key, value in test_data.items():
                print(f"  {key}: {value}")
            
            result = self.predict_risk(test_data)
            if result:
                print(f"🎯 预测结果: 风险等级 {result['risk_level']} - {result['risk_description']}")
                print(f"📈 各类别概率:")
                for level, prob in result['probabilities'].items():
                    print(f"  {level}: {prob}")
                
                # 如果风险等级大于0，添加预警记录
                if result['risk_level'] > 0:
                    message = f"检测到{result['risk_description']}，海拔{test_data['altitude']}米，血氧{test_data['SpO2']}%"
                    self.add_warning_record(user_id=i, risk_level=result['risk_level'], message=message)